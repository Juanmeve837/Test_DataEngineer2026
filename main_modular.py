import logging
import warnings
import os
import datetime
from pathlib import Path
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)
os.environ["ANONYMIZED_TELEMETRY"] = "False"


from src.index_builder import build_index_for_pdf
from src.modular_extract import extract_all_sections
from src.utils import save_metadata_csv, save_resources_csv, save_reserves_csv, save_economics_csv

PDF_PATH = r"data\sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Index configuration (optimized for GitHub Models)
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

def main():

    file_id = Path(PDF_PATH).stem[-8:] 
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  

    try:
        index = build_index_for_pdf(
            PDF_PATH,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
    except Exception as e:
        print(f"❌ ERROR building index: {e}")
        return 1
    
    try:
        print("\n📋 [1/4] Extracting METADATA")
        metadata = extract_all_sections(index, only="metadata")["metadata"]

        print("\n⛏️ [2/4] Extracting RESOURCES")
        resources = extract_all_sections(index, only="resources")["resources"]

        print("\n🧱 [3/4] Extracting RESERVES")
        reserves = extract_all_sections(index, only="reserves")["reserves"]

        print("\n💰 [4/4] Extracting ECONOMICS")
        economics = extract_all_sections(index, only="economics")["economics"]

    except Exception as e:
        print(f"\n❌ ERROR during extraction: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    try:
        # 1. Metadata CSV
        save_metadata_csv(metadata, OUTPUT_DIR / "metadata.csv",timestamp, file_id)

        # 2. Resources CSV
        save_resources_csv(resources, OUTPUT_DIR / "resources.csv",timestamp, file_id)

        # 3. Reserves CSV
        save_reserves_csv(reserves, OUTPUT_DIR / "reserves.csv",timestamp, file_id)

        # 4. Economics CSV
        save_economics_csv(economics, OUTPUT_DIR / "economics.csv",timestamp, file_id)
        
    except Exception as e:
        print(f"\n❌ ERROR saving CSVs: {e}")
        return 1
    
if __name__ == "__main__":
    main()