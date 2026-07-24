import os
import shutil
from common import MODS_DIR, EXTRACTED_DIR

def clean_directory(directory):
    if not os.path.exists(directory):
        print(f"[>] Directory does not exist, skipping: {os.path.basename(directory)}")
        return
    deleted_files = 0
    deleted_dirs = 0
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if item == ".gitignore":
            continue
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                deleted_dirs += 1
            else:
                os.remove(item_path)
                deleted_files += 1
        except Exception as e:
            print(f"[-] Error ({item}): {e}")
    print(f"[+] Cleaned {os.path.basename(directory)}: deleted {deleted_dirs} directories, {deleted_files} files.")

def main():
    print("[~] Cleaning temporary files...")
    clean_directory(MODS_DIR)
    clean_directory(EXTRACTED_DIR)
    print("[+] Cleanup complete!")

if __name__ == "__main__":
    main()
