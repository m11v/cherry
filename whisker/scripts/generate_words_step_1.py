import json
import os

ALL_JSON_PATH = "whisker/versions/icons/all.json"
OUTPUT_PATH = "whisker/versions/words/words_step_1.json"

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

# 保留 still valid 的 entries（即仍然在 all.json 中的 icon）
kept_changes = [item for item in existing_changes if item["icon"] in all_icons]
kept_icons = {item["icon"] for item in kept_changes}

# 为新增 icon 构造新 entries
new_changes = []
for icon_path in all_icons:
    if icon_path in kept_icons:
        continue  # 已存在，跳过

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

# 合并并排序（按 icon 排序）
merged_changes = sorted(kept_changes + new_changes, key=lambda x: x["icon"])

# 构建最终输出
output_data = {
    "version": version,
    "changes": merged_changes
}

# 写入
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"✅ words_step_1.json updated:")
print(f"   ➕ {len(new_changes)} new entries added")
print(f"   ➖ {len(existing_changes) - len(kept_changes)} removed (no longer in all.json)")
print(f"   📄 Total entries: {len(merged_changes)}")
