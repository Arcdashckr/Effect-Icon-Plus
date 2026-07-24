import os
import zipfile
import glob
from PIL import Image
from common import *

os.makedirs(EXTRACTED_DIR, exist_ok=True)

def scale_image(source_path, dest_path, size=(36, 36)):
    """Upscales the image to 36x36 without losing pixel detail (Nearest Neighbor)."""
    try:
        with Image.open(source_path) as img:
            # Nearest neighbor filter is required for sharp pixel art upscaling
            scaled_img = img.resize(size, Image.Resampling.NEAREST)
            scaled_img.save(dest_path)
        return True
    except Exception as e:
        print(f"[-] Image scaling error ({os.path.basename(source_path)}): {e}")
        return False

def extract_icons_from_jar(jar_path):
    """Extracts effect icons from the JAR file (excluding programmer_art)."""
    mod_name = os.path.splitext(os.path.basename(jar_path))[0]

    print(f"\n==================================================")
    print(f"[~] Processing: {mod_name}")
    print(f"==================================================")

    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            extracted_count = 0

            for file_info in jar.infolist():
                filename = file_info.filename

                if "programmer_art" in filename.lower():
                    continue

                if "assets/" in filename and "textures/mob_effect/" in filename and filename.endswith(".png"):

                    parts = filename.split("/")
                    try:
                        assets_index = parts.index("assets")
                        mod_id = parts[assets_index + 1]
                        icon_name = parts[-1]
                    except (ValueError, IndexError):
                        continue

                    mod_output_dir = os.path.join(EXTRACTED_DIR, mod_id)
                    os.makedirs(mod_output_dir, exist_ok=True)

                    temp_source = jar.extract(file_info, TOOLS_DIR)
                    dest_path = os.path.join(mod_output_dir, icon_name)

                    # Scale and save as 36x36
                    if scale_image(temp_source, dest_path):
                        print(f"  [>] Extracted: [{mod_id}] -> {icon_name}")
                        extracted_count += 1

                    if os.path.exists(temp_source):
                        os.remove(temp_source)
                        try:
                            os.removedirs(os.path.dirname(temp_source))
                        except OSError:
                            pass

            if extracted_count > 0:
                print("--------------------------------------------------")
                print(f"[+] SUCCESS: Extracted a total of {extracted_count} icons.")
            else:
                print(f"[!] Skipped: No matching effect icons found in this mod.")

    except Exception as e:
        print(f"[-] Error reading JAR file ({os.path.basename(jar_path)}): {e}")

def main():
    print("\n==================================================")
    print(" EFFECT ICON EXTRACTION MODULE FOR MODS")
    print("==================================================")

    if not os.path.exists(MODS_DIR) or not os.listdir(MODS_DIR):
        print("[-] 'tools/mods/' directory is empty or does not exist. Please download a mod first.")
        return

    jar_files = glob.glob(os.path.join(MODS_DIR, "*.jar")) + glob.glob(os.path.join(MODS_DIR, "*.zip"))

    print(f"[*] Found {len(jar_files)} archive file(s). Starting extraction...")

    for jar in jar_files:
        extract_icons_from_jar(jar)

    print("\n==================================================")
    print("[+] Extraction completed! Output is in 'tools/extracted/' folder.")
    print("==================================================")

if __name__ == "__main__":
    main()