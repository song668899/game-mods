# -*- coding: utf-8 -*-
r"""
mod-doctor.py —— 整合包一键体检
用法：
    python -X utf8 D:\星露谷MOD\工具\mod-doctor.py
    python -X utf8 D:\星露谷MOD\工具\mod-doctor.py --only load,i18n
    python -X utf8 D:\星露谷MOD\工具\mod-doctor.py --skip links

检查项：
    load   Content Patcher 两包 Load 同一资源（同资源两 Load = Exclusive 都不生效退回原版）
           分级：恒冲突 ERROR（两方都无 When）/ 条件冲突 WARN（至少一方带 When）
           / 已互斥 ✅（一方 When 含对方 UniqueID 的 HasMod|contains=false 守卫，不计 WARN）
           注：资源按需加载，未被请求的资源不触发、日志也不报
    i18n   i18n 缺键 / 大小写撞键 / 值仍是英文（豁免 URL、$token、{{i18n}} 占位）
    json   宽松解析=对齐 Newtonsoft/CP 容忍集（注释/尾逗号/孤立逗号/裸键/单引号/前导小数/
           裸tab/UTF-16 均救；缺冒号/缺逗号/结构残缺=真坏 WARN，Newtonsoft 同样 FAIL 已实证）
    links  文档 MD 本地链接断链（豁免规则文档内示例链接）

退出码：有 ERROR → 1，否则 0
"""
import os, re, io, sys, json, time, argparse, collections

ROOT = r'D:\星露谷MOD'
MODS = os.path.join(ROOT, '游戏', 'Mods')
DOCS = os.path.join(ROOT, '文档')

# ---------- 宽松 JSON 清理（Newtonsoft/SMAPI 方言级） ----------
# 顺序即状态：字符串分支在引号处整段吞掉（含内部 //）；注释分支在 /* 或 // 处整段吞掉（含内部引号）
_TOK_RE = re.compile(
    r'"(?:[^"\\]|\\.)*"'
    r"|'(?:[^'\\]|\\.)*'"          # 单引号字符串（Newtonsoft 方言）
    r'|/\*.*?\*/'
    r'|//[^\n]*', re.S)
_BAREKEY_RE = re.compile(r'([{\[,]\s*)([A-Za-z_$][\w$.\-]*|\d+)(\s*):')  # 裸键名
_TAIL_RE = re.compile(r',(\s*[}\]])')
_LEADING_DOT_RE = re.compile(r'(:\s*)\.(\d)')                              # 前导小数 .03 → 0.03
_UNCLOSED_BLOCK_RE = re.compile(r'/\*[\s\S]*$')
_PLACEHOLDER_RE = re.compile(r'\x00(\d+)\x00')
_CTRL_RE = re.compile(r'[\x00-\x1f]')  # 字符串内控制字符（含 tab/LF/CR）→ \u 转义

def strip_loose(text):
    keep = []
    def repl(m):
        s = m.group(0)
        if s[0] == '"':
            body = _CTRL_RE.sub(lambda x: '\\u%04x' % ord(x.group(0)), s)
            keep.append(body)
            return '\x00%d\x00' % (len(keep) - 1)
        if s[0] == "'":
            inner = s[1:-1].replace('"', '\\"')
            inner = _CTRL_RE.sub(lambda x: '\\u%04x' % ord(x.group(0)), inner)
            keep.append('"%s"' % inner)
            return '\x00%d\x00' % (len(keep) - 1)
        return ''
    text = _TOK_RE.sub(repl, text)
    if '/*' in text:
        text = _UNCLOSED_BLOCK_RE.sub('', text)
    text = re.sub(r',(\s*,)', r'\1', text)          # 孤立/双逗号（Newtonsoft 容忍，json 不容）
    text = _BAREKEY_RE.sub(r'\1"\2"\3:', text)   # 注意：冒号必须带在替换串里
    text = _LEADING_DOT_RE.sub(r'\g<1>0.\2', text)
    text = _TAIL_RE.sub(r'\1', text)
    return _PLACEHOLDER_RE.sub(lambda m: keep[int(m.group(1))], text)

