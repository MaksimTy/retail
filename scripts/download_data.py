#!/usr/bin/env python3
"""
Script to download the UCI Online Retail dataset.
"""

from retail.data.source.uci_downloader import download_online_retail

if __name__ == "__main__":
    download_online_retail()
    print("Data downloaded successfully!")