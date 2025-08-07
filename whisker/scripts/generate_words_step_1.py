import json
import os

ALL_JSON_PATH = "whisker/versions/icons/all.json"
OUTPUT_PATH = "whisker/versions/words/words_step_1.json"
NEW_ENTRIES_PATH = "whisker/versions/words/words_step_1_new.json"

def normalize_text(text):
    """替换 - 和 _ 为空格，转为小写"""
    return text.replace("-", " ").replace("_", " ").strip().lower()

# 读取 all.json
with open(ALL_JSON_PATH, "r", encoding="utf-8") as f:
    all_data = json.load(f)

version = all_data.get("version")
all_icons = {item["icon"] for item in all_data.get("changes", [])}

# 读取已有的 words_step_1.json（如果存在）
existing_changes = []
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
        existing_changes = existing_data.get("changes", [])

# 保留仍然在 all.json 中的 entries
kept_changes = [item for item in existing_changes if item["icon"] in all_icons]
kept_icons = {item["icon"] for item in kept_changes}

# 为新增 icon 构造新 entries
new_changes = []
for icon_path in all_icons:
    if icon_path in kept_icons:
        continue

    parts = icon_path.split("/")
    if len(parts) < 2:
        continue

    category_raw = parts[0]
    filename = os.path.splitext(parts[1])[0]

    word = normalize_text(filename)
    category = normalize_text(category_raw)

    new_changes.append({
        "icon": icon_path,
        "word": word,
        "category": category
    })

# 合并 + 排序
merged_changes = sorted(kept_changes + new_changes, key=lambda x: x["icon"])

# 输出 words_step_1.json（完整词表）
output_data = {
    "version": version,
    "changes": merged_changes
}
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

# 输出 words_step_1_new.json（仅新增部分）
new_output_data = {
    "version": version,
    "changes": sorted(new_changes, key=lambda x: x["icon"])
}
with open(NEW_ENTRIES_PATH, "w", encoding="utf-8") as f:
    json.dump(new_output_data, f, indent=2, ensure_ascii=False)

# 打印摘要
print(f"✅ words_step_1.json updated:")
print(f"   ➕ {len(new_changes)} new entries added")
print(f"   ➖ {len(existing_changes) - len(kept_changes)} removed (no longer in all.json)")
print(f"   📄 Total entries: {len(merged_changes)}")

print(f"🆕 words_step_1_new.json created with {len(new_changes)} new entries")
