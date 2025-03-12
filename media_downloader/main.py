import os
import sys
import hashlib
import pandas as pd
import aiohttp
import asyncio
import aiofiles
import time
import psutil
import logging
from tqdm import tqdm
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table
from aiohttp import ClientSession, ClientTimeout
import re
import filecmp

console = Console()

# Setup logging
logging.basicConfig(filename="download_log.txt", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")


def get_optimal_concurrency():
    cpu_usage = psutil.cpu_percent()
    memory_available = psutil.virtual_memory().available / (1024 * 1024)
    if cpu_usage < 30 and memory_available > 2000:
        return 50
    elif cpu_usage < 60 and memory_available > 1000:
        return 30
    else:
        return 10


def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()


def extract_filename_from_url(url):
    """Extracts the original filename from a URL, preserving the extension."""
    match = re.search(r"\/([^\/?#]+)(?=[^\/]*$)", url)
    if match:
        return match.group(1)
    return None


async def download_file(url, session, folder, filename, progress_task, progress, semaphore, duplicate_hashes):
    async with semaphore:
        if not url:
            progress.update(progress_task, advance=1)
            return None
        file_path = os.path.join(folder, filename)
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    current_hash = hashlib.md5(content).hexdigest()

                    if current_hash in duplicate_hashes:
                         logging.info(f"Duplicate file found: {filename}. Skipping download.")
                         return filename, "✔ Duplicate file skipped"

                    duplicate_hashes.add(current_hash)
                    
                    async with aiofiles.open(file_path, 'wb') as f:
                        await f.write(content)
                    return filename, "✔ Success"
                else:
                    return filename, "✖ Failed - Status: " + str(response.status)
        except Exception as e:
            return filename, "✖ Failed - Error: " + str(e)
        finally:
            progress.update(progress_task, advance=1)

async def main(csv_file, max_concurrent_downloads=None):
    if not os.path.exists(csv_file):
        console.print(
            f"[bold red]🚨 Error:[/bold red] File {csv_file} not found.")
        return

    df = pd.read_csv(csv_file)
    image_columns = [
        col for col in df.columns if "displayUrl" in col or "images" in col]
    video_columns = [
        col for col in df.columns if "videoUrl" in col]

    image_count = 0
    video_count = 0
    files_to_download = []

    for idx, row in df.iterrows():
        for col in image_columns:
            url = row[col]
            if pd.notna(url) and isinstance(url, str):
                filename = extract_filename_from_url(url)
                if not filename:
                  filename = f"img_{md5_hash(url)}.jpg"
                files_to_download.append((url, None, filename))
                image_count += 1

        for col in video_columns:
            url = row[col]
            if pd.notna(url) and isinstance(url, str):
                filename = extract_filename_from_url(url)
                if not filename:
                  filename = f"vid_{md5_hash(url)}.mp4"
                files_to_download.append((url, None, filename))
                video_count += 1
                
        # Process childPosts (Reels)
        for i in range(20):  # Assuming max 20 child posts
            child_video_url_col = f"childPosts/{i}/videoUrl"
            url = row.get(child_video_url_col)
            if pd.notna(url) and isinstance(url, str):
                filename = extract_filename_from_url(url)
                if not filename:
                  filename = f"vid_reel_{md5_hash(url)}.mp4"
                files_to_download.append((url, None, filename))
                video_count += 1

    total_files = len(files_to_download)
    if total_files == 0:
        console.print(
            "[bold yellow]⚠ No files found for download.[/bold yellow]")
        return

    summary_panel = Panel(
        f"🖼 [blue]Images:[/] {image_count}\n🎥 [magenta]Videos/Reels:[/] {video_count}\n📂 [cyan]Total:[/] {total_files}",
        title="[bold green]📸 Download Summary[/bold green]",
        expand=False
    )
    console.print(summary_panel)
    input("Press Enter to start downloading... ⏬")

    # Create folders here, after pressing Enter
    base_folder = os.path.splitext(os.path.basename(csv_file))[0]
    image_folder = os.path.join(base_folder, "images")
    video_folder = os.path.join(base_folder, "videos")
    os.makedirs(image_folder, exist_ok=True)
    os.makedirs(video_folder, exist_ok=True)

    # replace None with the correct folder
    for i in range(len(files_to_download)):
        if "img_" in files_to_download[i][2] or files_to_download[i][2].endswith(('.jpg','.jpeg','.png')):
            files_to_download[i] = (
                files_to_download[i][0], image_folder, files_to_download[i][2])
        elif "vid_" in files_to_download[i][2] or "vid_reel_" in files_to_download[i][2] or files_to_download[i][2].endswith('.mp4'):
            files_to_download[i] = (
                files_to_download[i][0], video_folder, files_to_download[i][2])


    if max_concurrent_downloads is None:
        max_concurrent_downloads = get_optimal_concurrency()

    semaphore = asyncio.Semaphore(max_concurrent_downloads)
    timeout = ClientTimeout(total=600)
    async with ClientSession(timeout=timeout) as session:
        with Progress(SpinnerColumn(), BarColumn(), TimeElapsedColumn(), TimeRemainingColumn(), TextColumn("{task.completed}/{task.total} [bold blue]files downloaded[/bold blue]")) as progress:
            progress_task = progress.add_task(
                "Downloading files", total=total_files)
            duplicate_hashes = set()
            tasks = [download_file(url, session, folder, filename, progress_task,
                                   progress, semaphore,duplicate_hashes) for url, folder, filename in files_to_download]
            results = await asyncio.gather(*tasks)

    table = Table(title="Download Status", show_lines=True)
    table.add_column("File Name", justify="left", style="cyan")
    table.add_column("Status", justify="center", style="green")

    for filename, status in results:
        table.add_row(filename, status)

    console.print(table)
    console.print(
        Panel(f"📂 [bold cyan]Files saved in:[/] {base_folder}", expand=False))
    console.print("\n[bold cyan]📊 Download Complete![/bold cyan]")

def cli_entry_point():
    """Entry point for the command-line interface created by setuptools."""
    if len(sys.argv) < 2:
        console.print(
            "[bold red]🚨 Usage:[/bold red] media-downloader <csv_file> [max_concurrent_downloads]")
    else:
        csv_file = sys.argv[1]
        max_downloads = int(sys.argv[2]) if len(sys.argv) > 2 else None
        asyncio.run(main(csv_file, max_downloads))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print(
            "[bold red]🚨 Usage:[/bold red] python main.py <csv_file> [max_concurrent_downloads]")
    else:
        csv_file = sys.argv[1]
        max_downloads = int(sys.argv[2]) if len(sys.argv) > 2 else None
        asyncio.run(main(csv_file, max_downloads))