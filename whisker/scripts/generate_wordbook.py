#!/usr/bin/env python3
import json
import toml
import sys
import argparse
from pathlib import Path

CONFIG_PATH = Path("whisker/configs.toml")
WORD_BOOK_DIR = Path("whisker/jsons/wordbook")

def main():
    parser = argparse.ArgumentParser(description="Generate new wordbook JSON and update configs.toml")
    parser.add_argument("--output-files", type=str, help="Path to save changed files list")
    args = parser.parse_args()

    # 1. 读取 configs.toml
    configs = toml.load(CONFIG_PATH)
    wordbook_version = configs["versions"]["wordbook"]
    words_version = configs["versions"]["words"]

    new_wordbook_version = wordbook_version + 1

    # 2. 构造文件路径
    full_file = WORD_BOOK_DIR / f"wordbook_full_{wordbook_version}.json"
    changes_file = WORD_BOOK_DIR / f"words_changes_{words_version}_to_wordbook.json"
    new_file = WORD_BOOK_DIR / f"wordbook_full_{new_wordbook_version}.json"

    # 3. 读取 JSON 文件
    try:
        with open(full_file, "r", encoding="utf-8") as f:
            full_data = json.load(f)
        with open(changes_file, "r", encoding="utf-8") as f:
            changes_data = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ 文件未找到: {e.filename}", file=sys.stderr)
        sys.exit(1)

    # 4. 合并并排序 words
    merged_words = full_data["words"] + changes_data["words"]
    merged_words.sort(key=lambda w: w.get("word", "").lower())

    # 5. 生成新 JSON
    new_data = {
        "version": changes_data["version"],
        "word_version": changes_data["word_version"],
        "icon_version": changes_data["icon_version"],
        "words": merged_words
    }

    with open(new_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    # 6. 更新 configs.toml
    configs["versions"]["wordbook"] = new_wordbook_version
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        toml.dump(configs, f)

    # 7. 输出修改文件路径（GitHub Actions 一行输出）
    changed_files = [str(new_file), str(CONFIG_PATH)]

    if args.output_files:
        with open(args.output_files, "w", encoding="utf-8") as f:
            f.write(" ".join(changed_files))
    else:
        print(" ".join(changed_files))

if __name__ == "__main__":
    main()