def decode_raw(path):
    b = open(path, 'rb').read()
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return b.decode('utf-16')     # UTF-16（SMAPI 允许）
    try:
        return b.decode('utf-8-sig')
    except UnicodeDecodeError:
        return b.decode('utf-8', errors='replace')

def load_json(path):
    """返回 (obj, strict_ok, loose_ok)；都失败 obj=None"""
    try:
        raw = decode_raw(path)
    except Exception:
        return None, False, False
    try:
        return json.loads(raw), True, True
    except Exception:
        try:
            return json.loads(strip_loose(raw)), False, True
        except Exception:
            return None, False, False

# ---------- 收集全部 json ----------
def iter_json_files(base):
    for dirpath, dirs, files in os.walk(base):
        for f in files:
            if f.endswith('.json'):
                yield os.path.join(dirpath, f)

# ---------- 检查 1：Load 冲突（按包对聚合 + 恒/条件分级） ----------
def _when_excl(w):
    """解析 When 里的互斥条件：'HasMod |contains=A, B': false → {A, B}（对方装了就不生效）。"""
    uids = set()
    if isinstance(w, dict):
        for k, v in w.items():
            m = re.match(r'HasMod\s*\|\s*contains\s*=\s*(.*)$', str(k).strip(), re.I)
            if m and v is False:
                for u in str(m.group(1)).split(','):
                    u = u.strip()
                    if u:
                        uids.add(u)
    return uids

def _val_exclusive(wa_list, wb_list, pack_a, pack_b, uid_owner):
    """值互斥：两包在该 target 的所有 patch 组合都存在「同义条件同键不同值」→ 永不同时生效。
    When=AND 语义；条件同义包含：
    - 同裸键（全局 token 如 Spouse/Day，或同名 config）：'Lewis': True vs False
    - 跨包 config：裸键 <name> vs Query: '{{Spiderbuttons.CMCT/Config: <uid>, <name>}}' = '<v>'
      （Query 的 uid 反查归属包后与对方包名匹配；坑 27）
    值比较 casefold（GMCM 写小写 'false'，manifest Default 是 'False'）。"""
    QRE = re.compile(r"^Query:\s*'\{\{\s*Spiderbuttons\.CMCT/Config:\s*([^,]+?),\s*(.+?)\s*\}\}'\s*=\s*'(.*)'\s*$")
    def norm(w):
        out = {}
        if not isinstance(w, dict):
            return None
        for k, v in w.items():
            s = str(k).strip()
            m = QRE.match(s)
            if m:
                if str(v).strip().casefold() == 'false':
                    continue   # 期望表达式不成立才应用 → 语义非字面值，保守排除
                out[(uid_owner.get(m.group(1).strip(), m.group(1).strip()), m.group(2).strip())] = \
                    m.group(3).strip().casefold()
            else:
                out[(None, s)] = str(v).strip().casefold()
        return out
    def same(k1, k2):
        (s1, n1), (s2, n2) = k1, k2
        if n1 != n2:
            return False
        if s1 == s2:
            return True
        return s1 == pack_b or s2 == pack_a   # Query 归属 == 对方包
    for wa in (wa_list or [None]):
        for wb in (wb_list or [None]):
            na, nb = norm(wa), norm(wb)
            if not na or not nb:
                return False   # 存在无条件 patch → 可同时生效
            if not any(same(ka, kb) and va != vb for ka, va in na.items()
                       for kb, vb in nb.items()):
                return False
    return True

def build_pack_uids():
    """顶层包目录 -> 其下所有 manifest 的 UniqueID 集合（manifest 普遍宽松 JSON，用宽松解析）。"""
    uids = collections.defaultdict(set)
    for dirpath, dirs, files in os.walk(MODS):
        if 'manifest.json' not in files:
            continue
        top = os.path.relpath(dirpath, MODS).split(os.sep)[0]
        d, _, _ = load_json(os.path.join(dirpath, 'manifest.json'))
        if isinstance(d, dict) and d.get('UniqueID'):
            uids[top].add(d['UniqueID'])
    return uids

