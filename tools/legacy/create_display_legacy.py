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
    if isinstance(mod_ids, str):
        mod_ids = [mod_ids]

    all_icons = []
    
    for mod_id in mod_ids:
        # Kod her zaman 'minecraft' klasörüne baksın
        folder_name = "minecraft" if mod_id == "vanilla" else mod_id
        effect_dir = os.path.join(ASSETS_DIR, folder_name, "textures", "mob_effect")
        
        if os.path.exists(effect_dir):
            icons_in_mod = glob.glob(os.path.join(effect_dir, "*.png"))
            all_icons.extend(icons_in_mod)

    if not all_icons:
        print("⚠️ Belirtilen klasörlerde hiç ikon (.png) bulunamadı.")
        return

    print(f"📸 Toplam {len(all_icons)} adet ikon tek bir resimde birleştiriliyor...")

    base_output = os.path.join(OUTPUT_DIR, f"effect_display_{output_name_suffix}.png")
    upscaled_output = os.path.join(OUTPUT_DIR, f"effect_display_{output_name_suffix}_upscaled.png")

    # 1. Standart Grid'i oluştur (İkon sayısına göre yüksekliği otomatik uzar)
    montage_cmd = [
        "magick", "montage"
    ] + all_icons + [
        "-background", "none",
        "-geometry", "54x54+5+5",
        "-tile", "10x",
        base_output
    ]

    try:
        subprocess.run(montage_cmd, check=True)
        print(f"✅ Standart grid oluşturuldu: {base_output}")

        # 2. ORANTILI VE SINIRSIZ (KIRPILMASIZ) UPSCALING
        # -extent komutunu tamamen kaldırdık. 
        # Resmi %400 (4 katı) oranında pikselleri bozmadan büyütür.
        # Yükseklik ne kadar uzun olursa olsun, kırpılmadan tam orantılı büyür.
        scale_cmd = [
            "magick", base_output,
            "-scale", "300%", 
            upscaled_output
        ]
        subprocess.run(scale_cmd, check=True)
        print(f"⚡ Keskin ve tam orantılı uzatılmış büyük grid oluşturuldu: {upscaled_output}")

    except Exception as e:
        print(f"❌ ImageMagick Grid Hatası: {e}")

def main():
    print("\n--------------------------------------------------")
    print("🖼️  ÖNİZLEME GRİDÜ (DISPLAY) OLUŞTURUCU")
    print("--------------------------------------------------")
    print("[1] Sadece Vanilla (Minecraft Klasörü) İçin Oluştur")
    print("[2] Belirli Bir Mod İçin Özel Oluştur")
    print("[3] Tüm Modlar İçin AYRI AYRI Resimler Oluştur")
    print("[4] HEPSİNİ TEK BİR RESİMDE BİRLEŞTİR (Sabit Link Dostu) 🔥")
    print("--------------------------------------------------")
    secim = input("Seçiminiz (1-4): ").strip()

    if not os.path.exists(ASSETS_DIR):
        print("❌ assets klasörü bulunamadı!")
        return

    all_folders = [f for f in os.listdir(ASSETS_DIR) if os.path.isdir(os.path.join(ASSETS_DIR, f))]

    if secim == "1":
        generate_grid("vanilla", "vanilla")
        
    elif secim == "2":
        mod_name = input("Lütfen mod klasörünün adını girin (Örn: alexsmobs): ").strip()
        if mod_name:
            generate_grid(mod_name, mod_name)
            
    elif secim == "3":
        for folder in all_folders:
            suffix = "vanilla" if folder == "minecraft" else folder
            generate_grid(folder, suffix)
            
    elif secim == "4":
        print("\nVanilla (Minecraft) efektleri de bu birleşik resme dahil edilsin mi?")
        vanilla_secim = input("Dahil edilsin mi? (E/H): ").strip().lower()
        
        target_mods = []
        for folder in all_folders:
            if folder == "minecraft":
                if vanilla_secim == "e":
                    target_mods.append("vanilla")
                continue
            target_mods.append(folder)
            
        generate_grid(target_mods, "mod")
        
    else:
        print("❌ Geçersiz seçim.")

if __name__ == "__main__":
    main()