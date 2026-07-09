import os
import zipfile
import shutil
import subprocess

# Klasör yolları
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
MODS_DIR = os.path.join(TOOLS_DIR, "mods")
EXTRACTED_DIR = os.path.join(TOOLS_DIR, "extracted")

# Klasörleri kontrol et ve yoksa oluştur
os.makedirs(MODS_DIR, exist_ok=True)
os.makedirs(EXTRACTED_DIR, exist_ok=True)

def process_jar(jar_path):
    jar_name = os.path.basename(jar_path)
    print(f"\n📦 {jar_name} işleniyor...")
    
    with zipfile.ZipFile(jar_path, 'r') as jar:
        # Klasör içindeki tüm dosyaları tara
        for file_info in jar.infolist():
            filename = file_info.filename
            
            # Minecraft standart mob_effect doku yolunu ara
            # assets/<mod_id>/textures/mob_effect/<efekt>.png
            if "textures/mob_effect/" in filename and filename.endswith(".png"):
                # Klasör yapısını parçala (assets, mod_id, textures, mob_effect, resim_adi)
                parts = filename.split('/')
                if len(parts) >= 5:
                    mod_id = parts[1]
                    image_name = parts[-1]
                    
                    # Hedef geçici klasör yapısını oluştur
                    target_mod_dir = os.path.join(EXTRACTED_DIR, mod_id)
                    os.makedirs(target_mod_dir, exist_ok=True)
                    
                    # Resmi geçici olarak zipten çıkar
                    temp_extract_path = os.path.join(target_mod_dir, "temp_" + image_name)
                    final_output_path = os.path.join(target_mod_dir, image_name)
                    
                    with jar.open(filename) as source, open(temp_extract_path, "wb") as target:
                        shutil.copyfileobj(source, target)
                    
                    # ImageMagick ile kayıpsız (Nearest Neighbor) 2 katına büyütme (18x18 -> 36x36)
                    print(f"       ⚡ {mod_id} -> {image_name} büyütülüyor...")
                    try:
                        # -scale parametresi pikselleri bozmadan, bulandırmadan büyütür
                        subprocess.run([
                            "magick", temp_extract_path, 
                            "-scale", "200%", 
                            final_output_path
                        ], check=True)
                    except Exception as e:
                        print(f"       ❌ ImageMagick hatası ({image_name}): {e}")
                        # Eğer imagemagick hata verirse ham halini bırak
                        shutil.copy(temp_extract_path, final_output_path)
                    
                    # Geçici ham dosyayı temizle
                    if os.path.exists(temp_extract_path):
                        os.remove(temp_extract_path)

def main():
    jar_files = [f for f in os.listdir(MODS_DIR) if f.endswith(".jar")]
    
    if not jar_files:
        print("❌ 'mods' klasöründe herhangi bir .jar dosyası bulunamadı!")
        return
        
    print(f"🚀 Toplam {len(jar_files)} mod dosyası bulundu. İşlem başlıyor...")
    
    for jar_file in jar_files:
        jar_path = os.path.join(MODS_DIR, jar_file)
        process_jar(jar_path)
        
    print("\n✅ İşlem tamamlandı! Büyütülmüş ikonları 'tools/extracted/' klasöründe bulabilirsin.")

if __name__ == "__main__":
    main()