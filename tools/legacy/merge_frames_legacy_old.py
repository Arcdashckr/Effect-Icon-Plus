import os
import json
import subprocess

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(TOOLS_DIR)  # Bir üst klasör (Repo kök dizini)
EXTRACTED_DIR = os.path.join(TOOLS_DIR, "extracted")
FRAMES_DIR = os.path.join(TOOLS_DIR, "frames")
JSON_PATH = os.path.join(TOOLS_DIR, "colors.json")

def load_colors():
    if not os.path.exists(JSON_PATH):
        print("❌ colors.json dosyası bulunamadı!")
        return {}
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def colorize_and_merge():
    color_data = load_colors()
    if not color_data:
        return

    print("🎨 Çerçeve renklendirme ve birleştirme işlemi başlıyor...")

    for mod_id, effects in color_data.items():
        mod_extracted_dir = os.path.join(EXTRACTED_DIR, mod_id)
        
        if not os.path.exists(mod_extracted_dir):
            print(f"⚠️ {mod_id} için extracted klasörü bulunamadı, atlanıyor...")
            continue

        for effect_name, colors in effects.items():
            icon_file = f"{effect_name}.png"
            icon_path = os.path.join(mod_extracted_dir, icon_file)

            if not os.path.exists(icon_path):
                print(f"⚠️ İkon bulunamadı: {mod_id} -> {icon_file} (Atlanıyor)")
                continue

            if len(colors) < 9:
                print(f"⚠️ {effect_name} için 9 renk girilmemiş! En az 9 renk olmalı.")
                continue

            # Hedef çıktı klasörünü oluştur
            output_dir = os.path.join(REPO_DIR, "assets", mod_id, "textures", "mob_effect")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, icon_file)

            print(f"⏳ İşleniyor: {mod_id} -> {effect_name}")

            # Başlangıç komutu: Boş ve şeffaf bir 54x54 tuval oluşturuyoruz
            magick_cmd = ["magick", "-size", "54x54", "canvas:transparent"]
            
            # 9 çerçeveyi sırayla renklendirip tuvalin üstüne koyuyoruz
            for i in range(1, 10):
                frame_img = os.path.join(FRAMES_DIR, f"{i}.png")
                if not os.path.exists(frame_img):
                    print(f"❌ Kritik Hata: {i}.png çerçeve dilimi bulunamadı!")
                    return
                
                color = colors[i-1]
                
                # Biçimlendirme Mantığı:
                # 1. Şablonu açıyoruz.
                # 2. Şeffaf (alpha) kanalını kilitliyoruz (-alpha On).
                # 3. Beyaz olan pikselleri dolgu rengiyle boyuyoruz (-fill color -opaque white).
                magick_cmd += [
                    "(", frame_img, 
                    "-alpha", "On", 
                    "-fill", color, 
                    "-opaque", "white", 
                    ")", 
                    "-composite"
                ]
            
            # En son 36x36'lık orijinal ikonu alıp 54x54'lük tuvalin tam ortasına yerleştiriyoruz
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
                # Komutu çalıştır
                subprocess.run(magick_cmd, check=True)
            except Exception as e:
                print(f"❌ ImageMagick Hatası ({effect_name}): {e}")

    print("\n✅ Tüm ikonlar başarıyla çerçevelendi ve repoya aktarıldı!")

if __name__ == "__main__":
    colorize_and_merge()