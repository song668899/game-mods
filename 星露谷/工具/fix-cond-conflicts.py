# -*- coding: utf-8 -*-
r"""
fix-cond-conflicts.py —— 2 对条件冲突精确互斥（方案A修正版：跨包 config 用 CMCT Query）
用法：
    python -X utf8 D:\星露谷MOD\工具\fix-cond-conflicts.py           # 执行修复
    python -X utf8 D:\星露谷MOD\工具\fix-cond-conflicts.py --dry-run  # 只预览+断言，不写盘

修法（2026-10-02 修正——直接引用对方 pack 的 config token 会被 CP 忽略：
"token could not be found"，见坑 27；正确语法 = 环境既有实例（女法师）的 CMCT Query）：
    When 键: "Query: '{{Spiderbuttons.CMCT/Config: Girafarig.HB, <config名>}}' = 'false'": true
    （单身汉开关关=config.json 值 "false"（GMCM 小写）→ 本 patch 生效；开关开 → 让路单身汉）
    另：manifest 加 Dependencies（CMCT 必需 + Girafarig.HB 可选，照抄女法师模式）
断言链：宽松可解析 + 逐步反向还原==原文 + 落盘重读一致 + mod-doctor 复验
"""
import os, re, io, sys, shutil, argparse, importlib.util, subprocess

ROOT = r'D:\星露谷MOD'
MODS = os.path.join(ROOT, '游戏', 'Mods')
BACKUP = os.path.join(ROOT, '汉化备份', '2026-10-02-条件冲突修复')
DOCTOR = os.path.join(ROOT, '工具', 'mod-doctor.py')
FIX = os.path.join(ROOT, '工具', 'fix-load-conflicts.py')

HB_UID = 'Girafarig.HB'
CMCT_UID = 'Spiderbuttons.CMCT'
CFG_NAME = 'Lewis should pass a law so the men of the town can be naked'
COND_KEY = "Query: '{{Spiderbuttons.CMCT/Config: %s, %s}}' = 'false'" % (HB_UID, CFG_NAME)
COND_VAL = 'true'
IDEM = 'Spiderbuttons.CMCT/Config: Girafarig.HB'   # 幂等裸子串

# content.json 的 (包目录, 文件, Target, FromFile 含(None=不查))
TASKS = [
    ("【地图美化】DaisyNiko's低饱和度大地", 'content.json', 'Maps/night_market_tilesheet_objects', None),
    ("【成人】淫乱节日", 'content.json', 'Maps/Festivals', 'Festivals-ff.png'),
    ("【成人】淫乱节日", 'content.json', 'Maps/Festivals', 'Festivals-phallic.png'),
]
# manifest.json 加 Dependencies 的包
MANIFESTS = [
    "【地图美化】DaisyNiko's低饱和度大地",
    "【成人】淫乱节日",
]

spec = importlib.util.spec_from_file_location('flc', FIX)
flc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flc)

spec2 = importlib.util.spec_from_file_location('moddoctor', DOCTOR)
doc = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(doc)

def mk_when_line(text, ps):
    """无 When → Action 行后插入 When 块"""
    m = re.search(r'\n([ \t]*)"Action"\s*:\s*"Load"', text[ps:ps + 2400])
    ind = m.group(1) if m else '            '
    ins = '\n%s"When": {\n%s\t"%s": %s\n%s},' % (ind, ind, COND_KEY, COND_VAL, ind)
    return (ps + 1, '', ins)

def mk_merge_when(text, ps, pe):
    """已有 When → '{' 后插入键值行（保留原键）"""
    seg = text[ps:pe]
    wm = re.search(r'"When"\s*:\s*\{', seg)
    at = ps + wm.end()
    m = re.search(r'\n([ \t]*)"', text[at:at + 300])
    ind = m.group(1) if m else '  '
    ins = '\n%s"%s": %s,' % (ind, COND_KEY, COND_VAL)
    return (at, '', ins)

def mk_deps(text):
    """manifest 无 Dependencies → ContentPackFor 前插入依赖数组"""
    m = re.search(r'\n([ \t]*)"ContentPackFor"', text)
    if not m:
        return None
    ind = m.group(1)
    ins = ('\n%s"Dependencies": [\n'
           '%s    { "UniqueID": "%s", "IsRequired": true },\n'
           '%s    { "UniqueID": "%s", "IsRequired": false }\n'
           '%s],' % (ind, ind, CMCT_UID, ind, HB_UID, ind))
    return (m.start(), '', ins)

def find_patch(text, target, ff):
    hits = []
    for pt in flc.find_load_patches(text):
        if target not in [t.strip() for t in flc.target_list(pt['target'])]:
            continue
        seg = text[pt['ps']:pt['pe']]
        if ff and ff not in seg:
            continue
        hits.append(pt)
    if len(hits) != 1:
        print('❌ patch 定位失败: target=%s ff=%s 命中 %d 个' % (target, ff, len(hits)))
        sys.exit(2)
    return hits[0]

