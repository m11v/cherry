import toml
import json
import pathlib
import subprocess
import sys

def main():
    # 获取本 PR 中变更的 icon 文件
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True, text=True
    )
    changed_files = [
        f.strip() for f in result.stdout.splitlines()
        if f.startswith("whisker/icons/")
    ]

    if not changed_files:
        # 如果文件没有改变则输出“NO_ICON_CHANGES”，供 workflow 使用
        print("NO_ICON_CHANGES")
        sys.exit(0)

    # 读取 configs.toml
    config_path = pathlib.Path("whisker/configs.toml")
    data = toml.load(config_path)

    # 增加 icon 版本
    old_version = data["versions"]["icon"]
    new_version = old_version + 1
    data["versions"]["icon"] = new_version

    # 保存 configs.toml
    with open(config_path, "w") as f:
        toml.dump(data, f)

    # 生成 changes/{version}.json
    changes_dir = pathlib.Path("whisker/jsons/icons/changes")
    changes_dir.mkdir(parents=True, exist_ok=True)

    changes_list = [
        {"icon": "/".join(pathlib.Path(f).parts[2:])}
        for f in changed_files
    ]
    # 排序
    changes_list = sorted(changes_list, key=lambda x: x["icon"])

    version_json_data = {
        "version": new_version,
        "count": len(changes_list),
        "changes": changes_list
    }
    version_json_path = changes_dir / f"{new_version}.json"
    with open(version_json_path, "w") as f:
        json.dump(version_json_data, f, indent=2, ensure_ascii=False)

    # 生成 all.json（包含仓库中所有 icon 文件）
    all_icons = []
    icons_root = pathlib.Path("whisker/icons")
    for path in icons_root.rglob("*"):
        if path.is_file():
            all_icons.append({"icon": "/".join(path.relative_to(icons_root).parts)})
    # 排序
    all_icons = sorted(all_icons, key=lambda x: x["icon"])

    all_json_path = pathlib.Path("whisker/jsons/icons/all.json")
    all_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(all_json_path, "w") as f:
        json.dump({
                "version": new_version,
                "icons": all_icons,
                "count": len(all_icons),
            }, f, indent=2, ensure_ascii=False)

    # 输出需要 commit 的文件路径，供 workflow 使用
    print(f"{config_path} {version_json_path} {all_json_path}")

if __name__ == "__main__":
    main()
