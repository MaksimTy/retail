#!/usr/bin/env python3
"""
Script to build the data warehouse.
"""

from retail.data.warehouse.loader import load_data

if __name__ == "__main__":
    load_data()
    print("Data warehouse built successfully!")