def check_load(all_objs):
    # (target, pack) -> has_when ; target -> {pack: has_when} ; target -> {pack: [When dict,...]}
    loads = collections.defaultdict(dict)
    guards = collections.defaultdict(lambda: collections.defaultdict(set))  # target -> pack -> 互斥UID集
    whens = collections.defaultdict(lambda: collections.defaultdict(list))  # target -> pack -> [When...]
    pack_uids = build_pack_uids()
    for path, obj in all_objs:
        if obj is None:
            continue
        pack = os.path.relpath(path, MODS).split(os.sep)[0]
        def walk(node):
            if isinstance(node, dict):
                if node.get('Action') == 'Load':
                    tgt = node.get('Target')
                    whn = node.get('When')
                    when = bool(whn)
                    ex = _when_excl(whn)
                    if isinstance(tgt, str):
                        for t in tgt.split(','):
                            t = t.strip()
                            if t:
                                loads[t][pack] = loads[t].get(pack, False) or when
                                if ex:
                                    guards[t][pack] |= ex
                                whens[t][pack].append(whn if isinstance(whn, dict) else None)
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
        walk(obj)
    # 按包对聚合：mutex=互斥When已消解 / conditional=条件冲突 / always=恒冲突
    uid_owner = {}
    for pk_, us in pack_uids.items():
        for u in us:
            uid_owner[u] = pk_
    pairs = collections.defaultdict(lambda: {'always': [], 'conditional': [], 'mutex': []})
    for tgt, pk in loads.items():
        if len(pk) < 2:
            continue
        pack_list = sorted(pk)
        for i in range(len(pack_list)):
            for j in range(i + 1, len(pack_list)):
                a, b = pack_list[i], pack_list[j]
                ga, gb = guards[tgt].get(a, set()), guards[tgt].get(b, set())
                if (ga & pack_uids.get(b, set())) or (gb & pack_uids.get(a, set())):
                    pairs[(a, b)]['mutex'].append(tgt)
                elif _val_exclusive(whens[tgt].get(a), whens[tgt].get(b), a, b, uid_owner):
                    pairs[(a, b)]['mutex'].append(tgt)
                elif pk[a] or pk[b]:
                    pairs[(a, b)]['conditional'].append(tgt)
                else:
                    pairs[(a, b)]['always'].append(tgt)
    return pairs

# ---------- 检查 2：i18n ----------
EN_RE = re.compile(r'[A-Za-z]')
# 有意保留英文的键（内部标识/虚构语言/专名，2026-10-02 逐键判定）
INTENTIONAL = {
    ('ZoomLevel', 'pages.keybinds.id'),            # 页面内部标识（界面标题已汉化）
    ('ZoomLevel', 'pages.values.id'),
    ('ZoomLevel', 'pages.miscellaneous.id'),
    ('ZoomLevel', 'pages.randomizer.id'),
    ('【功能】钓鱼助手 2', 'config-menu.title.hud'),          # HUD 缩写
    ('【NPC】地质学家', '55990004.05'),                       # 虚构语言剧情文本
    ('【大型拓展-ES附加】影子人', 'Core.Music.Underscarp'),   # 曲名+作者
    ('【大型拓展-ES附加】影子人', 'Rand.SenS.Book.Author2.1'),  # 作者名 Dest T.
    ('【大型拓展-ES附加】影子人', 'Rand.SenS.Book.Author2.4'),  # 作者名 PS. Child
    ('【大型拓展-ES附加】熊家', 'Sigurd.Random.Marriage.HorrorMovies.3'),  # 名号 BR14N
    ('【图块集】Lumisteria 图块集-室内', 'config.InteriorOption.values.ATDSV'),   # 选项值
    ('【图块集】Lumisteria 图块集-室内', 'config.InteriorOption.values.grapeponta'),
    ('【图块集】Lumisteria 图块集-室内', 'config.InteriorOption.values.starblue'),
}
def _untranslated(v):
    if not isinstance(v, str) or not EN_RE.search(v):
        return False
    if v.startswith(('http://', 'https://')):
        return False
    if re.fullmatch(r'\$[a-zA-Z0-9_{}#b#@~]+', v):   # $b #x @ 等 token
        return False
    if re.fullmatch(r'[\W\d_]+', v):                  # 纯符号数字
        return False
    if '{{' in v:
        return False
    if re.search(r'[一-鿿]', v):               # 含中文（如 'HUD位置'）
        return False
    if "''" in v:                                      # RSV 配偶名单 "Anton ''"
        return False
    if re.match(r'\s*(\$[A-Za-z]|/)', v):              # 事件命令 $v … / /shake …
        return False
    if re.fullmatch(r'\d[\d,.]*\s*g', v):              # 金额 2,500g
        return False
    if re.fullmatch(r'[zZ]{3,}', v):                   # 打鼾 ZZZZZ
        return False
    # 剥离 token 后无英文字母 → 纯标点/符号（'...$11#$b#...'、'{Greeting}'）
    bare = re.sub(r'\$[\w{}#b#@~]+|#[\w{}$b#@~]*#|\{[^}]*\}|%[A-Za-z][\w ]*|\^\w+|~\w+|@\w+|/[A-Za-z][\w/]*', '', v)
    if not EN_RE.search(bare):
        return False
    return True

