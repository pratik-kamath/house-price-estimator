
import os
import zipfile
import shutil
import glob

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))

def extract_nested_zip(zip_path, extract_to):
    """
    Extracts a zip file. If it contains other zip files (weekly data),
    extracts those as well into the target directory.
    """
    try:
        # Create a temp dir for the outer zip
        temp_extract_dir = os.path.join(extract_to, '_temp_' + os.path.basename(zip_path))
        os.makedirs(temp_extract_dir, exist_ok=True)
        
        print(f"Extracting outer zip: {zip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)

        # Iterate through extracted files
        for root, dirs, files in os.walk(temp_extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                if file.lower().endswith('.zip'):
                    # It's a weekly zip, extract it to the main data dir
                    print(f"  -> Extracting weekly zip: {file}")
                    try:
                        with zipfile.ZipFile(file_path, 'r') as inner_zip:
                            inner_zip.extractall(extract_to)
                    except zipfile.BadZipFile:
                        print(f"  [ERROR] Bad zip file: {file}")
                
                elif file.lower().endswith('.dat'):
                    # It's already a DAT file, move it
                    print(f"  -> Moving DAT file: {file}")
                    shutil.move(file_path, os.path.join(extract_to, file))

        # Cleanup temp dir
        shutil.rmtree(temp_extract_dir)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to process {zip_path}: {e}")
        return False

def flatten_directory(source_dir, target_dir):
    """
    Moves all .dat files from source_dir (and subdirs) to target_dir.
    Unzips any .zip files found along the way.
    """
    for root, dirs, files in os.walk(source_dir, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            
            if file.lower().endswith('.zip'):
                print(f"  -> Extracting zip in dir: {file}")
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(target_dir)
                    os.remove(file_path) # Remove zip after extraction
                except zipfile.BadZipFile:
                     print(f"  [ERROR] Bad zip file: {file}")

            elif file.lower().endswith('.dat'):
                # Move DAT file to target if it's not already there
                target_path = os.path.join(target_dir, file)
                if file_path != target_path:
                    print(f"  -> Moving DAT file: {file}")
                    shutil.move(file_path, target_path)

        # Remove empty directories
        if root != source_dir and root != target_dir:
            try:
                os.rmdir(root)
                print(f"Removed empty dir: {root}")
            except OSError:
                pass # Directory not empty

def main():
    print(f"Starting data extraction in: {DATA_DIR}")
    
    # 1. Process Year Zips (e.g., 2016.zip)
    year_zips = glob.glob(os.path.join(DATA_DIR, '*.zip'))
    for zip_path in year_zips:
        if extract_nested_zip(zip_path, DATA_DIR):
            print(f"Removing processed zip: {zip_path}")
            os.remove(zip_path)

    # 2. Process Year Directories (e.g., 2024/)
    # We treat subdirectories as sources to flatten
    items = os.listdir(DATA_DIR)
    for item in items:
        item_path = os.path.join(DATA_DIR, item)
        if os.path.isdir(item_path):
            print(f"Processing directory: {item}")
            flatten_directory(item_path, DATA_DIR)
            # Try to remove the year dir itself if empty
            try:
                os.rmdir(item_path)
                print(f"Removed processed directory: {item_path}")
            except OSError:
                 print(f"Directory not empty, skipping removal: {item_path}")

    print("Extraction complete.")
    
    # Verification
    dat_count = len(glob.glob(os.path.join(DATA_DIR, '*.DAT')))
    print(f"Total .DAT files in {DATA_DIR}: {dat_count}")

if __name__ == "__main__":
    main()
