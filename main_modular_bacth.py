"""
Script simple para procesar múltiples PDFs de una carpeta.
"""

import logging
import warnings
import os
import datetime
import time
from pathlib import Path
import pandas as pd

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from src.index_builder import build_index_for_pdf
from src.modular_extract import extract_all_sections
from src.utils import save_metadata_csv, save_resources_csv, save_reserves_csv, save_economics_csv


DATA_DIR = Path("data")           # Carpeta con PDFs
OUTPUT_DIR = Path("output")       # Carpeta de salida
OUTPUT_DIR.mkdir(exist_ok=True)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
DELAY_BETWEEN_PDFS = 10 

if __name__ == "__main__":
    
    print("\n Batch Processing Started\n")
    
    # Setup
    data_path = Path(DATA_DIR)
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    
    # Find PDFs
    pdfs = sorted(data_path.glob("*.pdf"))
    
    if not pdfs:
        print(f"No PDFs found in '{DATA_DIR}/' folder")
        exit(1)
    
    print(f"Found {len(pdfs)} PDF(s)\n")
    
    # Process each
    success = 0
    failed = 0
    
    for i, pdf in enumerate(pdfs, 1):
        print(f"[{i}/{len(pdfs)}] {pdf.name}")
        
        try:
            # Get IDs
            file_id = pdf.stem[-8:]
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Build index
            print("  Building index...")
            index = build_index_for_pdf(str(pdf), chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            
            # Extract (one section at a time)
            print("  Extracting metadata...")
            metadata = extract_all_sections(index, only="metadata")["metadata"]
            
            print("  Extracting resources...")
            resources = extract_all_sections(index, only="resources")["resources"]
            
            print("  Extracting reserves...")
            reserves = extract_all_sections(index, only="reserves")["reserves"]
            
            print("  Extracting economics...")
            economics = extract_all_sections(index, only="economics")["economics"]
            
            # Save
            print("  Saving CSVs...")
            save_metadata_csv(metadata, output_path / "metadata.csv", timestamp, file_id)
            save_resources_csv(resources, output_path / "resources.csv", timestamp, file_id)
            save_reserves_csv(reserves, output_path / "reserves.csv", timestamp, file_id)
            save_economics_csv(economics, output_path / "economics.csv", timestamp, file_id)
            
            print(f"  ✓ Done - {metadata.project_name or 'Unknown'}\n")
            success += 1
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:60]}...\n")
            failed += 1
        
        # Wait before next (except last)
        if i < len(pdfs):
            print(f"Waiting {DELAY_BETWEEN_PDFS }s...\n")
            time.sleep(DELAY_BETWEEN_PDFS)
    
    # Summary
    print("="*60)
    print(f"Done! {success} successful, {failed} failed")
    print(f"Output: {output_path.absolute()}")
    print("="*60)