def check_i18n():
    missing, clash, untranslated, no_zh, broken_zh = [], [], [], [], []
    for dirpath, dirs, files in os.walk(MODS):
        if os.path.basename(dirpath).lower() != 'i18n':
            continue
        if 'default.json' not in files:
            continue
        pack = os.path.relpath(dirpath, MODS).split(os.sep)[0]
        d, _, _ = load_json(os.path.join(dirpath, 'default.json'))
        if not isinstance(d, dict):
            continue
        if 'zh.json' not in files:
            no_zh.append(pack)
            continue
        z, _, zok = load_json(os.path.join(dirpath, 'zh.json'))
        if not isinstance(z, dict):
            broken_zh.append(pack)
            continue
        miss = sorted(set(d) - set(z))
        if miss:
            missing.append((pack, ', '.join(miss[:5]), len(miss)))
        low = collections.defaultdict(list)
        for k in z:
            low[k.lower()].append(k)
        for lk, ks in low.items():
            if len(ks) > 1:
                clash.append((pack, ' | '.join(sorted(ks))))
        cnt = 0
        samples = []
        for k, v in z.items():
            ov = d.get(k)
            if (isinstance(v, str) and isinstance(ov, str) and v == ov
                    and k != v and (pack, k) not in INTENTIONAL and _untranslated(v)):
                cnt += 1
                if len(samples) < 3:
                    samples.append(k)
        if cnt:
            untranslated.append((pack, cnt, ', '.join(samples)))
    return missing, clash, untranslated, no_zh, broken_zh

# ---------- 检查 3：JSON 严格解析 ----------
def _in_comment(text, pos):
    """字符串感知状态机：text[pos] 是否落在注释内（块/行注释）"""
    i, n, in_str, esc, depth = 0, len(text), False, False, 0
    line_comment = False
    while i < pos and i < n:
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if line_comment:
            if c == '\n':
                line_comment = False
            i += 1
            continue
        if c == '"':
            in_str = True
            i += 1
        elif text.startswith('/*', i):
            depth += 1
            i += 2
        elif text.startswith('*/', i):
            depth = max(0, depth - 1)
            i += 2
        elif text.startswith('//', i):
            line_comment = True
            i += 2
        else:
            i += 1
    if depth > 0 or line_comment:
        return True
    # pos 可能正好落在注释起点上
    return text.startswith('/*', pos) or text.startswith('//', pos)

def check_json(all_results):
    loose_ok, broken = [], []
    for path, strict_ok, ok in all_results:
        rel = os.path.relpath(path, MODS)
        if strict_ok:
            continue
        (loose_ok if ok else broken).append(rel)
    # include 引用线索：坏文件名（带扩展）出现在 content/manifest 中，且命中位置不在注释内
    entries = []
    for p in iter_json_files(MODS):
        bn = os.path.basename(p).lower()
        if bn == 'content.json' or bn == 'manifest.json':
            try:
                entries.append(io.open(p, encoding='utf-8-sig', errors='replace').read().lower())
            except Exception:
                pass
    referenced = []
    for rel in broken:
        stem = os.path.basename(rel).lower()
        hit = False
        for text in entries:
            pos = text.find(stem)
            while pos >= 0:
                if not _in_comment(text, pos):
                    hit = True
                    break
                pos = text.find(stem, pos + 1)
            if hit:
                break
        referenced.append((rel, hit))
    return loose_ok, referenced

