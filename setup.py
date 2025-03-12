import setuptools

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="media-downloader",
    vesion="0.1.0",
    author="Kissada Waravit",
    author_email = "Kissada.Waravit@gmail.com",
    description="A tool for batch downloading media files from URLs in a CSV file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="media, download, csv, batch, url",
    project_urls={
        "Bug Reports": "https://github.com/Kissada-W/Media-Downloader/issues",
        "Source": "https://github.com/Kissada-W/Media-Downloader",
    },
    packages=setuptools.find_packages(),
    classifies=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Internet :: File Transfer Protocol (FTP)",
        "Natural Language :: English",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "media-downloader=media_downloader.main:cli_entry_point",
        ],
    },
)
