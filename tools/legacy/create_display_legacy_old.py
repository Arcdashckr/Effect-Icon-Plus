import os
import subprocess
import glob

# Klasör yolları
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(TOOLS_DIR)
ASSETS_DIR = os.path.join(REPO_DIR, "assets")
OUTPUT_DIR = os.path.join(REPO_DIR, "images", "display")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_grid(mod_ids, output_name_suffix):
    """
    Belirtilen mod klasörlerindeki tüm ikonları toplar ve tek bir grid resmi oluşturur.
    mod_ids: Liste veya tek bir string (Klasör adları)
    """
    if isinstance(mod_ids, str):
        mod_ids = [mod_ids]

    all_icons = []
    
    # Tüm hedef mod klasörlerindeki ikonları topla
    for mod_id in mod_ids:
        effect_dir = os.path.join(ASSETS_DIR, mod_id, "textures", "mob_effect")
        if os.path.exists(effect_dir):
            icons_in_mod = glob.glob(os.path.join(effect_dir, "*.png"))
            all_icons.extend(icons_in_mod)

    if not all_icons:
        print("⚠️ Belirtilen klasörlerde hiç ikon (.png) bulunamadı.")
        return

    print(f"📸 Toplam {len(all_icons)} adet ikon tek bir resimde birleştiriliyor...")

    # Çıktı dosya isimleri (Eğer özel isim verilmişse onu kullanır)
    base_output = os.path.join(OUTPUT_DIR, f"effect_display_{output_name_suffix}.png")
    upscaled_output = os.path.join(OUTPUT_DIR, f"effect_display_{output_name_suffix}_upscaled.png")

    # ImageMagick Montage Komutu:
    # Tüm ikon yollarını komuta tek tek eklemek yerine geçici bir listeden veya doğrudan besliyoruz
    montage_cmd = [
        "magick", "montage"
    ] + all_icons + [
        "-background", "none",
        "-geometry", "54x54+5+5",
        "-tile", "10x",
        base_output
    ]

    try:
        # 1. Standart Grid'i oluştur
        subprocess.run(montage_cmd, check=True)
        print(f"✅ Sabit isimli grid oluşturuldu: {base_output}")

        # 2. 1920x1080 Sınırlarına Kayıpsız Upscale Etme
        scale_cmd = [
            "magick", base_output,
            "-scale", "1920x1080",
            upscaled_output
        ]
        subprocess.run(scale_cmd, check=True)
        print(f"⚡ Sabit isimli yüksek çözünürlüklü grid oluşturuldu: {upscaled_output}")

    except Exception as e:
        print(f"❌ ImageMagick Grid Hatası: {e}")

def main():
    print("\n--------------------------------------------------")
    print("🖼️  ÖNİZLEME GRİDÜ (DISPLAY) OLUŞTURUCU")
    print("--------------------------------------------------")
    print("[1] Sadece Vanilla (Minecraft) İçin Oluştur")
    print("[2] Belirli Bir Mod İçin Özel Oluştur")
    print("[3] Tüm Modlar İçin AYRI AYRI Resimler Oluştur")
    print("[4] HEPSİNİ TEK BİR RESİMDE BİRLEŞTİR (Sabit Link Dostu) 🔥")
    print("--------------------------------------------------")
    secim = input("Seçiminiz (1-4): ").strip()

    if not os.path.exists(ASSETS_DIR):
        print("❌ assets klasörü bulunamadı!")
        return

    # Tüm mod klasörlerini listele
    all_folders = [f for f in os.listdir(ASSETS_DIR) if os.path.isdir(os.path.join(ASSETS_DIR, f))]

    if secim == "1":
        generate_grid("minecraft", "vanilla")
        
    elif secim == "2":
        mod_name = input("Lütfen mod klasörünün adını girin (Örn: alexsmobs): ").strip()
        if mod_name:
            generate_grid(mod_name, mod_name)
            
    elif secim == "3":
        for folder in all_folders:
            generate_grid(folder, folder)
            
    elif secim == "4":
        # Vanilla (minecraft) klasörünü de bu dev birleşik resme dahil etmek istiyor musun?
        print("\nVanilla (Minecraft) efektleri de bu birleşik resme dahil edilsin mi?")
        vanilla_secim = input("Dahil edilsin mi? (E/H): ").strip().lower()
        
        target_mods = []
        for folder in all_folders:
            if folder == "minecraft" and vanilla_secim != "e":
                continue
            target_mods.append(folder)
            
        # Tam olarak istediğin dosya isimleriyle kaydeder:
        # -> effect_display_mod.png
        # -> effect_display_mod_upscaled.png
        generate_grid(target_mods, "mod")
        
    else:
        print("❌ Geçersiz seçim.")

if __name__ == "__main__":
    main()