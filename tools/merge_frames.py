import os
import json
import subprocess
import re

# Klasör yolları
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(TOOLS_DIR)
EXTRACTED_DIR = os.path.join(TOOLS_DIR, "extracted")
FRAMES_DIR = os.path.join(TOOLS_DIR, "frames")
JSON_PATH = os.path.join(TOOLS_DIR, "colors.json")

def get_color_brightness(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b

def adjust_contrast(colors, factor=1):
    """Renklerin arasındaki kontrastı artırır, böylece geçişler daha keskin olur"""
    if len(colors) < 2:
        return colors
        
    adjusted = []
    # Renkleri parlaklıklarına göre sıraladıktan sonra aralığı esnetiyoruz
    for color in colors:
        hex_str = color.lstrip('#')[:6]
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        
        # 128 (orta nokta) merkezli kontrast artırma
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
        
        # Çerçeve dilimleri için kontrastı keskinleştir
        colors = adjust_contrast(colors, factor=1.25)
        
        return colors
    except Exception as e:
        print(f"[-] Renk paleti çıkarılamadı ({os.path.basename(image_path)}): {e}")
        return ["#FFFFFFFF"]

def load_or_create_json():
    default_structure = {"auto": {}, "manual": {}}
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "auto" not in data or "manual" not in data:
                    return default_structure
                return data
        except Exception:
            return default_structure
    return default_structure

def save_json(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def colorize_and_merge():
    if not os.path.exists(EXTRACTED_DIR):
        print("[-] extracted klasörü bulunamadı! Önce 1. adımı çalıştırın.")
        return

    print("\n--------------------------------------------------")
    print(" RENK SIRALAMA MODU SEÇİNİZ")
    print("--------------------------------------------------")
    print("[1] Otomatik Sıralama Kullan (JSON'daki 'auto' bloğunu basar)")
    print("[2] Manuel Sıralama Kullan (JSON'daki 'manual' bloğunu basar)")
    print("--------------------------------------------------")
    secim = input("Seçiminiz (1 veya 2): ").strip()
    
    mode_key = "auto" if secim != "2" else "manual"
    
    print("\nHız modu kontrol edilsin mi?")
    skip_existing = input("Sadece yeni ve değişen ikonlar mı işlensin? (E/H): ").strip().lower() != 'h'

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
            
            # Çıktı yolları kontrolü (Minecraft -> minecraft eşleşmesi korundu)
            folder_target = "minecraft" if mod_id == "vanilla" or mod_id == "minecraft" else mod_id
            output_dir = os.path.join(REPO_DIR, "assets", folder_target, "textures", "mob_effect")
            output_path = os.path.join(output_dir, icon_file)

            # AKILLI HIZ FİLTRESİ:
            # Eğer dosya zaten varsa ve json'da kayıtlıysa, kullanıcı da 'Hız Modu' istemişse atla
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
            print(f"⚡ İşleniyor [{mode_key}]: {mod_id} -> {effect_name}")

            magick_cmd = ["magick", "-size", "54x54", "canvas:transparent"]
            for i in range(1, 10):
                frame_img = os.path.join(FRAMES_DIR, f"{i}.png")
                if not os.path.exists(frame_img):
                    print(f"[-] Kritik Hata: {i}.png çerçeve dilimi bulunamadı!")
                    return
                magick_cmd += ["(", frame_img, "-alpha", "On", "-fill", colors[i-1], "-opaque", "white", ")", "-composite"]
            
            magick_cmd += ["(", icon_path, "-background", "none", "-gravity", "center", "-extent", "54x54", ")", "-composite", output_path]

            try:
                subprocess.run(magick_cmd, check=True)
            except Exception as e:
                print(f"[-] ImageMagick Hatası ({effect_name}): {e}")

    if json_updated:
        save_json(json_data)
        print("[>] JSON dosyası yeni verilerle güncellendi.")

    print("\n[+] BAŞARILI: İşlem tamamlandı! İkonlar başarıyla oluşturuldu.")

if __name__ == "__main__":
    colorize_and_merge()