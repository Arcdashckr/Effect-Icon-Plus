import os
import subprocess
import glob

# Klasör yolları
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(TOOLS_DIR)
ASSETS_DIR = os.path.join(REPO_DIR, "assets")
OUTPUT_DIR = os.path.join(REPO_DIR, "images", "display")
README_PATH = os.path.join(REPO_DIR, "README.md")
COMPAT_PATH = os.path.join(REPO_DIR, "compatibility.md")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def update_readme_stats(total_mods, total_effects):
    """README.md dosyasını kullanıcının özel rozet şablonuyla günceller"""
    if not os.path.exists(README_PATH):
        print("⚠️ README.md bulunamadı, istatistik yazımı atlanıyor.")
        return

    # Tamamen senin tasarladığın dinamik badge yapısı
    readme_template = f"""![Effect Icon+](https://github.com/Arcdashckr/Effect-Icon-Plus/blob/main/images/title/effect_icon_plus_title_horizontal.png?raw=true) </br>
<center>
<img src="https://github.com/Arcdashckr/Effect-Icon-Plus/blob/main/images/display/effect_display_vanilla.png?raw=true"> </br>

**Adds colored frames to the icons of the effects** </br>
**Experience a more vibrant and colorful look** </br> </br>
---

<p align="center">
    <img src="https://img.shields.io/badge/Supported_Mods-_?style=for-the-badge&logo=modrinth&logoColor=%2300AF5C&logoSize=64&label={total_mods}&labelColor=black&color=00753F&link=https%3A%2F%2Fgithub.com%2FArcdashckr%2FEffect-Icon-Plus%2Fblob%2Fmain%2Fcompatibility.md" alt="Supported Mods Count: {total_mods}">
    &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
    <img src="https://img.shields.io/badge/Total_Effect_Icons-_?style=for-the-badge&logo=buffer&logoColor=%23FFFFFF&logoSize=64&label={total_effects}&labelColor=black&color=blue&link=https%3A%2F%2Fgithub.com%2FArcdashckr%2FEffect-Icon-Plus%2Ftree%2Fmain%2Fassets" alt="Total Effects Count: {total_effects}">
</p>

<img src="https://github.com/Arcdashckr/Effect-Icon-Plus/blob/main/images/display/effect_display_mod.png?raw=true"> </br>
**Check mod compatibility list from <a href="https://github.com/Arcdashckr/Effect-Icon-Plus/blob/main/compatibility.md" target="_blank">here</a>** </br>
**Request mod compatibility from <a href="https://github.com/Arcdashckr/Effect-Icon-Plus/issues" target="_blank">here</a>** </br> </br>
---

### <a href="https://github.com/Arcdashckr/Effect-Icon-Plus/blob/main/permission/" target="_blank">*</a>Thanks to <a href="https://www.planetminecraft.com/texture-pack/upgrade-effect-icon/" target="_blank">Upgrade Effect Icon</a> by <a href="https://www.planetminecraft.com/member/the_dark_side_of_rero/" target="_blank">CherryRero</a>
</center>"""

    try:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(readme_template)
        print("📝 README.md istatistikleri ve özel rozetleriniz güncellendi!")
    except Exception as e:
        print(f"❌ README.md güncellenirken hata oluştu: {e}")

def update_compatibility_file(mod_list_with_counts):
    """compatibility.md dosyasını güncel bir tablo halinde otomatik oluşturur"""
    try:
        # Mod listesini alfabetik sıralayalım
        sorted_mods = sorted(mod_list_with_counts.items())
        
        compat_content = "# 🧩 Mod Compatibility List\n\n"
        compat_content += "Here is the list of all supported mods and the total number of effect icons for each.\n\n"
        compat_content += "| # | Mod ID | Total Effect Icons |\n"
        compat_content += "|---|--------|--------------------|\n"
        
        for index, (mod_id, count) in enumerate(sorted_mods, start=1):
            compat_content += f"| {index} | `{mod_id}` | {count} |\n"
            
        with open(COMPAT_PATH, "w", encoding="utf-8") as f:
            f.write(compat_content)
        print("📝 compatibility.md tablosu başarıyla güncellendi!")
    except Exception as e:
        print(f"❌ compatibility.md güncellenirken hata oluştu: {e}")

def calculate_repo_stats_and_list():
    """Tüm repodaki detaylı istatistikleri toplar"""
    if not os.path.exists(ASSETS_DIR):
        return 0, 0, {}
        
    mod_folders = [f for f in os.listdir(ASSETS_DIR) if os.path.isdir(os.path.join(ASSETS_DIR, f))]
    
    total_mods = len([m for m in mod_folders if m != "minecraft"]) # Vanilla hariç mod sayısı
    total_effects = 0
    mod_list_with_counts = {}
    
    for folder in mod_folders:
        eff_dir = os.path.join(ASSETS_DIR, folder, "textures", "mob_effect")
        if os.path.exists(eff_dir):
            count = len(glob.glob(os.path.join(eff_dir, "*.png")))
            total_effects += count
            
            # Tabloya eklerken minecraft klasörünü 'vanilla' olarak isimlendirelim
            display_name = "vanilla" if folder == "minecraft" else folder
            mod_list_with_counts[display_name] = count
            
    return total_mods, total_effects, mod_list_with_counts

def generate_grid(mod_ids, output_name_suffix):
    if isinstance(mod_ids, str):
        mod_ids = [mod_ids]

    all_icons = []
    for mod_id in mod_ids:
        folder_name = "minecraft" if mod_id == "vanilla" else mod_id
        effect_dir = os.path.join(ASSETS_DIR, folder_name, "textures", "mob_effect")
        if os.path.exists(effect_dir):
            all_icons.extend(glob.glob(os.path.join(effect_dir, "*.png")))

    if not all_icons:
        print("⚠️ Belirtilen klasörlerde hiç ikon (.png) bulunamadı.")
        return

    base_output = os.path.join(OUTPUT_DIR, f"effect_display_{output_name_suffix}.png")
    upscaled_output = os.path.join(OUTPUT_DIR, f"effect_display_{output_name_suffix}_upscaled.png")

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

        scale_cmd = [
            "magick", base_output,
            "-scale", "300%", 
            upscaled_output
        ]
        subprocess.run(scale_cmd, check=True)
        print(f"⚡ Keskin ve tam orantılı büyük grid oluşturuldu: {upscaled_output}")

        # Her grid üretiminde tüm sistem istatistiklerini hesapla ve dosyaları enjekte et
        total_mods, total_effects, mod_list_with_counts = calculate_repo_stats_and_list()
        
        # Dosyaları güncelle
        update_readme_stats(total_mods, total_effects)
        update_compatibility_file(mod_list_with_counts)

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
        mod_name = input("Lütfen mod klasörünün adını girin: ").strip()
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