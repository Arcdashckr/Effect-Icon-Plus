import os
import zipfile
import glob
from PIL import Image

# Klasör yolları
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
MODS_DIR = os.path.join(TOOLS_DIR, "mods")
EXTRACTED_DIR = os.path.join(TOOLS_DIR, "extracted")

os.makedirs(EXTRACTED_DIR, exist_ok=True)

def scale_image(source_path, dest_path, size=(36, 36)):
    """Resmi pikselleri bozmadan (Nearest Neighbor) 36x36 boyutuna büyütür."""
    try:
        with Image.open(source_path) as img:
            # Keskin pixel-art görüntüsü için NEAREST filtresi şart
            scaled_img = img.resize(size, Image.Resampling.NEAREST)
            scaled_img.save(dest_path)
        return True
    except Exception as e:
        print(f"[-] Resim büyütme hatası ({os.path.basename(source_path)}): {e}")
        return False

def extract_icons_from_jar(jar_path):
    """Jar dosyasındaki efekt ikonlarını ayıklar (programmer_art hariç)."""
    mod_name = os.path.splitext(os.path.basename(jar_path))[0]
    
    print(f"\n==================================================")
    print(f"[~] İşleniyor: {mod_name}")
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
                    
                    # Burada artık her zaman 36x36 olarak işlenecek
                    if scale_image(temp_source, dest_path):
                        print(f"  [>] Ayıklandı: [{mod_id}] -> {icon_name}")
                        extracted_count += 1
                        
                    if os.path.exists(temp_source):
                        os.remove(temp_source)
                        try:
                            os.removedirs(os.path.dirname(temp_source))
                        except OSError:
                            pass
                            
            if extracted_count > 0:
                print("--------------------------------------------------")
                print(f"[+] BAŞARILI: Toplam {extracted_count} adet ikon ayıklandı.")
            else:
                print(f"[!] Pas Geçildi: Bu modun içinde uygun efekt ikonu yok.")
                
    except Exception as e:
        print(f"[-] Jar okunurken hata oluştu ({os.path.basename(jar_path)}): {e}")

def main():
    print("\n==================================================")
    print(" MODLARDAN EFEKT İKONLARINI AYIKLAMA MODÜLÜ")
    print("==================================================")
    
    if not os.path.exists(MODS_DIR) or not os.listdir(MODS_DIR):
        print("[-] 'tools/mods/' klasörü boş veya bulunamadı. Lütfen önce mod indirin.")
        return
        
    jar_files = glob.glob(os.path.join(MODS_DIR, "*.jar")) + glob.glob(os.path.join(MODS_DIR, "*.zip"))
    
    print(f"[*] Toplam {len(jar_files)} adet arşiv dosyası bulundu. Ayıklama başlıyor...")
    
    for jar in jar_files:
        extract_icons_from_jar(jar)
        
    print("\n==================================================")
    print("[+] Ayıklama işlemi tamamlandı! Çıktılar 'tools/extracted/' klasöründe.")
    print("==================================================")

if __name__ == "__main__":
    main()