def load_raw(path):
    rawb = open(path, 'rb').read()
    if rawb[:2] in (b'\xff\xfe', b'\xfe\xff'):
        print('❌ 非 UTF-8(UTF-16): %s' % path); sys.exit(2)
    has_bom = rawb[:3] == b'\xef\xbb\xbf'
    return rawb.decode('utf-8-sig' if has_bom else 'utf-8'), has_bom

def save_raw(path, orig, text, steps, rel):
    """断言链 + 备份 + 落盘重读；dry-run 时只断言"""
    try:
        __import__('json').loads(doc.strip_loose(text))
    except Exception as e:
        print('  ❌ 宽松解析断言失败 %s: %s' % (rel, e)); sys.exit(3)
    rev = text
    for (start, old, new, old_actual) in reversed(steps):
        if rev[start:start + len(new)] != new:
            print('  ❌ 反向断言(段不匹配) %s' % rel); sys.exit(3)
        rev = rev[:start] + old_actual + rev[start + len(new):]
    if rev != orig:
        print('  ❌ 反向还原 != 原文 %s' % rel); sys.exit(3)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    opt = ap.parse_args()

    print('=== fix-cond-conflicts（CMCT Query 精确互斥: %s = false）===' % CFG_NAME)

    # ---------- 1) content.json 的 When ----------
    by_file = {}
    for pkg, fname, target, ff in TASKS:
        by_file.setdefault((pkg, fname), []).append((target, ff))
    total_ins = total_idem = 0
    backed_up = set()
    for (pkg, fname), items in by_file.items():
        path = os.path.join(MODS, pkg, fname)
        if not os.path.exists(path):
            print('❌ 文件不存在: %s' % path); sys.exit(2)
        orig, has_bom = load_raw(path)
        text = orig
        steps = []
        print('\n▶ %s\\%s' % (pkg, fname))
        for target, ff in items:
            pt = find_patch(text, target, ff)
            seg = text[pt['ps']:pt['pe']]
            if IDEM in seg:
                print('  ⏭ 已含 Query（幂等）: %s %s' % (target, ff or ''))
                total_idem += 1
                continue
            if pt['when']:
                start, old, new = mk_merge_when(text, pt['ps'], pt['pe'])
            else:
                start, old, new = mk_when_line(text, pt['ps'])
            steps.append((start, old, new, text[start:start + len(old)]))
            text = text[:start] + new + text[start + len(old):]
            total_ins += 1
            print('  ✅ 插入 Query When（%s）: %s' % ('合并' if pt['when'] else '新建', target))
        if steps:
            save_raw(path, orig, text, steps, os.path.relpath(path, MODS))
            print('  断言链 OK（%d 处插入）' % len(steps))
            if not opt.dry_run:
                rel = os.path.relpath(path, MODS)
                if rel not in backed_up:
                    dst = os.path.join(BACKUP, rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(path, dst)   # 原文已回滚，备份=当前=原文
                    backed_up.add(rel)
                out = text.encode('utf-8')
                if has_bom:
                    out = b'\xef\xbb\xbf' + out
                with open(path, 'wb') as f:
                    f.write(out)
                if open(path, 'rb').read() != out:
                    print('  ❌ 落盘重读不一致'); sys.exit(4)
                print('  落盘 OK')

    # ---------- 2) manifest.json 的 Dependencies ----------
    man_ins = man_idem = 0
    for pkg in MANIFESTS:
        path = os.path.join(MODS, pkg, 'manifest.json')
        orig, has_bom = load_raw(path)
        rel = os.path.relpath(path, MODS)
        print('\n▶ %s\\manifest.json' % pkg)
        if HB_UID in orig and CMCT_UID in orig:
            print('  ⏭ Dependencies 已含（幂等）'); man_idem += 1
            continue
        r = mk_deps(orig)
        if r is None:
            print('  ❌ 找不到 ContentPackFor'); sys.exit(2)
        start, old, new = r
        text = orig[:start] + new + orig[start + len(old):]
        if not save_raw(path, orig, text, [(start, old, new, orig[start:start + len(old)])], rel):
            sys.exit(3)
        man_ins += 1
        print('  ✅ 插入 Dependencies（CMCT + Girafarig.HB），断言链 OK')
        if not opt.dry_run:
            if rel not in backed_up:
                dst = os.path.join(BACKUP, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(path, dst)
                backed_up.add(rel)
            with open(path, 'wb') as f:
                f.write(text.encode('utf-8'))
            if open(path, 'rb').read() != text.encode('utf-8'):
                print('  ❌ 落盘重读不一致'); sys.exit(4)
            print('  落盘 OK')

    print('\n汇总: When 插入 %d | manifest 插入 %d | 幂等跳过 %d | 备份 %d 文件' % (
        total_ins, man_ins, total_idem + man_idem, len(backed_up)))
    if opt.dry_run:
        print('（dry-run，未写盘）'); return

    print('\n复验 mod-doctor --only load ...')
    r = subprocess.run([sys.executable, '-X', 'utf8', DOCTOR, '--only', 'load', '--limit', '40'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    print((r.stdout or '')[-5000:])
    if r.returncode not in (0, 1):
        print('doctor 异常: %s' % (r.stderr or '')[:800])
    print('doctor exit=%d' % r.returncode)

if __name__ == '__main__':
    main()
