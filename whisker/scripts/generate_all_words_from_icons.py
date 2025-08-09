import json
import toml
import argparse
from pathlib import Path

CONFIG_PATH = Path("whisker/configs.toml")
ICONS_JSON_PATH = Path("whisker/jsons/icons/all.json")
WORDS_DIR = Path("whisker/jsons/words")

parser = argparse.ArgumentParser()
parser.add_argument("--output-files", help="Path to save list of changed files")
args = parser.parse_args()

# 1. Read old versions
config_data = toml.load(CONFIG_PATH)
old_words_version = config_data["versions"]["words"]
new_words_version = old_words_version + 1
icon_version = config_data["versions"]["icon"]

# 2. Read icons data
with open(ICONS_JSON_PATH, "r", encoding="utf-8") as f:
    icons_data = json.load(f)

# 3. Transform icons into words format
words_list = []
for item in icons_data.get("icons", []):
    icon_path = item.get("icon")
    if not icon_path:
        continue

    parts = icon_path.split("/")
    if len(parts) != 2:
        continue

    category_raw, filename_raw = parts
    category = category_raw.replace("_", " ").replace("-", " ")
    word = filename_raw.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")

    words_list.append({
        "icon": icon_path,
        "word": word,
        "category": category
    })

# 🔹 排序（按 icon 升序）
words_list.sort(key=lambda w: w["icon"])

# 4. Create new words file
WORDS_DIR.mkdir(parents=True, exist_ok=True)
new_words_file = WORDS_DIR / f"words_{new_words_version}.json"

output_data = {
    "version": new_words_version,
    "icon_version": icon_version,
    "words": words_list
}

with open(new_words_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

# 🔹 新增需求：比较新旧文件，生成 changes 文件
old_words_file = WORDS_DIR / f"words_{old_words_version}.json"
changes_file = None
if old_words_file.exists():
    with open(old_words_file, "r", encoding="utf-8") as f:
        old_data = json.load(f)
    old_icons = {w["icon"] for w in old_data.get("words", [])}

    new_entries = [w for w in words_list if w["icon"] not in old_icons]
    new_entries.sort(key=lambda w: w["icon"])  # 排序新词条

    if new_entries:
        changes_file = WORDS_DIR / f"words_changes_{new_words_version}.json"
        changes_output = {
            "version": new_words_version,
            "icon_version": icon_version,
            "new_words": new_entries
        }
        with open(changes_file, "w", encoding="utf-8") as f:
            json.dump(changes_output, f, ensure_ascii=False, indent=2)
        print(f"Generated {changes_file} with {len(new_entries)} new entries.")
    else:
        print("No new entries found.")
else:
    print(f"No old words file found: {old_words_file}")

# 5. Update configs.toml
config_data["versions"]["words"] = new_words_version
with open(CONFIG_PATH, "w", encoding="utf-8") as f:
    toml.dump(config_data, f)

print(f"Generated {new_words_file} with {len(words_list)} words.")

# 6. Output changed files list for GitHub Action
changed_files = [str(new_words_file), str(CONFIG_PATH)]
if changes_file:
    changed_files.append(str(changes_file))

if args.output_files:
    with open(args.output_files, "w") as f:
        f.write(" ".join(changed_files))
