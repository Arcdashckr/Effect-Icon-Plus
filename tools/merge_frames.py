import os
import json
import subprocess
import re
from common import ROOT_DIR, EXTRACTED_DIR, FRAMES_DIR, COLORS_PATH

def get_color_brightness(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b

def adjust_contrast(colors, factor=1):
    """Increases the contrast between colors so that transitions are sharper"""
    if len(colors) < 2:
        return colors

    adjusted = []
    # Stretch range after sorting colors by brightness
    for color in colors:
        hex_str = color.lstrip('#')[:6]
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)

        # Contrast enhancement centered around 128
        r = max(0, min(255, int(128 + (r - 128) * factor)))
        g = max(0, min(255, int(128 + (g - 128) * factor)))
        b = max(0, min(255, int(128 + (b - 128) * factor)))

        adjusted.append(f"#{r:02X}{g:02X}{b:02X}FF")
    return adjusted

def extract_palette_from_image(image_path, color_count=9):
    try:
        cmd = [
            "magick", image_path,
            "-alpha", "Background",
            "+dither",
            "-colors", "32",
            "-define", "histogram:unique-colors=true",
            "-format", "%c",
            "histogram:info:"
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        hex_colors = re.findall(r'#TextColor\s+([0-9A-Fa-f]{6,8})|#([0-9A-Fa-f]{6,8})', result.stdout)
        colors = []
        for match in hex_colors:
            color = match[0] if match[0] else match[1]
            if color:
                hex_str = f"#{color[:6].upper()}FF"
                if hex_str != "#000000FF" and hex_str not in colors:
                    colors.append(hex_str)

        if not colors:
            colors = ["#FFFFFFFF"]

        colors.sort(key=get_color_brightness, reverse=True)

        # Sharpen contrast for frame slices
        colors = adjust_contrast(colors, factor=1.25)

        return colors
    except Exception as e:
        print(f"[-] Failed to extract color palette ({os.path.basename(image_path)}): {e}")
        return ["#FFFFFFFF"]

def load_or_create_json():
    default_structure = {"auto": {}, "manual": {}}
    if os.path.exists(COLORS_PATH):
        try:
            with open(COLORS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "auto" not in data or "manual" not in data:
                    return default_structure
                return data
        except Exception:
            return default_structure
    return default_structure

def save_json(data):
    with open(COLORS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def colorize_and_merge():
    if not os.path.exists(EXTRACTED_DIR):
        print("[-] 'extracted' directory not found! Please run step [2] (Icon Extractor) first.")
        return

    print("\n--------------------------------------------------")
    print(" SELECT COLOR ORDER MODE")
    print("--------------------------------------------------")
    print("[1] Use Auto Sorting (based on the 'auto' block in JSON)")
    print("[2] Use Manual Sorting (based on the 'manual' block in JSON)")
    print("--------------------------------------------------")
    secim = input("Your choice (1 or 2): ").strip()

    mode_key = "auto" if secim != "2" else "manual"

    print("\nEnable fast mode?")
    skip_existing = input("Only process new and modified icons? (Y/N): ").strip().lower() != 'n'

    json_data = load_or_create_json()
    json_updated = False

    mod_folders = [f for f in os.listdir(EXTRACTED_DIR) if os.path.isdir(os.path.join(EXTRACTED_DIR, f))]

    for mod_id in mod_folders:
        mod_extracted_dir = os.path.join(EXTRACTED_DIR, mod_id)
        effect_icons = [f for f in os.listdir(mod_extracted_dir) if f.endswith(".png")]

        if mod_id not in json_data["auto"]:
            json_data["auto"][mod_id] = {}
        if mod_id not in json_data["manual"]:
            json_data["manual"][mod_id] = {}

        for icon_file in effect_icons:
            icon_path = os.path.join(mod_extracted_dir, icon_file)
            effect_name = os.path.splitext(icon_file)[0]

            # Output path checks (preserving minecraft mapping)
            folder_target = "minecraft" if mod_id == "vanilla" or mod_id == "minecraft" else mod_id
            output_dir = os.path.join(ROOT_DIR, "assets", folder_target, "textures", "mob_effect")
            output_path = os.path.join(output_dir, icon_file)

            # SMART FAST FILTER:
            is_already_in_json = effect_name in json_data["auto"][mod_id] and effect_name in json_data["manual"][mod_id]
            if skip_existing and os.path.exists(output_path) and is_already_in_json:
                continue

            all_extracted_colors = extract_palette_from_image(icon_path)

            nine_colors = list(all_extracted_colors)
            while len(nine_colors) < 9:
                nine_colors.append(nine_colors[-1] if nine_colors else "#FFFFFFFF")
            nine_colors = nine_colors[:9]

            if effect_name not in json_data["auto"][mod_id]:
                json_data["auto"][mod_id][effect_name] = nine_colors
                json_updated = True

            if effect_name not in json_data["manual"][mod_id]:
                json_data["manual"][mod_id][effect_name] = list(nine_colors)
                json_updated = True

            all_key = f"{effect_name}_all"
            if all_key not in json_data["manual"][mod_id]:
                json_data["manual"][mod_id][all_key] = all_extracted_colors
                json_updated = True

            colors = json_data[mode_key][mod_id][effect_name]
            while len(colors) < 9:
                colors.append(colors[-1] if colors else "#FFFFFFFF")
            colors = colors[:9]

            os.makedirs(output_dir, exist_ok=True)
            print(f"[~] Processing [{mode_key}]: {mod_id} -> {effect_name}")

            magick_cmd = ["magick", "-size", "54x54", "canvas:transparent"]
            for i in range(1, 10):
                frame_img = os.path.join(FRAMES_DIR, f"{i}.png")
                if not os.path.exists(frame_img):
                    print(f"[-] Critical Error: Frame slice {i}.png not found!")
                    return
                magick_cmd += ["(", frame_img, "-alpha", "On", "-fill", colors[i-1], "-opaque", "white", ")", "-composite"]

            magick_cmd += ["(", icon_path, "-background", "none", "-gravity", "center", "-extent", "54x54", ")", "-composite", output_path]

            try:
                subprocess.run(magick_cmd, check=True)
            except Exception as e:
                print(f"[-] ImageMagick Error ({effect_name}): {e}")

    if json_updated:
        save_json(json_data)
        print("[>] JSON file updated with new data.")

    print("\n[+] SUCCESS: Operation completed! Icons successfully generated.")

if __name__ == "__main__":
    colorize_and_merge()