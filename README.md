# Media Downloader

A powerful and efficient tool for batch downloading media files (images and videos) from URLs listed in a CSV file.

## 📋 Overview

This utility helps you download multiple media files referenced in a CSV dataset. It's particularly useful for downloading content from social media exports or any CSV containing image and video URLs. The tool intelligently identifies images and videos, organizes them into separate folders, detects duplicates, and provides detailed progress information with a beautiful interface.

## ✨ Features

- **Asynchronous Downloads**: Process multiple files simultaneously for maximum efficiency
- **Smart Resource Management**: Automatically adjusts concurrency based on system resources
- **Duplicate Detection**: Avoids downloading the same file twice using MD5 hash verification
- **Elegant Progress Display**: Real-time download progress with rich visual interface
- **Comprehensive Logging**: Detailed logs for troubleshooting
- **File Organization**: Automatically sorts downloads into images and videos folders
- **Original Filename Preservation**: Maintains original filenames from URLs where possible

## 🔧 Requirements

The following Python packages are required:

```
pandas
aiohttp
aiofiles
psutil
tqdm
rich
```

## 📥 Installation

### Option 1: Install from source

1. Clone or download this repository:
```bash
git clone https://github.com/yourusername/media-downloader.git
cd media-downloader
```

2. Install the package and dependencies:
```bash
pip install -e .
```

### Option 2: Install required dependencies manually

```bash
pip install pandas aiohttp aiofiles psutil tqdm rich
```

## 🚀 Usage

Run the script from the command line, providing a CSV file containing URLs:

```bash
python main.py <csv_file> [max_concurrent_downloads]
```

### Parameters:

- `<csv_file>`: Path to the CSV file containing the media URLs (required)
- `[max_concurrent_downloads]`: Optional parameter to set the maximum number of concurrent downloads. If not provided, the script automatically determines the optimal value based on your system resources.

### Example:

```bash
python main.py social_media_export.csv 20
```

## 📊 How It Works

1. The script scans your CSV for columns containing image or video URLs (identified by column names containing "displayUrl", "images", or "videoUrl")
2. It also checks for video content in child posts (commonly used for Reels or carousel posts)
3. Displays a summary of found media files and waits for your confirmation
4. Creates organized folders for images and videos based on your CSV filename
5. Downloads all files with an optimized number of concurrent connections
6. Shows real-time progress with a sleek progress bar
7. Provides a detailed status report upon completion

## 📁 Output Organization

Files are organized in the following structure:

```
[csv_name]/
├── images/
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
└── videos/
    ├── video1.mp4
    ├── reel_video2.mp4
    └── ...
```

## 📝 Logging

The script creates a log file named `download_log.txt` with detailed information about the download process, which can be helpful for troubleshooting.

## 🧠 Smart Concurrency

The script automatically determines the optimal number of concurrent downloads based on:
- CPU usage
- Available memory
- Network conditions

However, you can override this by specifying a maximum number of concurrent downloads as the second parameter.

## 💡 Tips

- For large datasets, let the script determine the optimal concurrency
- Check the download_log.txt file if you encounter any issues
- The script works best with CSV files that have explicit URL columns from social media exports

## ⚠️ Limitations

- The script assumes URLs are in columns containing specific keywords ("displayUrl", "images", "videoUrl", "videos")
- Maximum of 20 child posts per row are checked (for carousel/multi-image posts)
- Some websites may block or throttle multiple concurrent requests

## 📄 License

This project is available for open use. Please ensure you have the right to download and use any media files processed by this script.

## 🙏 Acknowledgements

This tool leverages several excellent Python packages including pandas, aiohttp, rich, and others that make this functionality possible.