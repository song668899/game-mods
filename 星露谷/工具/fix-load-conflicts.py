# -*- coding: utf-8 -*-
r"""
fix-load-conflicts.py —— 9 对 Load 恒冲突修复（互斥让路）
用法：
    python -X utf8 D:\星露谷MOD\工具\fix-load-conflicts.py           # 执行修复
    python -X utf8 D:\星露谷MOD\工具\fix-load-conflicts.py --dry-run  # 只预览+断言，不写盘

策略（幂等可重跑；mod 更新还原后重新执行即可）：
    纯冲突 patch（Target 全是冲突资源） → 加 "When": { "HasMod |contains=<生效方UID>": false }
    混合 patch（冲突+非冲突）           → 从 Target 移除冲突项（保非冲突项继续生效）
    移除后 Target 为空                  → 回退 When 互斥
断言链：宽松可解析 + 逐步反向还原==原文 + 落盘重读一致 + mod-doctor 复验归零
"""
import os, re, io, sys, json, glob, shutil, argparse, importlib.util, subprocess

ROOT = r'D:\星露谷MOD'
MODS = os.path.join(ROOT, '游戏', 'Mods')
BACKUP = os.path.join(ROOT, '汉化备份', '2026-10-02-Load冲突修复')
DOCTOR = os.path.join(ROOT, '工具', 'mod-doctor.py')

# (让路方, 生效方, 生效方UniqueID) —— 用户已拍板：#5 SVE 生效 / #8 Avian 生效 / 其余按推荐
TASKS = [
    ('【大型拓展】RSV',             '【立绘】季节性立绘-师爷改装版-RSV',      'Rafseazz.RSVSeasonalOutfits'),
    ('【大型拓展】SVE',             '【立绘】季节性立绘-师爷改装版-SVE',      'Poltergeister.SeasonalCuteSpritesSVE'),
    ('【立绘】Avian风格-ES',        '【大型拓展-ES附加】科幻作家',            'TheFrenchDodo.RodneyOBrien'),
    ('【大型拓展】SVE',             '【NPC-女法师附加】浪漫关系解锁-SVE兼容',  'Parrot.RomRas'),
    ('【大型拓展】ES',              '【大型拓展】SVE',                        'FlashShifter.SVECode'),
    ('【大型拓展】X露谷',           '【NPC】女法师',                          'Nom0ri.RomRas'),
    ('【大型拓展】ES',              '【NPC】流放者朱丽叶',                    'LemurKat.JulietHouse.NPC'),
    ('【大型拓展-ES附加】爬虫学家',  '【立绘】Avian风格-ES',                   'AvianRPG.FECharacterPortraitsEastScarp'),
    ('【大型拓展】X露谷',           '【大型拓展-X附加】X拓展',                'metakage.XtardewValley'),
]

spec = importlib.util.spec_from_file_location('moddoctor', DOCTOR)
doc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doc)

def pack_conflicts():
    all_objs = []
    for p in doc.iter_json_files(MODS):
        obj, _, _ = doc.load_json(p)
        if obj is not None:
            all_objs.append((p, obj))
    pairs = doc.check_load(all_objs)
    return {frozenset((a, b)): set(v['always']) for (a, b), v in pairs.items() if v['always']}

# ---------- 双表：skip=字符串或注释（结构定位跳过）；cmt=仅注释（判断匹配是否被注释掉） ----------
def build_mask(text):
    n = len(text)
    skip = [False] * n
    cmt = [False] * n
    i = 0
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1; esc = False
            while j < n:
                cj = text[j]
                if esc: esc = False
                elif cj == '\\': esc = True
                elif cj == '"': j += 1; break
                j += 1
            for k in range(i, min(j, n)): skip[k] = True
            i = j
        elif text.startswith('//', i):
            j = text.find('\n', i); j = n if j < 0 else j
            for k in range(i, j): skip[k] = True; cmt[k] = True
            i = j
        elif text.startswith('/*', i):
            j = text.find('*/', i + 2); j = n if j < 0 else j + 2
            for k in range(i, min(j, n)): skip[k] = True; cmt[k] = True
            i = j
        else:
            i += 1
    return skip, cmt

