import glob
from datetime import datetime
from common import *

# Configurable mod groups. You can easily add, remove, or edit groups here.
# Mods are grouped in order of appearance in this list.
MOD_GROUPS = [
    {
        "name": "Aether Series",
        "keywords": ["aether"]
    },
    {
        "name": "Create Add-ons",
        "keywords": ["create:", "createaddition", "create crafts"],
        "prefixes": ["create"]
    },
    {
        "name": "Farmer's Delight & Add-ons",
        "keywords": ["delight"]
    },
    {
        "name": "Let's Do Series",
        "keywords": ["let's do", "lets-do"]
    }
]

def get_mod_group_index(folder_name, display_name):
    name_lower = display_name.lower()
    folder_lower = folder_name.lower()
    
    for idx, group in enumerate(MOD_GROUPS):
        # Check prefixes if specified
        if "prefixes" in group:
            if any(name_lower.startswith(p) or folder_lower.startswith(p) for p in group["prefixes"]):
                return idx
        # Check keywords
        if "keywords" in group:
            if any(kw in name_lower or kw in folder_lower for kw in group["keywords"]):
                return idx
                
    return 99 # 99 represents "Other Mods"

def calculate_repo_stats_and_list():
    """Gathers detailed statistics from the repository"""
    if not os.path.exists(ASSETS_DIR):
        return 0, 0, {}
        
    mod_folders = [f for f in os.listdir(ASSETS_DIR) if os.path.isdir(os.path.join(ASSETS_DIR, f))]
    
    total_mods = len([m for m in mod_folders if m != "minecraft"]) # Mod count excluding vanilla
    total_effects = 0
    mod_list_with_counts = {}
    
    for folder in mod_folders:
        eff_dir = os.path.join(ASSETS_DIR, folder, "textures", "mob_effect")
        if os.path.exists(eff_dir):
            count = len(glob.glob(os.path.join(eff_dir, "*.png")))
            total_effects += count
            
            display_name = folder
            mod_list_with_counts[display_name] = count
            
    return total_mods, total_effects, mod_list_with_counts

def update_stats_json(total_mods, total_effects):
    """Creates/updates the tools/stats.json file"""

    stats = {
        "schemaVersion": 1,
        "label": "Effect Icon Plus",
        "message": "",
        "supported_mods": total_mods,
        "total_effect_icons": total_effects
    }

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

    print("[>] stats.json updated!")

