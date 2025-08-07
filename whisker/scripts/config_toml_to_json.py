import tomli
import json
import os

TOML_PATH = "whisker/configs.toml"
JSON_PATH = "whisker/configs.json"

# 读取 TOML
with open(TOML_PATH, "rb") as f:
    toml_data = tomli.load(f)

# 转成 JSON
os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(toml_data, f, indent=2, ensure_ascii=False)

print(f"✅ Converted {TOML_PATH} → {JSON_PATH}")
