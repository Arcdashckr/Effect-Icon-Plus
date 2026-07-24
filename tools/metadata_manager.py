import zipfile
import requests
from datetime import datetime
from common import *

def has_mob_effect_folder(namespace):
    """
    Checks if textures/mob_effect folder exists inside assets.
    """
    path = os.path.join(
        ASSETS_DIR,
        namespace,
        "textures",
        "mob_effect"
    )
    return os.path.isdir(path)

def extract_namespace_from_jar(jar_path):
    """
    Finds the actual namespace from the assets folder inside the JAR and verifies the existence of the mob_effect folder.
    """
    namespace = None
    has_mob_effect = False
    try:
        with zipfile.ZipFile(jar_path, "r") as jar:
            for name in jar.namelist():
                if "assets/" in name and "textures/mob_effect/" in name:
                    has_mob_effect = True
                    parts = name.split("/")
                    try:
                        assets_index = parts.index("assets")
                        ns = parts[assets_index + 1]
                        if ns and ns != "minecraft":
                            namespace = ns
                    except (ValueError, IndexError):
                        pass

            # If mob_effect not found, find any non-minecraft namespace
            if not namespace:
                for name in jar.namelist():
                    if not name.startswith("assets/"):
                        continue
                    parts = name.split("/")
                    if len(parts) < 2:
                        continue
                    ns = parts[1]
                    if ns and ns != "minecraft":
                        namespace = ns
                        break
    except Exception as e:
        print(f"[-] Failed to read namespace: {e}")
    return namespace, has_mob_effect