# ---------- 日志基线 ----------
def log_baseline():
    """返回 (n_error, n_warn, first_error_line) 或 None。格式: [14:09:55 ERROR game] ..."""
    p = os.path.expandvars(r'%APPDATA%\StardewValley\ErrorLogs\SMAPI-latest.txt')
    if not os.path.exists(p):
        return None
    try:
        t = io.open(p, encoding='utf-8', errors='replace').read()
    except Exception:
        return None
    errs = re.findall(r'^\[\d\d:\d\d:\d\d ERROR[^\n]*', t, re.M)
    warns = len(re.findall(r'^\[\d\d:\d\d:\d\d WARN', t, re.M))
    first = errs[0] if errs else None
    return len(errs), warns, first

# ---------- 检查 4：文档断链 ----------
LINK_EXEMPT = {('MD更新规则.md', '文件名.md')}  # 规则文档内示例链接（已知假阳性）
def check_links():
    bad = []
    files = []
    if os.path.isdir(DOCS):
        files += [os.path.join(DOCS, f) for f in os.listdir(DOCS) if f.endswith('.md')]
    readme = os.path.join(ROOT, 'README.md')
    if os.path.exists(readme):
        files.append(readme)
    for f in sorted(files):
        try:
            t = io.open(f, encoding='utf-8').read()
        except Exception:
            continue
        for _, h in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', t):
            if h.startswith(('http', '#')) or '://' in h:
                continue
            if (os.path.basename(f), h) in LINK_EXEMPT:
                continue
            if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), h))):
                bad.append((os.path.relpath(f, ROOT), h))
    return bad, len(files)

