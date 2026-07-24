import os
import requests
import re
from common import *
from metadata_manager import *

os.makedirs(MODS_DIR, exist_ok=True)

def extract_collection_id(user_input):
    user_input = user_input.strip()
    if "modrinth.com/collection/" in user_input:
        match = re.search(r"collection/([A-Za-z0-9\-_]+)", user_input)
        if match:
            return match.group(1)
    return user_input

def extract_project_id(user_input):
    user_input = user_input.strip()
    if "modrinth.com/mod/" in user_input:
        match = re.search(r"mod/([A-Za-z0-9\-_]+)", user_input)
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
        print(f"[-] Download error: {e}")
        return False

def get_collection_mods(collection_id):
    url = f"https://api.modrinth.com/v3/collection/{collection_id}"
    try:
        response = requests.get(url, headers=MODRINTH_HEADERS)
        response.raise_for_status()
        data = response.json()
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
        print(f"[-] Collection API error. Make sure the ID or URL is correct: {e}")
        return []

def download_latest_jar(project_id):
    url = f"https://api.modrinth.com/v2/project/{project_id}/version"
    try:
        response = requests.get(url, headers=MODRINTH_HEADERS)
        response.raise_for_status()
        versions = response.json()
        if not versions:
            print(f"[!] No versions found for {project_id}.")
            return
        latest_version = versions[0]
        files = latest_version.get("files", [])
        if not files:
            print(f"[!] No files found for {project_id} version.")
            return
        primary_file = files[0]
        file_name = primary_file.get("filename")
        download_url = primary_file.get("url")
        if not file_name or not download_url:
            return
        dest_path = os.path.join(MODS_DIR, file_name)
        if os.path.exists(dest_path):
            print(f"[>] Already downloaded: {file_name}")
            return
        print(f"[+] Downloading: {file_name} ...")
        if download_file(download_url, dest_path):
            namespace, has_mob_effect = extract_namespace_from_jar(dest_path)
            if not namespace:
                print("[!] Namespace not found.")
                try:
                    os.remove(dest_path)
                except:
                    pass
                return
            if not has_mob_effect:
                print(f"[!] {namespace} is not supported (no mob_effect folder). Deleting...")
                try:
                    os.remove(dest_path)
                except:
                    pass
                return
            update_metadata(namespace, "modrinth", project_id)
    except Exception as e:
        print(f"[-] Could not get mod version info ({project_id}): {e}")

def main():
    print("\n==================================================")
    print(" MODRINTH DOWNLOADER")
    print("==================================================")
    print("[1] Download Collection")
    print("[2] Download Single Mod")
    print("==================================================")
    choice = input("Your choice (1-2): ").strip()

    if choice not in ("1", "2"):
        print("[-] Invalid choice.")
        return

    if choice == "1":
        print("\nExample Inputs:")
        print("- GZWPt17E")
        print("- https://modrinth.com/collection/MIpQPiMy")
        print("==================================================")
        user_input = input("Please enter Collection ID or Link: ").strip()
        collection_id = extract_collection_id(user_input)
        if not collection_id:
            print("[-] Invalid input.")
            return
        print(f"\n[~] Querying collection via API (ID: {collection_id})...")
        mod_ids = get_collection_mods(collection_id)
        if not mod_ids:
            print("[!] No mods found to process in the collection or the collection is private/invalid.")
            return
        print(f"[*] Detected {len(mod_ids)} mods in the collection. Starting downloads...\n")
        for index, project_id in enumerate(mod_ids, start=1):
            print(f"[{index}/{len(mod_ids)}] ", end="")
            download_latest_jar(project_id)

    elif choice == "2":
        print("\nExample Inputs:")
        print("- sodium")
        print("- https://modrinth.com/mod/sodium")
        print("==================================================")
        user_input = input("Please enter Mod Slug or Link: ").strip()
        project_id = extract_project_id(user_input)
        if not project_id:
            print("[-] Invalid input.")
            return
        print(f"\n[~] Querying mod via API (ID: {project_id})...")
        download_latest_jar(project_id)

    print("\n[+] All download operations completed! Files are in 'tools/mods/' folder.")

if __name__ == "__main__":
    main()