def fetch_curseforge_metadata(namespace, project_id):
    """
    Fetches CurseForge mod metadata using CFWidget API with a BeautifulSoup fallback.
    """
    # 1. Try CFWidget API first
    url = f"https://api.cfwidget.com/minecraft/mc-mods/{project_id}"
    try:
        r = requests.get(url, headers=MODRINTH_HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            author = None
            if "members" in data and data["members"]:
                owners = [m["username"] for m in data["members"] if m.get("title") == "Owner"]
                if owners:
                    author = owners[0]
                else:
                    author = data["members"][0]["username"]
            
            return {
                "namespace": namespace,
                "source": "curseforge",
                "project_id": str(data.get("id", "")),
                "slug": project_id,
                "page_url": data.get("urls", {}).get("project") or f"https://www.curseforge.com/minecraft/mc-mods/{project_id}",
                "name": data.get("title", project_id),
                "author": author or "Unknown",
                "organization": None,
                "icon_url": data.get("thumbnail"),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
    except Exception as e:
        print(f"[~] CFWidget failed: {e}. Trying direct HTML scraping...")

    # 2. BeautifulSoup fallback scraper
    url = f"https://www.curseforge.com/minecraft/mc-mods/{project_id}"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            from bs4 import BeautifulSoup
            import json
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Extract title
            title_meta = soup.find("meta", property="og:title")
            title = title_meta["content"] if title_meta else project_id
            if title.endswith(" - Minecraft Mods - CurseForge"):
                title = title[:-30]
            elif title.endswith(" - Mods - Minecraft - CurseForge"):
                title = title[:-32]
            
            # Extract icon
            image_meta = soup.find("meta", property="og:image")
            icon_url = image_meta["content"] if image_meta else None
            
            # Extract author
            author = None
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    ld_data = json.loads(script.string)
                    if isinstance(ld_data, list):
                        for item in ld_data:
                            if "author" in item:
                                author = item["author"].get("name") or item["author"].get("username")
                                break
                    elif isinstance(ld_data, dict):
                        if "author" in ld_data:
                            if isinstance(ld_data["author"], list) and ld_data["author"]:
                                author = ld_data["author"][0].get("name")
                            elif isinstance(ld_data["author"], dict):
                                author = ld_data["author"].get("name")
                except:
                    pass
            
            if not author:
                author_tag = soup.find("a", href=lambda href: href and href.startswith("/members/"))
                if author_tag:
                    author = author_tag.text.strip()
            
            return {
                "namespace": namespace,
                "source": "curseforge",
                "project_id": project_id,
                "slug": project_id,
                "page_url": url,
                "name": title,
                "author": author or "Unknown",
                "organization": None,
                "icon_url": icon_url,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
    except Exception as e:
        print(f"[-] HTML scraping failed: {e}")
        
    return None

def fetch_project_metadata(namespace, source, project_id):
    if not source:
        return None
    if source.lower() == "modrinth":
        url = f"https://api.modrinth.com/v3/project/{project_id}"
        response = requests.get(url, headers=MODRINTH_HEADERS)
        response.raise_for_status()
        project = response.json()
        author_name = None
        organization_name = None
        try:
            team = requests.get(
                f"https://api.modrinth.com/v3/project/{project['id']}/members",
                headers=MODRINTH_HEADERS
            ).json()
            if team:
                author_name = team[0]["user"]["username"]
            else:
                organization = requests.get(
                    f"https://api.modrinth.com/v3/organization/{project['organization']}",
                    headers=MODRINTH_HEADERS
                ).json()
                if organization:
                    organization_name = organization["name"]
        except Exception as e:
            print(f"[-] Failed to fetch author info: {e}")
            pass
        return {
            "namespace": namespace,
            "source": source,
            "project_id": project["id"],
            "slug": project["slug"],
            "page_url": f"https://modrinth.com/mod/{project['slug']}",
            "name": project["name"],
            "author": author_name,
            "organization": organization_name,
            "icon_url": project.get("icon_url"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    elif source.lower() == "curseforge":
        return fetch_curseforge_metadata(namespace, project_id)
    else:
        print(f"[-] Unsupported source: {source}")
        return None

def update_metadata(namespace, source, identifier):
    metadata = load_metadata()
    try:
        info = fetch_project_metadata(namespace, source, identifier)
        if not info:
            return False
        metadata[namespace] = info
        save_metadata(metadata)
        print(f"[+] Metadata updated: {namespace} -> {info['name']}")
        return True
    except Exception as e:
        print(f"[-] Failed to fetch metadata ({namespace}): {e}")
        return False

def update_existing_metadata():
    if not os.path.exists(ASSETS_DIR):
        print("[-] 'assets' folder not found.")
        return

    metadata = load_metadata()

    folders = [
        f for f in os.listdir(ASSETS_DIR)
        if os.path.isdir(os.path.join(ASSETS_DIR, f))
    ]
    folders = [f for f in folders if f != "minecraft"]

    # Only update folders that do not have metadata
    folders_to_update = [f for f in folders if f not in metadata]

    if not folders_to_update:
        print("[+] Metadata already exists for all asset folders.")
        return

    print(f"\nMetadata will be searched for {len(folders_to_update)} folders.\n")

    for folder in folders_to_update:
        print(f"\n[~] Processing: {folder}")
        # Try fetching Modrinth project with direct name match first
        if update_metadata(folder, "modrinth", folder):
            continue

        # If direct match fails, search Modrinth API
        print(f"[~] Searching Modrinth for '{folder}'...")
        hits = []
        try:
            r = requests.get(
                f"https://api.modrinth.com/v3/search?query={folder}",
                headers=MODRINTH_HEADERS
            )
            if r.status_code == 200:
                hits = r.json().get("hits", [])
        except Exception as e:
            print(f"[-] Error occurred during search: {e}")

        if hits:
            print(f"\nSearch results for '{folder}':")
            # Show up to 5 results
            display_count = min(len(hits), 5)
            for idx in range(display_count):
                hit = hits[idx]
                title = hit.get("name", "Unknown Title")
                slug = hit.get("slug", "unknown-slug")
                author = hit.get("author", "Unknown Author")
                desc = hit.get("description", "")
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                print(f"  [{idx + 1}] {title} (slug: {slug}) - Author: {author}")
                if desc:
                    print(f"      {desc}")

            print("  [m] Enter manual Modrinth Slug or Project ID")
            print("  [c] Enter manual CurseForge Slug")
            print("  [s] Skip")

            while True:
                choice = input("Your choice (1-5, m, c, s): ").strip().lower()
                if choice == 's':
                    break
                elif choice == 'm':
                    selected_slug = input("Please enter Modrinth Slug or Project ID: ").strip()
                    if selected_slug:
                        if update_metadata(folder, "modrinth", selected_slug):
                            break
                elif choice == 'c':
                    selected_slug = input("Please enter CurseForge Slug: ").strip()
                    if selected_slug:
                        if update_metadata(folder, "curseforge", selected_slug):
                            break
                else:
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < display_count:
                            selected_slug = hits[idx]["slug"]
                            if update_metadata(folder, "modrinth", selected_slug):
                                break
                    except ValueError:
                        pass
                    print("[-] Invalid choice, please try again.")
        else:
            print(f"[!] No results found on Modrinth for '{folder}'.")
            while True:
                choice = input("Choose source: [m] Modrinth Slug, [c] CurseForge Slug, [s] Skip: ").strip().lower()
                if choice == 's':
                    break
                elif choice == 'm':
                    selected_slug = input("Please enter Modrinth Slug or Project ID: ").strip()
                    if selected_slug:
                        if update_metadata(folder, "modrinth", selected_slug):
                            break
                elif choice == 'c':
                    selected_slug = input("Please enter CurseForge Slug: ").strip()
                    if selected_slug:
                        if update_metadata(folder, "curseforge", selected_slug):
                            break
                else:
                    print("[-] Invalid choice.")

def update_single_mod_metadata():
    namespace = input("Enter mod namespace (assets folder name, e.g. 'farmersdelight'): ").strip()
    if not namespace:
        print("[-] Namespace cannot be empty.")
        return

    print(f"\nSelect source for '{namespace}':")
    print("[1] Modrinth")
    print("[2] CurseForge")
    choice = input("Your choice (1-2): ").strip()

    if choice == "1":
        source = "modrinth"
        project_id = input("Enter Modrinth Slug or Project ID: ").strip()
    elif choice == "2":
        source = "curseforge"
        project_id = input("Enter CurseForge Slug: ").strip()
    else:
        print("[-] Invalid choice.")
        return

    if not project_id:
        print("[-] Slug/Project ID cannot be empty.")
        return

    success = update_metadata(namespace, source, project_id)
    if success:
        print("[~] Regenerating repository compatibility files...")
        try:
            import subprocess
            subprocess.run(["python", "generate_repo_files.py"], check=True)
            print("[+] compatibility.md and stats.json updated successfully!")
        except Exception as e:
            print(f"[-] Failed to automatically regenerate repository files: {e}")

def main():
    print("\n==================================================")
    print(" METADATA MANAGER")
    print("==================================================")
    print("[1] Update Metadata for All Missing/Existing Assets")
    print("[2] Update Metadata for a Single Specific Mod")
    print("==================================================")
    choice = input("Your choice (1-2): ").strip()

    if choice == "1":
        update_existing_metadata()
    elif choice == "2":
        update_single_mod_metadata()
    else:
        print("[-] Invalid choice.")

if __name__ == "__main__":
    main()