def skip_string(text, i):
    n = len(text); i += 1; esc = False
    while i < n:
        c = text[i]
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': return i + 1
        i += 1
    return n

def find_patch_start(text, mask, pos):
    """Action 位置向前：非mask配对回溯找 patch 的 '{'"""
    depth = 0
    for i in range(pos - 1, -1, -1):
        if mask[i]: continue
        c = text[i]
        if c == '}': depth += 1
        elif c == '{':
            if depth == 0: return i
            depth -= 1
    return -1

def match_brace(text, mask, start):
    depth = 0
    for i in range(start, len(text)):
        if mask[i]: continue
        c = text[i]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return i + 1
    return -1

def find_load_patches(text):
    skip, cmt = build_mask(text)
    out = []
    for m in re.finditer(r'"Action"\s*:\s*"Load"', text):
        if cmt[m.start()]:   # 在注释内（被注释掉的 patch），跳过
            continue
        ps = find_patch_start(text, skip, m.start())
        if ps < 0: continue
        pe = match_brace(text, skip, ps)
        if pe < 0: continue
        seg = text[ps:pe]
        tm = re.search(r'"Target"\s*:\s*"', seg)
        if not tm: continue
        ts = ps + tm.end()          # 值开始（引号后）
        te = skip_string(text, ts - 1) - 1   # 闭合引号位置
        out.append({'ps': ps, 'pe': pe, 'tspan': (ts, te),
                    'target': text[ts:te],
                    'when': bool(re.search(r'"When"\s*:\s*\{', seg))})
    return out

def target_list(t):
    return [x.strip() for x in t.split(',') if x.strip()]

# ---------- 编辑：统一 (start, old, new)，old=被替换原文（插入型为 ''） ----------
def mk_when_line(text, ps, uid):
    m = re.search(r'\n([ \t]*)"Action"\s*:\s*"Load"', text[ps:ps + 2400])
    ind = m.group(1) if m else '            '
    ins = '\n%s"When": { "HasMod |contains=%s": false },' % (ind, uid)
    return (ps + 1, '', ins)

def mk_merge_when(text, ps, pe, uid):
    seg = text[ps:pe]
    wm = re.search(r'"When"\s*:\s*\{', seg)
    at = ps + wm.end()
    m = re.search(r'\n([ \t]*)"', text[at:at + 300])
    ind = m.group(1) if m else '  '
    ins = '\n%s"HasMod |contains=%s": false,' % (ind, uid)
    return (at, '', ins)

