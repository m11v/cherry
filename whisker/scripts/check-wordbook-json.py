import json
import os
import re
import argparse
from collections import OrderedDict

# 音标 -> 拼音映射表
phoneme_map = {
    "ˈ": "ˈ",
    "ˌ": "ˌ",
    "iː": "i",
    "ɪ": "i",
    "e": "e",
    "æ": "ai",
    "ɑː": "a～",
    "ɒ": "o",
    "ɔː": "ao～",
    "ʊ": "u",
    "uː": "u～",
    "ʌ": "a",
    "ɜː": "e～",
    "ə": "e",
    "eɪ": "ei",
    "aɪ": "ai",
    "ɔɪ": "ao i",
    "aʊ": "ao u",
    "əʊ": "ou",
    "oʊ": "ou",
    "ɪə": "i e",
    "eə": "ei e",
    "ʊə": "u e",
    "p": "p",
    "b": "b",
    "t": "t",
    "d": "d",
    "k": "k",
    "g": "g",
    "tʃ": "q",
    "dʒ": "j",
    "f": "f",
    "v": "v",
    "θ": "s",
    "ð": "z",
    "s": "s",
    "z": "z",
    "ʃ": "sh",
    "ʒ": "zh",
    "h": "h",
    "m": "m",
    "n": "n",
    "ŋ": "ng",
    "l": "l",
    "r": "r",
    "j": "y",
    "w": "w"
}

FIELD_ORDER = ["icon", "word", "category", "ps", "pt", "cps", "cpt", "hans", "hant", "ts", "tt", "py"]

def parse_ps_to_py(ps):
    # ps 格式示例: "/kæt/"
    # 去除前后斜杠
    if not ps:
        return ""
    ps = ps.strip("/")
    # 音标拆分，优先匹配多字符音标
    phonemes = sorted(phoneme_map.keys(), key=len, reverse=True)
    pattern = '|'.join(re.escape(p) for p in phonemes)
    tokens = re.findall(pattern, ps)
    py_parts = []
    for t in tokens:
        if t in phoneme_map:
            py_parts.append(phoneme_map[t])
        else:
            py_parts.append(t)  # 找不到映射原样放
    return ' '.join(py_parts)

def fix_ps(ps):
    if not ps:
        return ps
    if not ps.startswith('/'):
        ps = '/' + ps
    if not ps.endswith('/'):
        ps = ps + '/'
    return ps

def reorder_dict(d):
    # 按照 FIELD_ORDER 重新排序字典，未列出字段排后面
    new_d = OrderedDict()
    for key in FIELD_ORDER:
        if key in d:
            new_d[key] = d[key]
    for k, v in d.items():
        if k not in new_d:
            new_d[k] = v
    return new_d

def main():
    parser = argparse.ArgumentParser(description="Generate new wordbook JSON and update configs.toml")
    parser.add_argument("--output-files", type=str, help="Path to save changed files list")
    args = parser.parse_args()

    base_dir = "../jsons/wordbook"
    changed_files = []

    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.endswith(".json"):
                continue
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            changed = False

            # 1. 补count字段
            if "count" not in data:
                if "words" in data and isinstance(data["words"], list):
                    data["count"] = len(data["words"])
                    changed = True

            # 2. words中每个元素处理
            if "words" in data and isinstance(data["words"], list):
                for i, w in enumerate(data["words"]):
                    if not isinstance(w, dict):
                        continue

                    # 修正 ps 字段，确保前后有 /
                    old_ps = w.get("ps", "")
                    fixed_ps = fix_ps(old_ps)
                    if fixed_ps != old_ps:
                        w["ps"] = fixed_ps
                        changed = True

                    # 补 py 字段
                    if "py" not in w or not w["py"]:
                        py_value = parse_ps_to_py(w.get("ps", ""))
                        if py_value != "":
                            w["py"] = py_value
                            changed = True

                    # 调整字段顺序
                    new_word = reorder_dict(w)
                    if list(w.keys()) != list(new_word.keys()):
                        data["words"][i] = new_word
                        changed = True

            if changed:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                changed_files.append(path)

    # 输出修改文件路径（GitHub Actions 一行输出）
    if args.output_files:
        with open(args.output_files, "w", encoding="utf-8") as f:
             f.write(" ".join(changed_files))
    else:
        print(" ".join(changed_files))

if __name__ == "__main__":
    main()
