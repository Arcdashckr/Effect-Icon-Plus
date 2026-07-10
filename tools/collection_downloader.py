import os
import requests
import re

# Klasör yolları
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
MODS_DIR = os.path.join(TOOLS_DIR, "mods")

os.makedirs(MODS_DIR, exist_ok=True)

def extract_collection_id(user_input):
    user_input = user_input.strip()
    if "modrinth.com/collection/" in user_input:
        match = re.search(r"collection/([A-Za-z0-9\-_]+)", user_input)
        if match:
            return match.group(1)
    return user_input

def download_file(url, destination):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"[-] İndirme hatası: {e}")
        return False

def get_collection_mods(collection_id):
    headers = {"User-Agent": "Arcdashckr/Effect-Icon-Plus-Downloader (arcdashckr@gmail.com)"}
    url = f"https://api.modrinth.com/v3/collection/{collection_id}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # API verisi doğrudan bir liste veya projeleri içeren bir sözlük olabilir.
        # İki ihtimali de güvenli bir şekilde kontrol ediyoruz.
        projects = []
        if isinstance(data, list):
            projects = data
        elif isinstance(data, dict):
            projects = data.get("projects", data.get("works", []))
        
        mod_ids = []
        for proj in projects:
            if isinstance(proj, dict):
                p_id = proj.get("id") or proj.get("project_id") or proj.get("slug")
                if p_id:
                    mod_ids.append(p_id)
            elif isinstance(proj, str):
                mod_ids.append(proj)
                
        return mod_ids
    except Exception as e:
        print(f"[-] Koleksiyon API hatası. ID veya URL'nin doğru olduğundan emin olun: {e}")
        return []

def download_latest_jar(project_id):
    headers = {"User-Agent": "Arcdashckr/Effect-Icon-Plus-Downloader (arcdashckr@gmail.com)"}
    url = f"https://api.modrinth.com/v2/project/{project_id}/version"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        versions = response.json()
        
        if not versions:
            print(f"[!] {project_id} için hiçbir sürüm bulunamadı.")
            return

        latest_version = versions[0]
        files = latest_version.get("files", [])
        
        if not files:
            print(f"[!] {project_id} sürümünde dosya bulunamadı.")
            return
            
        primary_file = files[0]
        file_name = primary_file.get("filename")
        download_url = primary_file.get("url")
        
        if not file_name or not download_url:
            return

        dest_path = os.path.join(MODS_DIR, file_name)
        
        if os.path.exists(dest_path):
            print(f"[>] Zaten indirilmiş: {file_name}")
            return

        print(f"[+] İndiriliyor: {file_name} ...")
        if download_file(download_url, dest_path):
            print(f"[+] Başarıyla indirildi: {file_name}")
            
    except Exception as e:
        print(f"[-] Mod sürüm bilgisi alınamadı ({project_id}): {e}")

def main():
    print("\n==================================================")
    print(" MODRINTH KOLEKSİYON İNDİRİCİ (v3 API)")
    print("==================================================")
    print("Örnek Girişler:")
    print("- GZWPt17E")
    print("- https://modrinth.com/collection/MIpQPiMy")
    print("==================================================")
    
    user_input = input("Lütfen Koleksiyon ID'sini veya Linkini girin: ").strip()
    collection_id = extract_collection_id(user_input)
        
    if not collection_id:
        print("[-] Geçersiz giriş yaptınız.")
        return

    print(f"\n[~] Koleksiyon API üzerinden inceleniyor (ID: {collection_id})...")
    mod_ids = get_collection_mods(collection_id)
    
    if not mod_ids:
        print("[!] Koleksiyonda işlenecek mod bulunamadı ya da koleksiyon gizli/hatalı.")
        return

    print(f"[*] Koleksiyonda {len(mod_ids)} adet mod tespit edildi. İndirmeler başlatılıyor...\n")
    
    for index, project_id in enumerate(mod_ids, start=1):
        print(f"[{index}/{len(mod_ids)}] ", end="")
        download_latest_jar(project_id)

    print("\n[+] Bütün indirme işlemleri tamamlandı! Dosyalar 'tools/mods/' klasöründe.")

if __name__ == "__main__":
    main()