# ---------- 主流程 ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    opt = ap.parse_args()

    print('=== fix-load-conflicts ===')
    conflicts = pack_conflicts()
    print('当前恒冲突包对: %d' % len(conflicts))

    # UID 断言
    for _, win, uid in TASKS:
        ok = False
        for mp in glob.glob(os.path.join(MODS, win, '**', 'manifest.json'), recursive=True):
            try:
                if uid in io.open(mp, encoding='utf-8-sig', errors='replace').read():
                    ok = True; break
            except Exception:
                pass
        if not ok:
            print('❌ UID 断言失败: %s ∉ %s' % (uid, win)); sys.exit(2)
    print('UID 断言: 9/9 通过')

    backed_up = set()
    skipped_utf = []
    total_when = total_rm = total_skip = 0

    for lose, win, uid in TASKS:
        key = frozenset((lose, win))
        res = conflicts.get(key)
        if not res:
            print('⚠️ %s × %s 不在当前恒冲突（已修/变化），跳过' % (lose, win))
            continue
        print('\n▶ %s 让路 → %s 生效（%d 资源）' % (lose, win, len(res)))
        for p in doc.iter_json_files(os.path.join(MODS, lose)):
            if os.path.basename(p).lower() == 'manifest.json':
                continue
            rawb = open(p, 'rb').read()
            if rawb[:2] in (b'\xff\xfe', b'\xfe\xff'):
                skipped_utf.append(os.path.relpath(p, MODS)); continue
            if b'"Load"' not in rawb:
                continue
            has_bom = rawb[:3] == b'\xef\xbb\xbf'
            try:
                orig = rawb.decode('utf-8-sig' if has_bom else 'utf-8')
            except UnicodeDecodeError:
                skipped_utf.append(os.path.relpath(p, MODS)); continue

            text = orig
            steps = []   # [(start, old, new, old_actual, kind)] 逐步
            saw_idem = False
            while True:
                hit = None
                for pt in find_load_patches(text):
                    tset = set(target_list(pt['target']))
                    ov = tset & res
                    if not ov:
                        continue
                    seg = text[pt['ps']:pt['pe']]
                    if uid in seg:
                        saw_idem = True   # 幂等：该 patch 已处理（When 或原生含 UID），继续看下一个
                        continue
                    hit = (pt, ov, tset)
                    break
                if hit is None:
                    break
                pt, ov, tset = hit
                if ov == tset:
                    # 纯冲突 → When
                    if pt['when']:
                        start, old, new = mk_merge_when(text, pt['ps'], pt['pe'], uid)
                    else:
                        start, old, new = mk_when_line(text, pt['ps'], uid)
                    new_text = text[:start] + new + text[start + len(old):]
                    steps.append((start, old, new, text[start:start + len(old)], 'when'))
                    text = new_text
                    total_when += 1
                else:
                    keep = [r for r in target_list(pt['target']) if r not in ov]
                    if not keep:
                        start, old, new = mk_when_line(text, pt['ps'], uid)
                        new_text = text[:start] + new + text[start + len(old):]
                        steps.append((start, old, new, '', 'when'))
                        text = new_text
                        total_when += 1
                    else:
                        ts, te = pt['tspan']
                        old = text[ts:te]
                        new = ', '.join(keep)
                        new_text = text[:ts] + new + text[te:]
                        steps.append((ts, old, new, old, 'rm'))
                        text = new_text
                        total_rm += len(ov)
            if not steps:
                if saw_idem:
                    total_skip += 1   # 命中但全部幂等（已修过）
                continue

            # ---- 断言链 ----
            # 1) 宽松可解析
            try:
                json.loads(doc.strip_loose(text))
            except Exception as e:
                print('  ❌ 解析断言失败 %s: %s' % (os.path.relpath(p, MODS), e)); sys.exit(3)
            # 2) 逐步反向还原 == 原文
            rev = text
            for (start, old, new, old_actual, kind) in reversed(steps):
                seg = rev[start:start + len(new)]
                if seg != new:
                    print('  ❌ 反向断言(段不匹配) %s' % os.path.relpath(p, MODS)); sys.exit(3)
                rev = rev[:start] + old_actual + rev[start + len(new):]
            if rev != orig:
                print('  ❌ 反向还原 != 原文 %s' % os.path.relpath(p, MODS)); sys.exit(3)

            rel = os.path.relpath(p, MODS)
            print('  ✅ %s（When %d / 移除项 %d，反向还原 OK）' % (
                rel, sum(1 for s in steps if s[4] == 'when'),
                sum(1 for s in steps if s[4] == 'rm')))

            if opt.dry_run:
                continue
            # 3) 备份（一次）
            if rel not in backed_up:
                dst = os.path.join(BACKUP, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if not os.path.exists(dst):
                    shutil.copy2(p, dst)
                backed_up.add(rel)
            # 4) 落盘（保留 BOM）+ 重读
            out = text.encode('utf-8')
            if has_bom:
                out = b'\xef\xbb\xbf' + out
            with open(p, 'wb') as f:
                f.write(out)
            if open(p, 'rb').read() != out:
                print('  ❌ 落盘重读不一致 %s' % rel); sys.exit(4)

    print('\n汇总: When 互斥 %d | Target 移除冲突项 %d | 幂等跳过 %d | 备份 %d 文件' % (
        total_when, total_rm, total_skip, len(backed_up)))
    if skipped_utf:
        print('跳过(非UTF-8): %s' % skipped_utf)
    if opt.dry_run:
        print('（dry-run，未写盘）'); return

    print('\n复验 mod-doctor --only load ...')
    r = subprocess.run([sys.executable, '-X', 'utf8', DOCTOR, '--only', 'load', '--limit', '30'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    print((r.stdout or '')[-4000:])
    if r.returncode not in (0, 1):
        print('doctor 异常: %s' % (r.stderr or '')[:800])
    print('doctor exit=%d' % r.returncode)

if __name__ == '__main__':
    main()
