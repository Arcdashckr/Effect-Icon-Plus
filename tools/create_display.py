import os
import subprocess
import glob
from common import *

os.makedirs(DISPLAY_DIR, exist_ok=True)

# Checkerboard background colors and tile size (in pixels per square)
CHECKER_COLOR_A = "#26292F"
CHECKER_COLOR_B = "#2D3138"
CHECKER_TILE_PX = 12


def add_checkerboard_background(source_image, output_image):
    """
    Composites source_image onto a checkerboard background and saves to output_image.
    The checkerboard uses CHECKER_COLOR_A and CHECKER_COLOR_B with CHECKER_TILE_PX-px squares.
    The background canvas is sized to match the source image exactly.
    """
    try:
        # Retrieve source image dimensions
        identify_cmd = [
            "magick", "identify",
            "-format", "%wx%h",
            source_image
        ]
        result = subprocess.run(identify_cmd, check=True, capture_output=True, text=True)
        dimensions = result.stdout.strip()
        width, height = map(int, dimensions.split("x"))

        tile_size = CHECKER_TILE_PX * 2  # full checkerboard repeat unit
        composite_cmd = [
            "magick",
            # Build a (tile_size x tile_size) checkerboard tile in memory:
            # Fill the entire tile with COLOR_A, then paint COLOR_B into the
            # top-right and bottom-left quadrants.
            "-size", f"{tile_size}x{tile_size}",
            f"xc:{CHECKER_COLOR_A}",
            "-fill", CHECKER_COLOR_B,
            "-draw", f"rectangle {CHECKER_TILE_PX},0 {tile_size - 1},{CHECKER_TILE_PX - 1}",
            "-draw", f"rectangle 0,{CHECKER_TILE_PX} {CHECKER_TILE_PX - 1},{tile_size - 1}",
            # Store tile in ImageMagick's named-image register
            "-write", "mpr:checker_tile",
            "+delete",
            # Tile it across the full canvas matching the source dimensions
            "-size", f"{width}x{height}",
            "tile:mpr:checker_tile",
            # Composite the icon grid (with alpha) over the checkerboard
            source_image,
            "-composite",
            output_image
        ]
        subprocess.run(composite_cmd, check=True)
        print(f"[+] SUCCESS: Background version created: {output_image}")
    except Exception as e:
        print(f"[-] Error creating background version for '{source_image}': {e}")


def generate_grid(mod_ids, output_name_suffix, single=False):
    if isinstance(mod_ids, str):
        mod_ids = [mod_ids]

    all_icons = []
    for mod_id in mod_ids:
        folder_name = mod_id
        effect_dir = os.path.join(ASSETS_DIR, folder_name, "textures", "mob_effect")
        if os.path.exists(effect_dir):
            all_icons.extend(glob.glob(os.path.join(effect_dir, "*.png")))

    if not all_icons:
        print("[-] No icons (.png) found in the specified folders.")
        return

    base_output          = os.path.join(DISPLAY_DIR, f"effect_display_{output_name_suffix}.png")
    base_bg_output       = os.path.join(DISPLAY_DIR, f"effect_display_{output_name_suffix}_background.png")
    upscaled_output      = os.path.join(DISPLAY_DIR, f"effect_display_{output_name_suffix}_upscaled.png")
    upscaled_bg_output   = os.path.join(DISPLAY_DIR, f"effect_display_{output_name_suffix}_upscaled_background.png")

    if single:
        tile_count = f"{min(len(all_icons), 10)}x"
    else:
        tile_count = "10x"

    list_file_path = os.path.join(DISPLAY_DIR, f"temp_{output_name_suffix}_list.txt")

    try:
        # Write icon paths to a temporary file to bypass the Windows
        # command line length limit (WinError 206).
        with open(list_file_path, "w", encoding="utf-8") as f:
            for icon in all_icons:
                f.write(icon + "\n")

        # --- Standard grid (transparent background) ---
        montage_cmd = [
            "magick", "montage",
            f"@{list_file_path}",
            "-background", "none",
            "-geometry", "54x54+5+5",
            "-tile", tile_count,
            base_output
        ]
        subprocess.run(montage_cmd, check=True)
        print(f"[+] SUCCESS: Standard grid created: {base_output}")

        # --- Standard grid with checkerboard background ---
        add_checkerboard_background(base_output, base_bg_output)

        # --- Upscaled grid (transparent background) ---
        scale_cmd = [
            "magick", base_output,
            "-scale", "300%",
            upscaled_output
        ]
        subprocess.run(scale_cmd, check=True)
        print(f"[+] SUCCESS: Sharp upscaled grid created: {upscaled_output}")

        # --- Upscaled grid with checkerboard background ---
        add_checkerboard_background(upscaled_output, upscaled_bg_output)

    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        if os.path.exists(list_file_path):
            try:
                os.remove(list_file_path)
            except:
                pass


def main():
    print("\n--------------------------------------------------")
    print(" PREVIEW GRID (DISPLAY) CREATOR")
    print("--------------------------------------------------")
    print("[1] Generate for Vanilla Only (Minecraft Folder)")
    print("[2] Generate for a Specific Mod")
    print("[3] Generate Separate Images for Each Mod")
    print("[4] COMBINE ALL INTO A SINGLE IMAGE (Permalink Friendly) 🔥")
    print("--------------------------------------------------")
    choice = input("Your choice (1-4): ").strip()

    if not os.path.exists(ASSETS_DIR):
        print("[-] 'assets' folder not found!")
        return

    all_folders = [f for f in os.listdir(ASSETS_DIR) if os.path.isdir(os.path.join(ASSETS_DIR, f))]

    if choice == "1":
        generate_grid("minecraft", "vanilla")
    elif choice == "2":
        mod_name = input("Please enter the mod folder name: ").strip()
        if mod_name:
            generate_grid(mod_name, mod_name, single=True)
    elif choice == "3":
        for folder in all_folders:
            suffix = "vanilla" if folder == "minecraft" else folder
            generate_grid(folder, suffix, single=True)
    elif choice == "4":
        print("\nShould Vanilla (Minecraft) effects also be included in this combined image?")
        vanilla_choice = input("Include? (Y/N): ").strip().lower()

        target_mods = []
        for folder in all_folders:
            if folder == "minecraft":
                if vanilla_choice == "y":
                    target_mods.append("minecraft")
                continue
            target_mods.append(folder)

        generate_grid(target_mods, "mod")
    else:
        print("[-] Invalid choice.")


if __name__ == "__main__":
    main()