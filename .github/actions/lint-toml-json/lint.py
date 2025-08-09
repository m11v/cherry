# .github/actions/lint-toml-json/lint.py
import sys
import subprocess
import json
from pathlib import Path
import tomli
import toml

IGNORE_DIRS = {"node_modules", "vendor", ".venv", ".git"}

def get_changed_files():
    try:
        base = subprocess.check_output(
            ["git", "merge-base", "origin/main", "HEAD"],
            text=True
        ).strip()
    except subprocess.CalledProcessError:
        base = "HEAD~1"

    files = subprocess.check_output(
        ["git", "diff", "--name-only", base],
        text=True
    ).splitlines()

    result = []
    for f in files:
        p = Path(f)
        if not p.exists():
            continue
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        if p.suffix in (".json", ".toml"):
            result.append(p)
    return result

def validate_json(path: Path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return True, data
    except Exception:
        return False, None

def validate_toml(path: Path):
    try:
        with path.open("rb") as f:
            data = tomli.load(f)
        return True, data
    except Exception:
        return False, None

def format_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def format_toml(path: Path, data):
    # 使用 toml 库写回（保持原有数据结构）
    path.write_text(toml.dumps(data), encoding="utf-8")

def main():
    files = get_changed_files()
    if not files:
        print("✅ No changed JSON/TOML files to check.")
        sys.exit(0)

    print(f"🔍 Checking {len(files)} changed files...")
    json_failed = []
    toml_failed = []
    formatted = []

    for file in files:
        if file.suffix == ".json":
            valid, data = validate_json(file)
            if not valid:
                json_failed.append(file)
            else:
                before = file.read_text(encoding="utf-8")
                format_json(file, data)
                after = file.read_text(encoding="utf-8")
                if before != after:
                    formatted.append(str(file))
        elif file.suffix == ".toml":
            valid, data = validate_toml(file)
            if not valid:
                toml_failed.append(file)
            else:
                before = file.read_text(encoding="utf-8")
                format_toml(file, data)
                after = file.read_text(encoding="utf-8")
                if before != after:
                    formatted.append(str(file))

    if json_failed:
        print("❌ Invalid JSON files:")
        for f in json_failed:
            print(f"   {f}")
    if toml_failed:
        print("❌ Invalid TOML files:")
        for f in toml_failed:
            print(f"   {f}")

    if json_failed or toml_failed:
        sys.exit(1)

    if formatted:
        # 去重并排序，写入 .lint-formatted（每行一个相对路径）
        unique_sorted = sorted(set(formatted))
        Path(".lint-formatted").write_text("\n".join(unique_sorted) + "\n")
        print(f"🛠 Formatted {len(unique_sorted)} files:")
        for f in unique_sorted:
            print(f"   {f}")
    else:
        # 确保不存在或为空
        if Path(".lint-formatted").exists():
            Path(".lint-formatted").unlink()
        print("✅ All JSON/TOML files are valid and formatted!")

if __name__ == "__main__":
    main()