def update_compatibility_file(mod_list_with_counts):
    metadata = load_metadata()

    # Pre-build list of items with their sorting criteria
    mod_items = []
    manual_items = []

    for folder_name, effect_count in mod_list_with_counts.items():
        info = metadata.get(folder_name)
        effects = f'**[{effect_count}]({GITHUB_REPO}/tree/main/assets/{folder_name}/textures/mob_effect)**'

        if folder_name == "minecraft":
            name = MINECRAFT_NAME
            author = MINECRAFT_AUTHOR
            page_url = MINECRAFT_PAGE_URL
            icon_url = MINECRAFT_ICON_URL
            if info:
                name = info.get("name") or name
                if name.lower() == "minecraft":
                    name = MINECRAFT_NAME
                author = info.get("author") or info.get("organization") or author
                if not author or author == "Unknown":
                    author = MINECRAFT_AUTHOR
                page_url = info.get("page_url") or page_url
                icon_url = info.get("icon_url") or icon_url
            icon = f'<a href="{page_url}"><img src="{icon_url}" width="32"></a>'
            mod = f'**[{name}]({page_url})**'
            author_str = f"by {author}"
            group_idx = get_mod_group_index(folder_name, name)
            mod_items.append({
                "folder_name": folder_name,
                "name": name,
                "author": author,
                "icon": icon,
                "mod": mod,
                "author_str": author_str,
                "effects": effects,
                "group_idx": group_idx
            })
        elif info:
            name = info.get("name") or folder_name
            author = info.get("organization") or info.get("author") or "Unknown"
            page_url = info.get("page_url")
            icon_url = info.get("icon_url")
            author_str = f"by {author}" if author != "Unknown" else "Unknown"

            is_manual = info.get("needs_manual_config", False) or not page_url

            if is_manual:
                # Mod needs manual configuration (dead link or unconfigured)
                icon = f'<img src="{icon_url}" width="32">' if icon_url else "❔"
                if page_url:
                    mod = f'~~[{name}]({page_url})~~ *(404 Not Found)*'
                else:
                    mod = f'**{name}** *(No URL)*'
                manual_items.append({
                    "folder_name": folder_name,
                    "name": name,
                    "author": author,
                    "icon": icon,
                    "mod": mod,
                    "author_str": author_str,
                    "effects": effects
                })
            else:
                icon = f'<a href="{page_url}"><img src="{icon_url}" width="32"></a>' if icon_url else "❔"
                mod = f'**[{name}]({page_url})**'
                group_idx = get_mod_group_index(folder_name, name)
                mod_items.append({
                    "folder_name": folder_name,
                    "name": name,
                    "author": author,
                    "icon": icon,
                    "mod": mod,
                    "author_str": author_str,
                    "effects": effects,
                    "group_idx": group_idx
                })
        else:
            # Asset folder exists, but no metadata found in mod_metadata.json
            manual_items.append({
                "folder_name": folder_name,
                "name": folder_name,
                "author": "Unknown",
                "icon": "❔",
                "mod": f'**{folder_name}** *(Metadata missing)*',
                "author_str": "Unknown",
                "effects": effects
            })

    # Sort key:
    # Group index < 99 -> sort by (group_idx, display_name.lower())
    # Group index == 99 -> sort by (99, author.lower(), display_name.lower())
    def sort_key(item):
        g_idx = item["group_idx"]
        author_lower = item["author"].lower()
        name_lower = item["name"].lower()
        
        if g_idx < 99:
            return (g_idx, "", name_lower)
        else:
            return (99, author_lower, name_lower)

    mod_items.sort(key=sort_key)
    manual_items.sort(key=lambda x: x["name"].lower())

    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_mods = len(mod_list_with_counts)
    total_effects = sum(mod_list_with_counts.values())

    lines.append("# 🧩 Mod Compatibility")
    lines.append("")
    lines.append(
        "Supported mods and their available effect icons."
    )
    lines.append("")
    lines.append("> 💡 Click the **icon** or **mod name** to open its page. </br>")
    lines.append("> 💡 Click the **effect count** to browse the resource pack assets.")
    lines.append("")
    lines.append(f"**Supported Mods:** {total_mods}")
    lines.append("")
    lines.append(f"**Total Effect Icons:** {total_effects}")
    lines.append("")
    lines.append(f"**Last Updated:** {now}")
    lines.append("")
    lines.append("| Icon | Mod | Author | Effects |")
    lines.append("|:---:|------|------|------:|")

    for item in mod_items:
        lines.append(
            f"| {item['icon']} | {item['mod']} | {item['author_str']} | {item['effects']} |"
        )

    if manual_items:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## ⚠️ Manual Configuration Required")
        lines.append("")
        lines.append("The following mods could not be verified automatically on Modrinth or CurseForge (page returned 404 or metadata is missing). Please configure them manually using `start.bat` (Option 5: Manage Mod Metadata):")
        lines.append("")
        lines.append("| Icon | Mod | Author | Effects |")
        lines.append("|:---:|------|------|------:|")
        for item in manual_items:
            lines.append(
                f"| {item['icon']} | {item['mod']} | {item['author_str']} | {item['effects']} |"
            )

    with open(COMPATIBILITY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("[>] compatibility.md updated!")

def main():
    import sys
    if "--check-links" in sys.argv or "--validate" in sys.argv:
        from metadata_manager import validate_and_repair_metadata
        validate_and_repair_metadata()
        return

    # Recalculate stats and generate files
    total_mods, total_effects, mod_list_with_counts = calculate_repo_stats_and_list()
    update_stats_json(total_mods, total_effects)
    update_compatibility_file(mod_list_with_counts)

if __name__ == "__main__":
    main()