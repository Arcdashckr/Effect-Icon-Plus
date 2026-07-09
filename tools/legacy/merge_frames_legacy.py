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
    """Bir HEX renginin parlaklık (luminance) değerini hesaplar"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b

def extract_palette_from_image(image_path, color_count=9):
    """ImageMagick kullanarak resimdeki transparan olmayan tüm baskın renkleri çıkarır"""
    try:
        cmd = [
            "magick", image_path,
            "-alpha", "Background",
            "+dither",
            "-colors", "32", # Tüm renkleri görebilmek için analizi biraz genişletiyoruz
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
            
        # Tüm renkleri parlaklığına göre sırala
        colors.sort(key=get_color_brightness, reverse=True)
        return colors
    except Exception as e:
        print(f"❌ Renk paleti çıkarılamadı ({os.path.basename(image_path)}): {e}")
        return ["#FFFFFFFF"]

def load_or_create_json():
    """colors.json dosyasını yükler, ana yapıyı kontrol eder"""
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
    """colors.json dosyasını kaydeder"""
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def colorize_and_merge():
    if not os.path.exists(EXTRACTED_DIR):
        print("❌ extracted klasörü bulunamadı! Önce 1. adımı çalıştırın.")
        return

    print("\n--------------------------------------------------")
    print("🤖 RENK SIRALAMA MODU SEÇİNİZ")
    print("--------------------------------------------------")
    print("[1] Otomatik Sıralama Kullan (JSON'daki 'auto' bloğunu basar)")
    print("[2] Manuel Sıralama Kullan (JSON'daki 'manual' bloğundaki 9'lu listeyi basar)")
    print("--------------------------------------------------")
    secim = input("Seçiminiz (1 veya 2): ").strip()
    
    mode_key = "auto" if secim != "2" else "manual"
    print(f"ℹ️  colors.json içerisindeki '{mode_key}' bloğu temel alınarak üretilecek.\n")

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

            # Resimdeki TÜM benzersiz renkleri çıkar
            all_extracted_colors = extract_palette_from_image(icon_path)
            
            # Çerçeve için 9'a tamamlanmış halini üret
            nine_colors = list(all_extracted_colors)
            while len(nine_colors) < 9:
                nine_colors.append(nine_colors[-1] if nine_colors else "#FFFFFFFF")
            nine_colors = nine_colors[:9]

            # JSON Güncelleme Mantığı
            # Auto bloğuna ekle (Sadece 9 renk)
            if effect_name not in json_data["auto"][mod_id]:
                json_data["auto"][mod_id][effect_name] = nine_colors
                json_updated = True

            # Manual bloğuna normal 9'lu listeyi ekle
            if effect_name not in json_data["manual"][mod_id]:
                json_data["manual"][mod_id][effect_name] = list(nine_colors)
                json_updated = True

            # Manual bloğuna _all referans listesini ekle (Resimdeki tüm ham renkler)
            all_key = f"{effect_name}_all"
            if all_key not in json_data["manual"][mod_id]:
                json_data["manual"][mod_id][all_key] = all_extracted_colors
                json_updated = True

            # Boyama için renkleri seç (Eğer manual moddaysak kesinlikle _all anahtarını DEĞİL, normal anahtarı kullan)
            colors = json_data[mode_key][mod_id][effect_name]
            
            while len(colors) < 9:
                colors.append(colors[-1] if colors else "#FFFFFFFF")
            colors = colors[:9]

            # Hedef çıktı klasörü
            output_dir = os.path.join(REPO_DIR, "assets", mod_id, "textures", "mob_effect")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, icon_file)

            print(f"⚡ İşleniyor [{mode_key}]: {mod_id} -> {effect_name}")

            # ImageMagick birleştirme zinciri
            magick_cmd = ["magick", "-size", "54x54", "canvas:transparent"]
            
            for i in range(1, 10):
                frame_img = os.path.join(FRAMES_DIR, f"{i}.png")
                if not os.path.exists(frame_img):
                    print(f"❌ Kritik Hata: {i}.png çerçeve dilimi bulunamadı!")
                    return
                
                color = colors[i-1]
                magick_cmd += [
                    "(", frame_img, 
                    "-alpha", "On", 
                    "-fill", color, 
                    "-opaque", "white", 
                    ")", 
                    "-composite"
                ]
            
            magick_cmd += [
                "(", icon_path, 
                "-background", "none", 
                "-gravity", "center", 
                "-extent", "54x54", 
                ")",
                "-composite",
                output_path
            ]

            try:
                subprocess.run(magick_cmd, check=True)
            except Exception as e:
                print(f"❌ ImageMagick Hatası ({effect_name}): {e}")

    if json_updated:
        save_json(json_data)
        print("📝 JSON dosyası güncellendi! '_all' referans renkleri 'manual' bloğuna eklendi.")

    print("\n✅ İşlem tamamlandı! İkonlar başarıyla oluşturuldu.")

if __name__ == "__main__":
    colorize_and_merge()