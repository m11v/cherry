import toml
import os
import json
import glob

CONFIG_PATH = "whisker/configs.toml"
VERSIONS_DIR = "whisker/icons"
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

# 创建版本 JSON 文件
version_file = os.path.join(VERSIONS_DIR, f"version_{new_version}.json")
with open(version_file, "w") as f:
    json.dump({
        "version": new_version,
        "changes": changes
    }, f, indent=2)

print(f"Version {new_version} generated with {len(changes)} changes.")
