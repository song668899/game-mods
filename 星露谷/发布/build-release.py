#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发布包组装工具（星露谷整合包 → 单个 ZIP，师爷式结构）

用法（一律 python -X utf8）：
  python -X utf8 build-release.py --manifest   扫描 Mods 生成 mod-manifest.csv
  python -X utf8 build-release.py --dry-run    打印组装计划，不复制不压缩
  python -X utf8 build-release.py              组装 stage + 打 ZIP（默认 v1.0）
  python -X utf8 build-release.py --version 1.1

产物：D:\\星露谷MOD\\MOD上传\\【星露谷整合包】v<版本>.zip
"""
import argparse
import csv
import datetime
import io
import json
import os
import re
import shutil
import stat
import sys
import time
import zipfile

ROOT = r"D:\星露谷MOD"
MODS_DIR = os.path.join(ROOT, "游戏", "Mods")
SMAPI_DIR = os.path.join(ROOT, "SMAPI 4.5.2 installer")
HERE = os.path.dirname(os.path.abspath(__file__))          # D:\星露谷MOD\发布
TPL_DIR = os.path.join(HERE, "模板")
STAGE_ROOT = os.path.join(HERE, "stage")
OUT_DIR = os.path.join(ROOT, "MOD上传")
CSV_PATH = os.path.join(HERE, "mod-manifest.csv")
SMAPI_LOG = os.path.join(
    os.environ.get("APPDATA", ""), "StardewValley", "ErrorLogs", "SMAPI-latest.txt")
DEFAULT_VER = "1.0"


def _strip_line_comments(text):
    """剥行尾 // 注释（引号感知，不伤字符串内的 //）。"""
    out = []
    for line in text.splitlines(True):
        in_str, i, cut = False, 0, None
        while i < len(line):
            c = line[i]
            if in_str:
                if c == "\\":
                    i += 2
                    continue
                if c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c == "/" and i + 1 < len(line) and line[i + 1] == "/":
                cut = i
                break
            i += 1
        out.append(line[:cut] if cut is not None else line)
    return "".join(out)


def _loose_json(text):
    """剥 /* */ 与行尾 // 注释、尾逗号后再解析（对齐 SMAPI/Newtonsoft 容忍集）。"""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = _strip_line_comments(text)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return json.loads(text)


def scan_mods():
    """扫描游戏\\Mods：返回目录清单（含 manifest 元数据）。"""
    rows = []
    for entry in sorted(os.scandir(MODS_DIR), key=lambda e: e.name):
        if not entry.is_dir():
            continue
        row = {"folder": entry.name, "name": "", "uid": "",
               "version": "", "author": "", "has_manifest": "否"}
        mpath = os.path.join(entry.path, "manifest.json")
        if os.path.isfile(mpath):
            try:
                with io.open(mpath, encoding="utf-8-sig") as f:
                    raw = f.read()
                try:
                    m = json.loads(raw)
                except json.JSONDecodeError:
                    m = _loose_json(raw)
                row["name"] = m.get("Name", "")
                row["uid"] = m.get("UniqueID", "")
                row["version"] = str(m.get("Version", ""))
                row["author"] = m.get("Author", "")
                row["has_manifest"] = "是"
            except Exception as exc:
                row["name"] = "(manifest 解析失败: %s)" % exc
        if not row["name"]:
            row["name"] = entry.name
        rows.append(row)
    return rows


def gen_manifest_csv(rows):
    with io.open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["文件夹", "模组名", "UniqueID", "版本", "作者", "有manifest"])
        for r in rows:
            w.writerow([r["folder"], r["name"], r["uid"],
                        r["version"], r["author"], r["has_manifest"]])
    print("清单已生成: %s（%d 个文件夹）" % (CSV_PATH, len(rows)))


def smapi_load_text():
    """从 SMAPI 日志提取加载口径；失败则返回占位说明。"""
    try:
        with io.open(SMAPI_LOG, encoding="utf-8", errors="replace") as f:
            t = f.read()
    except OSError:
        return "（以 SMAPI 启动日志为准）"
    loaded = re.search(r"Loaded (\d+) mods", t)
    total = re.search(r"Checking for updates to (\d+) mods", t)
    if loaded and total:
        packs = int(total.group(1)) - int(loaded.group(1))
        return "%s 个 mod + %d 个内容包（共 %s 项）" % (
            loaded.group(1), packs, total.group(1))
    return "（以 SMAPI 启动日志为准）"


def author_list(rows):
    lines = []
    for r in rows:
        if r["author"]:
            lines.append("%s —— %s" % (r["folder"], r["author"]))
        else:
            lines.append(r["folder"])
    return "\r\n".join(lines)


def render(text, mapping):
    for key, val in mapping.items():
        text = text.replace("{{%s}}" % key, val)
    leftover = re.findall(r"\{\{(\w+)\}\}", text)
    if leftover:
        print("警告: 未替换的占位符 %s" % leftover, file=sys.stderr)
    return text


