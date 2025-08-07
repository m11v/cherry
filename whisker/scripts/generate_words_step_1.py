import json
import os

ALL_JSON_PATH = "whisker/versions/icons/all.json"
OUTPUT_PATH = "whisker/versions/words/words_step_1.json"

def normalize_text(text):
    """替换 - 和 _ 为空格，转为小写"""
    return text.replace("-", " ").replace("_", " ").strip().lower()

# 读取 all.json
with open(ALL_JSON_PATH, "r") as f:
    all_data = json.load(f)

version = all_data.get("version")
changes = []

for item in all_data.get("changes", []):
    icon_path = item.get("icon")  # 例如 "vegetables/corn.png"

    parts = icon_path.split("/")
    if len(parts) < 2:
        continue  # 跳过无效路径

    category_raw = parts[0]
    filename = os.path.splitext(parts[1])[0]

    word = normalize_text(filename)
    category = normalize_text(category_raw)

    changes.append({
        "icon": icon_path,
        "word": word,
        "category": category
    })

# 构建输出 JSON
output_data = {
    "version": version,
    "changes": changes
}

# 写入 words_step_1.json
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"✅ Generated {OUTPUT_PATH} with {len(changes)} entries (version: {version})")
