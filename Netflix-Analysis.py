#!/usr/bin/env python
# coding: utf-8
"""
ETL Data Pipeline: Kaggle to SQL Server
Description: This script downloads the Netflix Shows dataset from Kaggle, 
             extracts it, processes it using Pandas, and loads it into 
             a Microsoft SQL Server database.
"""

import os
import zipfile
import pandas as pd
import sqlalchemy as sal

# ==========================================
# 1. DATA EXTRACTION (Kaggle API & Unzipping)
# ==========================================

print("Starting data extraction from Kaggle...")

# Download the specific dataset file using the Kaggle API
# Note: Ensure your 'kaggle.json' credentials file is placed in ~/.kaggle/
try:
    import kaggle
    kaggle.api.datasets_download_file('shivamb/netflix-shows', 'netflix_titles.csv')
    print("Dataset downloaded successfully as a zip file.")
except Exception as e:
    print(f"Error downloading dataset from Kaggle: {e}")

# Extract the CSV file from the downloaded zip archive
zip_file_path = 'netflix_titles.csv.zip'
if os.path.exists(zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall()  # Extract all contents to the current directory
    print("File extracted successfully.")
else:
    print(f"Error: {zip_file_path} not found.")

# ==========================================
# 2. DATA TRANSFORMATION & INSPECTION (Pandas)
# ==========================================

print("\nLoading and inspecting data with Pandas...")

# Load the extracted CSV file into a Pandas DataFrame
df = pd.read_csv('netflix_titles.csv')

# Inspect the dataset layout, data types, and total rows
print("\n--- DataFrame Summary ---")
df.info()

print(f"\nTotal number of records: {len(df)}")

print("\nFirst 5 rows of the dataset:")
print(df.head(5))

print("\nLast 5 rows of the dataset:")
print(df.tail(5))

# Optional data analysis: Find the maximum character length in the 'title' column
# This helps in defining the target SQL column width (e.g., VARCHAR(N))
if 'title' in df.columns:
    max_title_len = max(df['title'].dropna().str.len())
    print(f"\nMaximum character length of a title: {max_title_len}")

# ==========================================
# 3. DATA LOADING (SQL Server Database)
# ==========================================

print("\nConnecting to SQL Server...")

# Establish connection to SQL Server using SQL Server Authentication Mode
# Update the server name (MUZER\\MSSQLSERVER01) and DB name (Project_DB) as needed
connection_string = (
    "mssql+pyodbc://sa:Abc%40123@MUZER\\MSSQLSERVER01/Project_DB"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

try:
    engine = sal.create_engine(connection_string)
    conn = engine.connect()
    print("Database connection established successfully.")

    # SCENARIO A: If the table does not exist or needs to be completely reset
    # This will drop the existing table and recreate it based on DataFrame schema
    print("Loading data into 'netflix_raw' (Replace Mode)...")
    df.to_sql('netflix_raw', con=conn, index=False, if_exists='replace')
    print("Data loaded (Table created/replaced).")

    # SCENARIO B: If the table was already manually created in SQL Server
    # Uncomment the lines below if you only want to insert rows into a pre-existing table
    # print("Appending data to existing 'netflix_raw' table...")
    # df.to_sql('netflix_raw', con=conn, index=False, if_exists='append')
    # print("Data appended successfully.")

except Exception as e:
    print(f"Database operation failed: {e}")
finally:
    # Safely close the database connection
    if 'conn' in locals():
        conn.close()
        print("Database connection closed.")


