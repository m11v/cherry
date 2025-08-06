import os
import json
import toml

CONFIG_PATH = "whisker/configs.toml"
ICONS_DIR = "whisker/icons"
OUTPUT_FILE = "whisker/versions/icons/all.json"

# 读取版本号
with open(CONFIG_PATH, "r") as f:
    config = toml.load(f)

version = config["versions"]["icon"]

# 收集所有图标路径
icon_files = []

for root, dirs, files in os.walk(ICONS_DIR):
    for file in files:
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, ICONS_DIR)
        icon_files.append({"icon": rel_path})

# 构造 JSON 内容
all_json = {
    "version": version,
    "changes": sorted(icon_files, key=lambda x: x["icon"])
}

# 确保输出目录存在
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# 写入 all.json
with open(OUTPUT_FILE, "w") as f:
    json.dump(all_json, f, indent=2)

print(f"✅ Generated {OUTPUT_FILE} with version {version} and {len(icon_files)} icons.")