def template_mapping(rows):
    return {
        "DIR_COUNT": str(len(rows)),
        "DATE": datetime.date.today().isoformat(),
        "SMAPI_LOAD": smapi_load_text(),
        "AUTHOR_LIST": author_list(rows),
    }


def stage_dir_for(version):
    return os.path.join(STAGE_ROOT, "【星露谷整合包】v%s" % version)


def _rmtree_force(path):
    """删目录树（容错只读文件——Mods 源里有只读项，copytree 会保留属性）。"""
    def clear(func, target, exc):
        os.chmod(target, stat.S_IWRITE)
        func(target)
    shutil.rmtree(path, onexc=clear)


def assemble(version, rows):
    stage = stage_dir_for(version)
    if os.path.isdir(stage):
        _rmtree_force(stage)
    mods_dst = os.path.join(stage, "MODS")
    smapi_dst = os.path.join(stage, os.path.basename(SMAPI_DIR))
    print("复制 Mods -> MODS ...")
    shutil.copytree(MODS_DIR, mods_dst)
    print("复制 SMAPI installer ...")
    shutil.copytree(SMAPI_DIR, smapi_dst)
    mapping = template_mapping(rows)
    print("渲染说明文本 ...")
    for name in sorted(os.listdir(TPL_DIR)):
        src = os.path.join(TPL_DIR, name)
        if not os.path.isfile(src):
            continue
        with io.open(src, encoding="utf-8") as f:
            text = render(f.read(), mapping)
        with io.open(os.path.join(stage, name), "w", encoding="utf-8", newline="") as f:
            f.write(text)
    n_files = sum(len(files) for _, _, files in os.walk(stage))
    size = sum(os.path.getsize(os.path.join(dp, f))
               for dp, _, files in os.walk(stage) for f in files)
    print("stage 完成: %d 个文件, %.1f MB" % (n_files, size / 1048576))
    return stage, n_files


def make_zip(stage, version):
    os.makedirs(OUT_DIR, exist_ok=True)
    zip_path = os.path.join(OUT_DIR, "【星露谷整合包】v%s.zip" % version)
    root_name = os.path.basename(stage)
    t0 = time.time()
    n = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        for dp, dns, fns in os.walk(stage):
            for fn in sorted(fns):
                full = os.path.join(dp, fn)
                arc = os.path.join(root_name, os.path.relpath(full, stage))
                zf.write(full, arc)
                n += 1
    dt = time.time() - t0
    zsize = os.path.getsize(zip_path)
    print("ZIP 写入: %s" % zip_path)
    print("  条目 %d | %.1f MB | 耗时 %.0f 秒" % (n, zsize / 1048576, dt))
    print("校验中 ...")
    with zipfile.ZipFile(zip_path) as zf:
        bad = zf.testzip()
        m = len(zf.infolist())
    if bad:
        raise SystemExit("校验失败，损坏条目: %s" % bad)
    if m != n:
        raise SystemExit("校验失败: stage %d vs zip %d" % (n, m))
    print("校验通过: 条目一致 (%d)，testzip 无损坏" % m)
    return zip_path


def dry_run(version, rows):
    print("=== dry-run 组装计划 ===")
    print("源 Mods : %s （%d 个文件夹）" % (MODS_DIR, len(rows)))
    print("源 SMAPI: %s" % SMAPI_DIR)
    print("模板目录: %s" % TPL_DIR)
    print("stage   : %s" % stage_dir_for(version))
    print("ZIP 输出: %s" % os.path.join(
        OUT_DIR, "【星露谷整合包】v%s.zip" % version))
    print("占位符预览:")
    for k, v in sorted(template_mapping(rows).items()):
        head = v if k != "AUTHOR_LIST" else (
            v.splitlines()[0] + " ... （共 %d 行）" % len(v.splitlines()))
        print("  {{%s}} = %s" % (k, head))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", action="store_true", help="只生成 mod-manifest.csv")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划")
    ap.add_argument("--version", default=DEFAULT_VER, help="发布版本号（默认 %s）" % DEFAULT_VER)
    args = ap.parse_args()

    for p in (MODS_DIR, SMAPI_DIR, TPL_DIR):
        if not os.path.isdir(p):
            raise SystemExit("缺目录: %s" % p)
    rows = scan_mods()
    print("扫描 Mods: %d 个文件夹" % len(rows))

    if args.manifest:
        gen_manifest_csv(rows)
        return
    if args.dry_run:
        dry_run(args.version, rows)
        return
    t0 = time.time()
    stage, _ = assemble(args.version, rows)
    make_zip(stage, args.version)
    print("总耗时 %.0f 秒" % (time.time() - t0))


if __name__ == "__main__":
    main()
