import toml
import os
import json
import glob

CONFIG_PATH = "whisker/configs.toml"
VERSIONS_DIR = "whisker/versions/icons/changes"
CHANGED_PATH = "changed/icons.txt"

# 读取当前版本
with open(CONFIG_PATH, "r") as f:
    config = toml.load(f)

current_version = config["versions"]["icon"]
new_version = current_version + 1

# 更新版本号
config["versions"]["icon"] = new_version

with open(CONFIG_PATH, "w") as f:
    toml.dump(config, f)

# 读取改动的图标路径
with open(CHANGED_PATH, "r") as f:
    changed_files = [line.strip() for line in f.readlines() if line.strip().startswith("whisker/icons/")]

# 构造 changes 数组
changes = [{"icon": path.replace("whisker/icons/", "")} for path in changed_files]

# ✅ 确保目录存在
os.makedirs(VERSIONS_DIR, exist_ok=True)

# 创建版本 JSON 文件
version_file = os.path.join(VERSIONS_DIR, f"{new_version}.json")
with open(version_file, "w") as f:
    json.dump({
        "version": new_version,
        "changes": changes
    }, f, indent=2)
print(f"Version {new_version} generated with {len(changes)} changes.")

# ✅ 打印生成的 JSON 文件内容
json_content = {
    "version": new_version,
    "changes": changes
}
with open(version_file, "w") as f:
    json.dump(json_content, f, indent=2)
print(f"\n✅ Created JSON file: {version_file}")
print("🔍 Content:")
print(json.dumps(json_content, indent=2))