# ---------- 主流程 ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='', help='load,i18n,json,links')
    ap.add_argument('--skip', default='', help='load,i18n,json,links')
    ap.add_argument('--limit', type=int, default=5, help='每项明细最多显示条数')
    opt = ap.parse_args()
    all_checks = ['load', 'i18n', 'json', 'links']
    sel = set(x.strip() for x in opt.only.split(',') if x.strip()) or set(all_checks)
    sel -= set(x.strip() for x in opt.skip.split(',') if x.strip())

    t0 = time.time()
    errors, warns = 0, 0
    print('=== 整合包体检 mod-doctor ===')
    print('Mods: %s' % MODS)
    base = log_baseline()
    if base is not None:
        n_err, n_warn, first = base
        print('日志基线: ERROR x%d | WARN x%d（最近一次启动）' % (n_err, n_warn))
        if first:
            print('          首条 ERROR: %s' % first[:160])

    all_results, all_objs = [], []
    n = 0
    for p in iter_json_files(MODS):
        obj, strict_ok, loose_ok = load_json(p)
        all_results.append((p, strict_ok, loose_ok))
        if obj is not None:
            all_objs.append((p, obj))
        n += 1
        if n % 200 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
    print(' [%d json]' % n)

    if 'load' in sel:
        pairs = check_load(all_objs)
        # 去重：同一资源在同对里只算一次
        n_always_d = len(set(t for v in pairs.values() for t in v['always']))
        n_cond_d = len(set(t for v in pairs.values() for t in v['conditional']))
        n_mutex_d = len(set(t for v in pairs.values() for t in v['mutex']))
        if n_always_d:
            n_pairs_err = sum(1 for v in pairs.values() if v['always'])
            errors += n_pairs_err
            print('[load]   ❌ 恒冲突 %d 资源（无 When，资源一被请求即触发）/ 涉 %d 包对' % (n_always_d, n_pairs_err))
        else:
            print('[load]   ✅ 无恒冲突')
        if n_cond_d:
            n_pairs_warn = sum(1 for v in pairs.values() if not v['always'] and v['conditional'])
            warns += n_pairs_warn
            print('[load]   ⚠️ 条件冲突 %d 资源（带 When，条件同时满足才触发，涉 %d 包对）' % (n_cond_d, n_pairs_warn))
        if n_mutex_d:
            n_pairs_mutex = sum(1 for v in pairs.values() if v['mutex'])
            print('[load]   ✅ 已互斥 %d 资源（HasMod=false 守卫已消解双 Load，涉 %d 包对，不计警告）' % (n_mutex_d, n_pairs_mutex))
        # 按包对聚合输出（恒冲突 > 条件冲突 > 仅互斥，互斥沉底）
        sorted_pairs = sorted(pairs.items(),
                              key=lambda kv: -(len(kv[1]['always']) * 1000 + len(kv[1]['conditional'])))
        shown = 0
        for (a, b), v in sorted_pairs:
            if shown >= opt.limit:
                break
            tag = '恒%d/条%d/互%d' % (len(v['always']), len(v['conditional']), len(v['mutex']))
            if v['always']:
                errs_here = '❌'
            elif v['conditional']:
                errs_here = '⚠️'
            else:
                errs_here = '✅'
            print('         %s %s × %s（%s 资源）' % (errs_here, a, b, tag))
            for t in sorted(v['always'])[:2]:
                print('              %s' % t)
            shown += 1
        if len(pairs) > opt.limit:
            print('         ... 另 %d 包对' % (len(pairs) - opt.limit))
        print('         （注：资源按需加载，未请求不触发；日志 0 次 ≠ 无冲突）')

    if 'i18n' in sel:
        miss, clash, untr, no_zh, broken_zh = check_i18n()
        parts = []
        if miss:
            errors += len(miss)
            parts.append('缺键 ❌%d包' % len(miss))
        else:
            parts.append('缺键✅')
        if clash:
            errors += len(clash)
            parts.append('撞键 ❌%d包' % len(clash))
        else:
            parts.append('撞键✅')
        n_untr = sum(c for _, c, _ in untr)
        if n_untr:
            warns += len(untr)
            parts.append('未翻 ⚠️%d键' % n_untr)
        else:
            parts.append('未翻✅')
        if broken_zh:
            warns += len(broken_zh)
            parts.append('zh解析失败 ⚠️%d包' % len(broken_zh))
        parts.append('无zh %d包' % len(no_zh))
        print('[i18n]   %s' % ' | '.join(parts))
        for pack in broken_zh:
            print('         zh解析失败 %s' % pack)
        for pack, keys, cnt in miss[:opt.limit]:
            print('         缺键 %s: %d 个（%s…）' % (pack, cnt, keys))
        for pack, ks in clash[:opt.limit]:
            print('         撞键 %s: %s' % (pack, ks))
        for pack, cnt, samples in untr[:opt.limit]:
            print('         未翻 %s: %d 键（如 %s…）' % (pack, cnt, samples))
        if len(untr) > opt.limit:
            print('         ... 另 %d 包未翻' % (len(untr) - opt.limit))

    if 'json' in sel:
        loose_ok, broken = check_json(all_results)
        if broken:
            warns += len(broken)
            n_ref = sum(1 for _, hit in broken if hit)
            print('[json]   ⚠️ 语法坏文件 %d 个（字面被引用 %d）| 宽松可救 %d 个（注释/尾逗号，正常）'
                  % (len(broken), n_ref, len(loose_ok)))
            print('         （实证：日志中无 CP/SMAPI JSON 解析类 ERROR = 这些坏文件当前未被加载）')
            for rel, hit in broken[:opt.limit]:
                print('         坏: %s%s' % (rel, '  [content 字面引用]' if hit else '  [未见字面引用]'))
            if len(broken) > opt.limit:
                print('         ... 另 %d 个' % (len(broken) - opt.limit))
        else:
            print('[json]   ✅ 无语法坏文件 | 宽松可救 %d 个（注释/尾逗号，正常）' % len(loose_ok))

    if 'links' in sel:
        bad, n_files = check_links()
        if bad:
            errors += len(bad)
            print('[links]  ❌ 断链 %d 条 / %d 文件' % (len(bad), n_files))
            for f, h in bad[:opt.limit]:
                print('         %s -> %s' % (f, h))
        else:
            print('[links]  ✅ 全部有效（%d 文件，已豁免规则文档示例）' % n_files)

    dt = time.time() - t0
    verdict = '发现 ERROR，需处理 ❌' if errors else ('仅警告 ⚠️' if warns else '全绿 ✅')
    print('---')
    print('汇总: ERROR %d | WARN %d | 耗时 %.1fs → %s' % (errors, warns, dt, verdict))
    sys.exit(1 if errors else 0)

if __name__ == '__main__':
    main()
