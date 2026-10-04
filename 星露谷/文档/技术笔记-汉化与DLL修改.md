# 技术笔记：汉化机制与 DLL 修改

> **动手改任何 MOD 之前必读。** 这里是从实际工作里总结的方法论和踩过的坑。
  > 最后更新：2026-10-04（坑 28「模组 manifest 带注释——标准 JSON 解析必炸，剥 /* */ 与行尾 // 注释+尾逗号再读，本环境 37/152 命中」；同日坑 27 补重启实证：CMCT Query 修正后 0 patch Ignored / 0 ERROR）；2026-10-02 新增坑 27「跨包引用对方 config token → 整个 patch 被 Ignored——用 CMCT Query 条件 + manifest 依赖，启动日志 Ignored 行是唯一权威验证」、坑 26「CP When 值互斥——同键不同值=永不同真，体检判互斥不报冲突；同键相同值不算」、坑 25「未翻判定口径=zh 值与 default 英文完全相同，豁免分层：通则+键=值+显式白名单，只看值含英文会误判 3 万+」、坑 24「SMAPI 日志行格式 `[HH:MM:SS ERROR mod]`——按 `[ERROR]` 检索为 0 ≠ 无 ERROR，基线随启动刷新」、坑 23「CP 互斥 When 写 `HasMod |contains=<UID>': false`，一键两冒号是非法 JSON；幂等用裸子串防死循环」、坑 22「Newtonsoft 容忍集以 .NET 实测为准——孤立逗号/注释/裸键全救，缺冒号/缺逗号才真坏」、坑 21「事件双报错是因果链——changeLocation 拼写损坏留在自定义地图，switchEvent 按当前地图查资产落空」、坑 20「有 i18n ≠ 全汉化——quickQuestion 菜单是事件命令内联参数，不走 i18n，动态提取+断言后直接改事件 JSON」、坑 19「`Can't get audio ID` ERROR——事件 playMusic 短 ID 对不上注册全名，AlternativeTrackIds 不是全局别名」、坑 18「外部生成途径缺 mod 自有初始化——CJB 悬浮剑与魔法空槽枪越界崩菜单，诊断路径与修复候选已记」、坑 16「缺键扫描须大小写不敏感，否则补出重复键」、坑 17「mod 加载期 i18n.Get 英文快照——改 zh 无效，用 MFM content pack 同 Id 覆盖」；同日此前：坑 13「i18n 批量改写的 token parity 与豁免分类」、坑 14「同名 i18n 目录导出互相覆盖」、坑 15「批量替换中途失败的幂等保护」；此前 2026-10-01：坑 9「dnPE 占句柄写不进」、坑 10「截断式测试毁文件」、坑 11「#US 空条目 ln==1」、坑 12「盘点扫调用处漏变量实参标签」，坑 3 补第四次翻车「content.json 大小写漏盘」；第四节补条目级字典法实战与校验清单；第七节新增「Can't apply data patch 类黄字三分支定位法」）

---

## 一、界面英文的三层结构（先定位，再动手）

玩家可见的「英文」分三层，**根因完全不同，修法也不同**：

| 层 | 位置 | 文本来源 | 能不能改 |
|---|---|---|---|
| **A** | GMCM 的 **MOD 列表页** | 该 MOD `manifest.json` 的 `Name` 字段 | ✅ 改 Name |
| **B** | 点进去的**配置页**（选项名/说明） | DLL 硬编码 **或** CP 框架渲染 | ✅ 分情况，见下 |
| **C** | 配置页里的**人名** | `ConfigSchema` 的 `AllowValues`（NPC 内部 ID） | ❌ **不能改** |

### C 层为什么绝对不能改

`AllowValues` 的值（`Abigail`、`Abigail+Sebastian`、`Anton`…）必须**逐字匹配游戏内 NPC 内部 ID**。
翻译成中文后 MOD 匹配不到角色，**配置直接失效**。这是框架设计约束，不是漏译。

### GMCM 列表排序规则（2026-10-01 反编译实证）

列表条目 = `manifest.Name`，排序 = `OrderBy(entry => entry.ModName)`（`ModName → ModManifest.Name`），
即 **.NET 当前文化排序**——**不是**注册顺序、**不是**加载顺序、**不是**字母序（ordinal）。

- **想让某 MOD 排最前**：给 `Name` 加低权重前缀。全量 177 个 manifest 实测（`Sort-Object` + 与 GMCM 同语义的 `[string]::Compare` 逐条验证）：
  - ✅ `！`（U+FF01 全角）、`（置顶）`、`!`（ASCII）前缀 → 排第一
  - ❌ `0`、`①`、不加前缀 → **排不到第一**（`[` 开头的条目如 `[CP] ...` 当前排最前）
  - 验证标准：**对全部其余条目 `Compare<0` 且无平局**（平局会退化成注册顺序，不确定）
- **改 Name 的安全性**：GMCM 配置字典以 **UniqueID 为键**（`ModConfigManager` 实证），改 Name 不孤儿化配置；但 Name 同时是 SMAPI 日志显示名与 GMCM 页面标题，改名影响面 = 显示，零功能影响。
- **分节注意**：游戏内 GMCM 分「可编辑 / 仅标题屏」两节，各自独立排序；调用过 `SetTitleScreenOnlyForNextOptions(…, true)` 的 MOD 在游戏内落入后一节——**置顶前先反编译确认没设过它**（拖拉机未设置 → 在第一节）。

> 实例（2026-10-01）：用户要求拖拉机置顶 → `【功能】拖拉机` → `（置顶）【功能】拖拉机`，[string]::Compare 对其余 176 条全 <0。

---

## 二、B 层的两种 MOD 类型（关键分水岭）

### ① DLL 型 —— 选项名硬编码，只能改 DLL

**判断方法**：反编译 DLL，搜 `GenericModConfigMenu` 注册代码，看参数是**字面量**还是 `Translation.Get()`。

```csharp
// 硬编码 —— i18n 管不到，只能改 DLL
api.AddBoolOption(..., () => "Gift Service", () => "Let you send gifts...", null);

// 走 i18n —— 加 zh.json 键即可
api.AddBoolOption(..., () => Helper.Translation.Get("GiftService"), ...);
```

**实例**：MailServicesMod（52 个字面量，0 处 `Translation.Get()`）、SkipFishingMinigame、Unlockable Bundles 的部分串。

→ 修法：**DLL 等长字节替换**（见第四节）

### ② Content Patcher 内容包 —— 加 i18n 键即可，不用碰 DLL

选项名由 **CP 框架**从 `content.json` 的 `ConfigSchema` 字段名渲染。**CP 自带 i18n 支持**。

**实例**：Frontier Farm、山谷女孩、East Scarp、Childhood Sweetheart Caroline、DaisyNiko Earthy Recolour

→ 修法：**新增 `config.*` 键**（见第三节）

---

## 三、Content Patcher 的 ConfigSchema i18n 约定

反编译 `ContentPatcher.dll` 的 `GenericModConfigMenuIntegrationForContentPack.cs` 确认：

```csharp
private void AddSection(...) {
    menu.AddSectionTitle(
        () => this.TryTranslate("config.section." + name + ".name", name),   // 先查翻译
        () => this.TryTranslate("config.section." + name + ".description", null));
}
private string TryTranslate(string key, string fallback) {
    string translation = this.ContentPack.Translation.Get(key).UsePlaceholder(false);
    return string.IsNullOrWhiteSpace(translation) ? (fallback ?? "") : translation;  // 查不到才用原文
}
```

### 键名约定

**大小写严格照抄字段名。**

| 用途 | 键名 |
|---|---|
| 选项名 | `config.<字段名>.name` |
| 选项说明 | `config.<字段名>.description` |
| 下拉选项值 | `config.<字段名>.values.<值>` |
| 分组标题 | `config.section.<分组名>.name` |

### 三个已生效实例（可照抄这个模式）

| MOD | ConfigSchema 字段 | i18n 键 | 显示 |
|---|---|---|---|
| Childhood Sweetheart Caroline | `AutoSingle` | `config.AutoSingle.name` | 强制单身模式 |
| DaisyNiko Earthy Recolour | `enableGrass` | `config.enableGrass.name` | 启用草地 |
| East Scarp Core | `GoatSkin` | `config.GoatSkin.name` | 山羊的造型选择 |

---

## 四、DLL 等长字节替换（改硬编码文本的唯一安全方法）

### 原理

.NET 的 `#US` 字符串表用「长度前缀 + 连续数据」存储，**字符数必须与原文完全一致**，否则后续字符串偏移错乱、DLL 直接损坏。

中文字符在 UTF-16 里占 2 字节，表达力约等于 3-4 个英文字母 → **中文通常比英文短，用空格补齐**（GMCM 界面里看不见尾部空格）。

### ⚠️ 替换顺序陷阱：必须长串优先

**实例**（MailServicesMod）：

```
'Gift Service'      是  'Gift Service:'                 的子串
'Recovery Service'  是  'Recovery Service (Default):'   的子串
"Let in game events change..." 是 "...若未启用...将改变默认属性。" 的子串
```

→ 若短串先替换，会把长串里的那份也改掉，导致**长串无法匹配**。

**正确做法**：
1. 按长度**从长到短**排序
2. 逐个替换，每个**必须 `count == 1`**
3. 长串先改，短串在它内部的那份被一并吃掉，短串就只剩独立的 1 处

**验证方法**：先用等长占位符模拟替换，检查每个串最终 `count == 1`。

### 替换后三项校验（缺一不可）

1. **文件大小完全不变** —— `len(改后) == len(改前)`
2. **`dnfile` 能重新解析** —— 类型数/方法数正常，结构未坏
3. **逐条复核** —— 旧英文已消除 + 新中文已写入（同一编码 `utf-16-le`）

```python
import dnfile
pe = dnfile.dnPE(path)
td = len(list(pe.net.mdtables.TypeDef.rows))
md = len(list(pe.net.mdtables.MethodDef.rows))
```

### ⭐ 升级打法：条目级字典法（2026-10-01 第 5 批实战，13 DLL / 272 条一次成功）

上面的"子串替换 + 长串优先"是朴素做法；**把 #US 拆成条目后按整串精确匹配，可以整体绕开子串陷阱**：

1. **遍历 #US 得到 `(偏移, hdr, ln, 值)` 条目表**（空条目判定见坑 11）→ `值 → [条目]` 字典；
2. **翻译 TSV 一端是英文原串、一端是中文 + 尾随空格**，硬约束 `len(cn) ≤ len(en)`（UTF-16 码元数，差额补空格）——等长由构造保证，不靠事后凑；
3. **定位要求命中恰好 1 处**（0 处 = 键没对上（如原文拼写差异，见坑 11 实例）；≥2 处 = 有同串条目，必须换定位方式）——`"Tree"`/`"Tree Saplings"` 是不同条目，天然免疫子串互吃，**无需长串排序**；
4. **只写字符区** `file_pos = us流文件偏移 + 条目偏移 + hdr`，长度 `ln-1` 字节；前缀/标志字节不碰 → 文件大小恒不变。

**校验做成四件（按强度递增）**：① 重解析 + 条目数不变；② 新值在·旧值无；③ **文件字节差异集 ⊆ 计划补丁区间**（抓计划外改动）；④ **对照备份逐文件独立复验**（独立进程重读重解析，别复用执行脚本的内存状态）。

**句柄纪律**：全流程 `读字节 → dnPE(data=...) 内存解析 → 写回字节`，别按路径解析后再写（坑 9）。

> 实例：`_暂存-整合包拓展\scripts\{gen-b5-translations.py, apply-b5-dll-patch.py}` + `verify_b5_dll.py`；翻译表存档 `gmcm-翻译-B2-DLL等长-2026-10-01.tsv`，MOD 更新后可直接重跑。

---

## 五、⚠️ 踩过的坑（全部实际发生过）

### 1. SMAPI 的 i18n 键**大小写不敏感**

```
[山谷女孩] Found duplicate translation keys for zh:
[config.ManualRecolourSelection.name, ...]. Keys are case-insensitive.
```

**后果**：修改任何 `zh.json` 前，**必须先做大小写归一化检查**。

**检测要点**——不要用 `k.startswith('config.')` 过滤，要用 `k.lower().startswith('config.')`：

```python
seen, dup = {}, []
for k in data:
    low = k.lower()
    if low in seen:
        dup.append((seen[low], k))
    else:
        seen[low] = k
```

> 实例：山谷女孩的 zh.json 原本用**大写** `Config.` 前缀，用**小写**过滤时没看见它 → 加了重复键 → SMAPI 报错。
> 实例（2026-10-01 GMCM B 层）：钓鱼助手2 的 default 用 `Instant-catch-treasure`、zh 用 `instant-catch-treasure` —— 大小写变体**游戏内正常生效**，audit 报「缺 1」是误报。但反向要警惕：`audit-case-sensitivity.py` 不滤死键、section 按字段重复计数，它报出的缺口数**不能当真**（见坑 3）。

### 2. 「只有 zh.json 没有 default.json」**不是缺汉化**

那类 MOD 的原文本**硬编码在 DLL 里**，官方提供 zh.json 作为**可选覆盖层**。
有 zh.json = 已汉化；反而是**有 default.json 的才需要逐键对比**。

### 3. 不要用弱检测器扫全量

**两次翻车都因检测方法本身有盲区**：
- 用错正则把嵌套对象拍平 → 造出「缺 100 键」的**假警报**（实际 0 缺失）
- 用小写过滤 → 漏掉大写的 `Config.` 键，导致重复添加
- **第三次翻车（2026-10-01）**：`audit-case-sensitivity.py` 只读扁平 `i18n\zh.json`、不读 `i18n\zh\` 目录结构 → 把剑与魔法（556）、熊家（643）等**已有翻译整包误判为缺**；叠加死键重复计数，报出「缺 2177」这类不可信数字
- **第四次翻车（2026-10-01，连"权威脚本"也翻）**：`gen-B1-worksheet2.py` 用 `'content.json' not in files` 判定包类型——**大小写敏感** → CJB 传送点包（用的是 **`Content.json`** 大写 C）整包漏盘，账面缺口直到手工复扫才归零。**教训：凡按文件名做判据，一律 `name.lower()` 比较；且覆盖统计要有闭环——改完后全量 rescan，缺口必须恰好等于"已知有意跳过数"，多一条少一条都说明还有盲区**

**正确做法**：先拿**已知文件**自检检测器（与标准 JSON 解析对比键集合），通过后再扫全量。
> GMCM B 层的权威覆盖脚本是 `gen-B1-worksheet2.py`：读全部 zh 位置（扁平 + `i18n\zh\` 子目录）、按大小写归一化查重、**过滤死键**（布尔/数字输入框的 values），三件事都做对了才可作为结论。

### 4. 改动前先备份 + 改后独立比对

两次救回损失都靠备份：
- **WearMoreRings 被误覆盖**（因键名带引号，旧正则误报"全缺"，覆盖了原有的好翻译）
- **山谷女孩重复键**

**比对要独立读文件**，不要复用同一个 Python 对象——本次有一次因对象引用导致"差异为空"的假象。

### 5. SMAPI 宽松 JSON vs 标准 JSON（含「解析失败 ≠ 文件坏」）

SMAPI 接受带**注释**、**尾随逗号**、**无引号键名**的 JSON（如 `SetBackpackSizeCommand: "..."`），Python 标准 `json` 模块**不接受**。

**处理**：写一个宽松解析器（去注释 → 去尾随逗号），或用 `json5` 类库。**判定文件坏不坏要跑两遍**：先 `json.loads` 严格解析，失败再试 JSONC；两遍都失败才是真损坏（全盘扫描实测 111 个 zh 文件 = 60 严格 + 48 仅 JSONC + 3 真损坏）。

**同类的非法转义 `\'`**：标准解析器报 `Invalid \escape`，但 **JSON.NET（游戏侧）接受**——`可摧毁灌木\i18n\zh.json` 含 18 处 `\'`，曾因此被脚本误判「52 键全缺」，实际 52 键早已有完整中文翻译。

**正确做法**：确认「缺键」前先看它是不是解析问题；文件本身有 `\'` 时用 `\'`→`'` 修复（JSON 字符串里单引号无需转义，渲染结果不变），修后即变严格合法。

> 实例（2026-10-01 GMCM B 层）：`repair-bush-zh.py` 备份后修了 18 处转义，键数 52→52、值零变化，从「全缺」变成 0 新增。
> 实例二（同日，剑与魔法）：`zh\zh.json` 值里 2 处 `\'` —— **游戏侧 JSON.NET 全程正常加载，但 `gen-B1-worksheet2.py` 读不了整个文件**，把该包报成「缺 134 条」假缺口。**教训：「游戏能加载」≠「分析脚本能读」；覆盖统计异常先查文件能不能被严格解析，再信数字。**

### 6. DLL 里的多轮重载不是冲突

日志里同一资源多次 `load → edit → load`，可能是**季节切换/条件刷新**导致的正常重载，不是覆盖冲突。
**判断覆盖要看"同一轮内"的顺序**，不要跨轮比较。

### 7. 文本拼接追加键：原文件自带尾随逗号会拼出 `,,`

**现象**：往 zh.json 末尾追加新键时，脚本按 `body + ',\n' + 新键` 拼接，若原文件 `}` 前**本来就有尾随逗号**（SMAPI/JSON.NET 容忍），拼出 `key1,,"newKey": ...` → 解析失败。

**原因**：尾随逗号在宽松 JSON 里合法，按字符串拼接时却会被当成"已有分隔符"再拼一次。

**正确做法**：拼接前先去掉 `body.rstrip()` 末尾的 `,`；**写盘前先对拼好的整串做 `json.loads`（或严格+JSONC 双重）自检**，通过才落盘。

> 实例（2026-10-01 GMCM B 层）：`apply-gmcm-translations.py` 首版漏了这步，靠写盘前自检当场拦下，**没有文件写坏**；随后把去尾逗号修复同步进了 `apply-gmcm-translations.py` 与 `merge-external-packs.py` 两个脚本。

**配套纪律**：内联 `python -c "..."` 会被 PowerShell 转义搞坏（中文/引号全乱），一律写 `.py` 脚本文件执行；Python 统一 `python -X utf8`。

### 8. `i18n\<语言>\` 是多文件目录：CP 合并全部 json 并**跨文件查重**

**现象**：往 `i18n\zh\` 里新建 `config.json` 后，游戏日志刷 207 条：
```
[XX包] Mod couldn't load some translation files:
[XX包]   - Ignored duplicate translation key 'config.xxx.name' in zh\zh.json.
```

**原因**：`i18n\zh\` 目录下的**所有** json（`zh.json`、`config.json`、`Handbook.json`…）会被合并成一套翻译，**重复键跨文件存在也会被告警并忽略其一**（加载顺序按文件名，`config.json` 先于 `zh.json` → 被忽略的是 `zh.json` 里那份）。根因是**合并前的缺口分析没读到 `zh\zh.json`**（该文件带块注释 + 2 处 `\'`，严格解析直接失败，分析脚本误判「180 条全缺」）→ 把外部汉化包里**已有的 207 键**又合并了进去。

**正确做法**：
1. **合并外部汉化包前，缺口必须以「游戏实际会读到的全部文件」重算**——且重算脚本必须能通过该包 zh 文件的解析（先修 `\'`/注释问题，见坑 5）。
2. `i18n\<语言>\` 目录里**只放真正缺的键**；发现重复立即去重（保留装包原文件，删自己新建文件里的重复键）。
3. 启动日志搜 `duplicate translation key` 是**发现这类问题的唯一可靠手段**——静态校验各文件自身都合法，发现不了跨文件重复。

> 实例（2026-10-01 剑与魔法）：`config.json` 223 键 → 去重后 16 键（只留 `zh\zh.json` 没有的 TimegateConfig/MateoThemeConfig/HectorThemeConfig 等），装包原措辞恢复生效，告警应清零；备份 `汉化备份\2026-10-01-剑与魔法config去重前\`。

### 9. `dnfile.dnPE(path)` 会占住文件：随后 `open(p,'wb')` 报 `Errno 22`

```
OSError: [Errno 22] Invalid argument: 'D:\...\AlternativeTextures.dll'
```

**原因**：按路径加载后 dnPE/pefile 的文件句柄（或映射）未释放，与写入模式打开冲突——**读没事、一写就炸**，且报错信息（EINVAL）完全指不到"句柄占用"上，极易误判为文件只读或路径非法。

**正确做法**：整个流程用内存副本，别让解析器碰磁盘上的写路径：

```python
fb = bytearray(open(p, 'rb').read())   # 1. 读盘并关闭
pe = dnfile.dnPE(data=bytes(fb))        # 2. 从内存解析（dnPE 支持 data= 参数）
# ...计算补丁，改 fb...
with open(p, 'wb') as fw:               # 3. 此时无其他句柄，可正常写
    fw.write(bytes(fb))
```

> 实例（2026-10-01 第 5 批 DLL 替换）：首跑写 `AlternativeTextures.dll` 直接失败；改内存解析后 13 个 DLL 一次全部成功。

### 10. ⛔ 绝不用「`'wb'` 打开后只写几十字节就关」的方式测试生产文件

**现象**：为了复现坑 9，我写了个"复现测试"：`f = open(p,'wb'); f.write(d[:10]); f.close()` —— 结果**把 317 440 字节的 DLL 截断成了 10 字节**。

**原因**：`'wb'` 先截断再写。对生产文件的任何写打开都是**一次真实变更**，不存在"只测一下"。

**正确做法**：
1. 排查类测试**只用只读方式**（读、比对、`'r+b'` 不截断模式），或**对副本操作**；
2. 确需验证写入时，目标也应是备份文件而非原件；
3. **铁律 1/2（改前备份 + 改后独立比对）是唯一兜底**——本次靠 `汉化备份\2026-10-01-第5批DLL替换前\` 的原件 + SHA256 比对当场恢复，与文件同目录备份的及时性直接相关。

> 实例（2026-10-01，同一场内）：截断发生在第 5 批执行前、备份建立之后，恢复后哈希与备份完全一致，**未影响后续 13 个 DLL 的替换**。1 小时内两次靠备份脱险，这不是运气，是流程。

### 11. #US 堆遍历：`ln == 1` 是合法的**空字符串**条目，不是坏条目

**现象**：遍历脚本遇到"条目长 1 字节"就当损坏 `break` → MailServices 等 DLL 报坏条目、全量命中验证做不下去（一度误以为"这些 DLL 解析不了"）。

**原因**：#US 条目布局 = `[压缩长度 ln（含尾部标志字节）][UTF-16 字符区][标志字节 0/1]`。空字符串的字符区为 0 字节，只剩标志字节 → `ln == 1`。判定写成 `if ln < 2` 就会把它误杀。

**正确做法**：

```python
if ln < 1 or i + hdr + ln > n:      # 注意是 < 1，不是 < 2
    raise RuntimeError('坏条目')
s = data[i+hdr : i+hdr+ln-1].decode('utf-16le') if ln > 1 else ''
```

**配套（等长替换的安全边界）**：只替换字符区（`ln-1` 字节），**长度前缀与标志字节绝不碰** → 条目数、流大小、文件大小全部不变，PE 结构零影响。字典法定位（整串精确匹配，命中必须恰好 1 处）天然规避子串误伤（`"Tree"` 与 `"Tree Saplings"` 是不同条目）。

> 实例（2026-10-01 第 5 批）：修正判定后 15 个 DLL 的 272 条英文**全部精确命中、0 重复、0 坏条目**。同轮另踩：**字典键必须与 #US 逐字节一致**——作业表原文 `Meat Cleaver/Want` 是原作者拼写错误，我凭印象按 `Wand` 建键，字典校验直接报"缺 1 多余 1"拦下（翻译流程里让脚本对账、别信记忆）。

### 12. ⚠️ B-2 盘点只扫「GMCM 调用处」，会漏掉「实参是变量」的标签

**现象**：Spritesheet Extender 的两个标签 `Male/Female Sprites to Be Added` 在盘点表里记为 **0 条字面量**（"标签是变量"），于是第 5 批没翻；游戏内截图打脸——**字面量其实存在**，只是不在调用处：`api.AddIntOption(() => config.MaleCount, label: LABEL_MALE, ...)` 这类写法里实参是变量，字面量在别处（字段初始化/常量）赋值，调用处扫描看不见。

**原因**：调用处提取（反编译正则扫 `Add*Option(...)`）只认**写在括号里的字面量**；C# 允许把字面量先赋给变量再传入 → 同一个标签"调用处无字面量、#US 里有"。

**正确做法**：
1. 盘点表里标"0 条字面量"的 MOD，**不能默认为无需处理**——应对该 DLL 的 **#US 全量过目**（过滤出像 UI 标签的英文串）再下结论；
2. 第 5 批的收尾自检应加一步：**改完后扫 13 个 DLL 的 #US 残留英文**，把"像标签的"逐条人工过目，而不是只信作业表覆盖率。

> 实例（2026-10-01）：用户游戏内截图发现 → 实测 `#US` 确有两条 → `apply-b5b-spriteextender.py` 补替 2 条（等长+四件套校验 PASS）。**教训：作业表的"0"要分清是"真没有"还是"提取器没看见"。**

---

### 13. i18n 批量改写：写前 token parity 固定正则 +「值是英文」先分类再决定译不译

**现象**：给 zh.json 批量补键/改值时，最容易写出"token 丢了、游戏内报错或对话断裂"的文件；另外全包扫描"zh 值仍是英文"出 232 条，直接全译会把命令、占位符改坏。

**原因**：SDV 文本里混着十几种 token（`#$b#` 段落、`$0-$9` 与 `$s/$h/$u/$l` 表情、`#` 选项、`^` 换行、`@` 玩家名、`%` 前缀、`{{...}}` i18n 占位），漏一个就断；而"值是英文"≠"漏译"——命令值、id、署名译了会直接损坏功能。

**正确做法**：
1. **写前 parity**，新旧值用同一正则提取 token 列表逐项相等：
   ```python
   TOK = re.compile(r'#$b#|[@~]|\$\d+|\$[a-zA-Z]|#|\^|%|\{\{[^}]*\}\}')
   assert TOK.findall(old) == TOK.findall(new)
   ```
   `#$b#` 必须排在 `#` 之前；`$` 要同时匹配数字与字母（X 拓展用 `$s/$h/$u/$l`）。
2. **CJK 检查带豁免**：仅当 EN 含 `[A-Za-z]{3,}` 才要求 ZH 含汉字——纯标点值（`……$4`）、EN 本身是中文（个别 default 如"即时捕捉宝藏"）不报。
3. **「值是英文」先分六类再决定**：内部 id/脚本命令（`$v AbigailNTS3 false false`）、纯占位符模板（`{{name}} x{{count}}`）、画师/音乐署名、虚构语言（地质学家密文）、schema URL、应保留术语（HUD/DaisyNiko）→ **不译**；真对话/config 文案 → 译。232 条筛出 116 条真漏译。
4. **写回保结构**：解析用状态机剥 `//`、`/* */` 注释并剥 `}` 前尾逗号（配套坑 5）；写回用 **raw 原文去掉尾 `}` 再追加键行**（保留原注释），最后一个键行**不带尾逗号**、注释行内不放逗号（配套坑 7）。
5. 同名键替换用 `re.escape(json.dumps(key))` 定位并断言 `count == 1`。

> 实例（2026-10-02）：四批补键 771 + 英文值汉化 116，全部按此流程，独立复核 ALL PASS。脚本模板：`Temp\opencode\batch4-merge.py`（补键）、`sameeng-merge.py`（改值）。

---

### 14. 同名 i18n 目录：导出清单按 mod 名生成文件名会互相覆盖

**现象**：全包扫描导出缺键清单，`【大型拓展】ES` 下两个 i18n（`[CP] East Scarp` 缺 2 键、`[CP] East Scarp NPCs` 缺 7 键）都写入 `_大型拓展_ES.txt`，后者覆盖前者 → 差点漏译 2 键，首轮统计也失真。

**原因**：输出文件名只取了 mod 目录名，同一 mod 可以有多个 i18n 目录（多个 content pack）。

**正确做法**：文件名带子目录（`mod+子目录`），或**合并脚本运行时自己现算 missing、不依赖导出文件**（本次最终做法）；统计口径以现算为准。

> 实例（2026-10-02）：`batch4-paths.py` 复扫后补齐 ES 2 键（`Strings.EloiseSummer.2`、`Strings.MeadowFarm.1`）。

---

### 15. 批量替换中途失败，重跑会撞「old 值已变」——先做幂等判断

**现象**：`sameeng-merge.py` 跑到第 9 个 mod 因小写键 old 值写错而 assert 中断；已成功的前 8 个 mod 若直接重跑，会在 `zj[k] == old` 断言上全部炸掉。

**原因**：脚本假设"文件永远是改前状态"，但部分成功后文件已是混合状态。

**正确做法**：替换前按三态分支——`当前值 == new → 跳过（已改）`、`== old → 待替换`、`都不等 → 报错停机`；只对"待替换"集合执行备份与写入。

```python
if zj[k] == new:      continue          # 幂等：上一轮已完成
assert zj[k] == old    # 否则必须是原文，防改错文件
pending[k] = (old, new)
```

> 实例（2026-10-02）：时尚感 `\n` 转义写错中断 + 神秘生物小写 old 错，两次靠幂等保护重跑收齐 116 键。

---

### 16. 缺键扫描要按 SMAPI 一样**大小写不敏感**，否则已有键被误判缺失 → 补出重复键

**现象**：SMAPI 日志两行 WARN——`Found duplicate translation keys for zh: [config-menu.option.Instant-catch-treasure]. Keys are case-insensitive.`（钓鱼助手）与 `[Generic.XDV.nofemale]`（X拓展）。文件内同键一大小写两份。

**原因**：SMAPI 的 i18n 键查找**大小写不敏感**（坑 1 已记），但批 4 缺键扫描用 `k not in zj`（**大小写敏感**）→ 文件里已有大写版 `Instant-catch-treasure`，脚本找小写 `instant-catch-treasure` 判为缺失 → 追加成两份。**假阳性 missing 是撞键的唯一来源。**

**正确做法**：扫描缺键前先建小写索引，与 SMAPI 行为对齐：

```python
zj_lc = {k.lower() for k in zj}
missing = [k for k in dj if k.lower() not in zj_lc]
```

补完键后加一道 dup 扫描兜底（按 `k.lower()` 分组，组内 >1 即报）；已撞的删小写、留大写（保留原译值）。

> 实例（2026-10-02 下半场）：钓鱼助手 163 键、X拓展 459 键修复，全包仅这 2 组撞键。

---

### 17. mod **加载期** `i18n.Get()` 是英文快照：语言切换前固化的信件文本，改对 zh.json 也永远不生效

**现象**：恐龙蛋捐赠信显示英文（截图），但 `【拓展】畜牧业\i18n\zh.json` 里 `Feeding.TreatDaffodil.Letter` 早已是中文，SMAPI 日志也无该 mod 翻译警告——"翻译在、加载正常、就是显示英文"。

**原因**（dnSpy 反编译 `AnimalHusbandryMod.dll` + `MailFrameworkMod.dll` + 日志时序三重实证）：
1. 畜牧业 `DataLoader.LoadTreatsMail()`（`DataLoader.cs` 构造函数内，**只在 mod 加载期跑一次**，日志 18:43:29）执行 `i18n.Get(key)` → 此刻游戏语言还没切（日志 18:44:21 才 `CurrentLanguageCode en→zh`）→ 取到 default 英文；
2. 结果**直接当字符串存进 `Letter.Text`**（`Letter.I18N == null`），邮件框架显示时（`Letter.cs`）`I18N != null 才 I18N.Get(Text)，否则原样显示 Text` → 永远是这个快照；
3. 畜牧业 `OnSaveLoaded` 只重跑工具信/食谱信，**不重跑本信** → 进档后也不会刷新。
→ 结论：**这类"构造期取值"的文本，改 i18n 文件无效**，必须换注册方式。

**正确做法**（不动 DLL）：用邮件框架的 **content pack 同 Id 覆盖**——pack 在 `SaveLoaded`（语言已 zh）重跑 `SaveLetter`，同 Id 替换掉英文信；pack 传的是 **i18n 键名**而非文本，`I18N = contentPack.Translation` → 显示时按当前语言取值（延迟翻译）。要点：
- mail.json 的 `Title`/`Text` 放 pack 自己 i18n 的键（模板：`【前置】邮件服务框架\ContentPackTemplate\mail.json`）；
- 条件逐项对照原 mod 源码复刻（本例 `MailNotReceived` + `CollectionConditions: Artifacts`）；
- pack 必须带 `i18n\default.json`，否则 `hasTranslation=false` → `I18N=null` → 显示键名字面量。
- 通用判别：反编译看到 `xxx = i18n.Get(...)` 的结果**进构造函数/字段赋值**（快照）而非 `.Get()` 时传键名，就是这个坑。

> 实例（2026-10-02 下半场）：`游戏\Mods\【汉化】畜牧业恐龙信-邮箱覆盖\`（恐龙蛋信/番红花信两封，独立复核 `mf-pack-verify.py` PASS）；用户已读过的英文信是一次性历史，不重现属正常。

---

### 18. **外部生成途径**缺 mod 自有初始化：CJB 悬浮剑与魔法「国王万岁（枪）」附件槽空数组 → 越界崩菜单

**现象**（用户贴的日志摘要）：CJB 物品生成器绘制时
`ItemMenu.draw → drawToolTip → Tool.drawAttachments_PatchedBy<Digus.AnimalHusbandryMod__KCC.SnS>
→ LLTKAttachmentSlots.Prefix (Bow.cs:297) → 反射 Slingshot.DrawAttachmentSlot
→ LLTKGunSlotSprites.Postfix (Bow.cs:411) → ArgumentOutOfRangeException`，
SMAPI 强制关闭菜单（游戏本体未崩，无存档风险）。

**原因**（`dnSpy.Console` 反编译 `SwordAndSorcerySMAPI.dll` 实证，输出在临时目录 `opencode\sns-decomp\`）：
1. SnS 的 `LLTKAttachmentSlots.Prefix`（patch `Tool.drawAttachments`）对 ItemId = `DN.SnS_longlivetheking_gun` 反射调 `DrawAttachmentSlot(0/1)`；
2. `LLTKGunSlotSprites.Postfix`（patch `Slingshot.GetAttachmentSlotSprite`）**裸访问 `attachments[slot]`/`attachments[0]`，无边界检查**；
3. 1.6 `new Slingshot(itemId)` 构造出的实例附件槽 **Count=0**。SnS 自有路径全都补槽——剑↔枪切换 `ModSnS.SwapLltk` 手动 `AttachmentSlotsCount = 2`（`ModSnS.cs:1122`），剑版还有 `MeleeWeaponSetAttachmentCountForLLTK` 的 drawTooltip 兜底——**唯独外部生成途径（CJB 直接创建）没人补** → 越界；
4. 堆栈里的 `PatchedBy<Digus.AnimalHusbandryMod__KCC.SnS>` 只是**同方法多 patcher 的排序显示**：畜牧业的 Prefix 对非其工具 `return true`，不是肇事者。

**正确做法**：
- **诊断路径**（可复用）：崩溃堆栈 `PatchedBy<...>` ≠ 肇事者签名 → 从最内层（真正抛异常的）patch 反编译查边界检查 → 再对比「mod 自有路径」与「外部工具触发路径」的初始化差异。
- **规避**（当前方案，用户确认）：CJB 列表不悬浮该枪；取出进背包后不悬浮其 tooltip（挥舞/使用不走 `drawAttachments` 路径）。
- **根治候选**（按优先级）：① 前置小 SMAPI mod 在 `drawAttachments` 前给空槽枪补 `AttachmentSlotsCount = 2`（纯新增可删，需 .NET SDK 编译）；② 改 SnS DLL 加边界检查（重写第三方 DLL，最后手段）；③ 等上游修复。**截至记录时未做任何改动。**

> 实例（2026-10-02 第四场）：反编译诊断完成，选定规避方案，零改动。

---

### 19. `Can't get audio ID 'xxx'` ERROR：事件 **playMusic 短 ID** 对不上注册全名；`AlternativeTrackIds` 不是全局别名

**现象**：`[ERROR game] Can't get audio ID 'NewMagicLearned' because it doesn't exist.`（及 `'Nexus'`）各若干次；不崩不坏档，但该时刻剧情 BGM 静默。

**原因**（SVE 本体 vs 女法师附加 CP 对照实证）：
1. 曲目由 CP `Data/Music` patch 以**全名**注册（SVE `Music.json`：`FlashShifter.StardewValleyExpandedCP_Nexus` → `assets/Music/Nexus.ogg`）；
2. 另一 content pack 的事件命令写**短 ID**（`playMusic Nexus`）→ 游戏按 audio ID 查表失败 → ERROR；
3. **陷阱**：`Jukebox.json` 的 `AlternativeTrackIds: ["Nexus"]` 让短 ID 看似合法——它只在**点唱机曲目表内**生效，不注册全局 `playMusic` 别名。

**诊断路径**（可复用）：
1. ERROR 行拿曲目名 → 全 Mods json 搜事件行内 `playMusic <名>`——事件是**单行超长**，用 `finditer` 数**匹配数**而非行数（本例 9 行含 12 匹配，按行数预期 3 被写前断言拦下）；
2. 搜注册方确认全名：`Music.json` / `Data/Music` patch 的键；
3. 事件重复器的 `Current Event` DEBUG 给出事发事件 ID，交叉定位事件文件；ERROR 时间戳与事件段落（warp/pause）对齐可闭环。

**正确做法**：事件短 ID 改成注册全名——**对照同一事件在 SVE 本体的写法最稳**。替换走三步断言：预期计数先列全部匹配核实 → 反向还原 == 原文（字节级零误伤证明）→ 重读复核 0 残留。

> 实例（2026-10-02 第五场）：女法师附加 CP `SVE_Events.json` 12 处修复，备份 `汉化备份\2026-10-02-女法师附加音效ID\`；详见使用记录当日第五场章节。

---

### 20. 有 i18n ≠ 全汉化——事件 `quickQuestion` 菜单是**命令内联参数**，不走 i18n，要直接改事件 JSON

**现象**：对话明明是中文（`{{i18n}}` 已翻），同一事件里弹出的**选择菜单**却整行英文——典型如山谷女孩成人事件的选项（`What do you want to do?#Doggy#Cowgirl#…`）。

**原因**：CP 事件里两种文本机制并存——
1. `speak` 对白：文本写 `{{i18n 键}}`，加载时查 `i18n/zh.json` → 已汉化；
2. `quickQuestion` 的问题 + `#` 分隔选项：是**事件命令的内联参数字符串**，没有任何 i18n 键机制 → 游戏原样显示英文。改 zh.json 对它完全无效。

**正确做法**（`fix-vg-menus.py` 范式）：
1. **动态提取预期**，不手数（防漏）：`QRE = re.compile(r'quickQuestion\s+(\\"|")?([^#"]+(?:#[^#"/]*){1,12})')`，命中后用 `(break)|playMusic|switchEvent` 截断尾随命令 → 得到全部实际出现的选项块（本例 **29 种 / 147 处**）；
2. 手写「模式 → 译文」表（含按人名注入的批量键与显式 Fix 表），**写前断言**：`set(EXPECT) == set(TRANS)` 双向零差集 + 总数恒等，任一不满足中止、一个字节都不动；
3. 长串优先替换 → **反向还原逐字节 == 原文**（零误伤证明）→ 重读键级残留 0 + 译文计数 == 预期；
4. 人名译文**复用该 mod `i18n/zh.json` 既有译名**（防同一 NPC 出现两种译法）；
5. 单引号参数字面量（`'ends Cutscene'`、`'cost 400g'`）**保守原样保留在译文内**——语义未查证（疑似游戏可识别参数），不翻译不删除；若游戏内仍显示英文残段再单独处理。

> 实例（2026-10-02 第六场）：山谷女孩 13 个事件文件、12 个改动、147 处选项汉化，备份 `汉化备份\2026-10-02-山谷女孩菜单汉化\`；详见使用记录当日第六场章节。

---

### 21. 事件双报错是**因果链**：上游 `changeLocation` 拼写损坏 → 玩家留在自定义地图 → `switchEvent` 按**当前地图**查资产落空

**现象**（成对出现）：
```
[game] Event '10551' has command 'changeL ocation FarmHouse' which couldn't be parsed: unknown command 'changeL'.
[game] Event '10551' has command 'switchEvent 10551_Emily' which couldn't be parsed: can't load new event from asset 'Data\Events\Custom_BedEvent' because it doesn't exist.
```

**原因**（一条链，不是两个独立 bug）：
1. 事件命令字符串损坏（本例 `changeL ocation` 多一个空格）→ 该命令**被跳过** → `changeLocation` 没执行 → 玩家仍留在上一段切进去的**自定义事件地图**；
2. `switchEvent` 的目标资产 = **玩家当前所在地图**的 `Data/Events/<地图名>`；自定义事件地图（`CreateOnLoad` 型，如 `Custom_BedEvent`）通常**没有任何包给它建 `Data/Events` 行** → 资产不存在 → 该命令也被跳过；
3. 命令逐条跳过，事件流到键尾**自然结束**——实测有兜底（回触发前的地图），不崩不卡，但**每次触发固定打 2 条 ERROR**，且收尾走的是异常路径（边缘时机下仍有风险）。

**正确做法**：
1. **从第一条 `unknown command` 入手**——它才是根因入口，报错里有确切的坏字符串（`changeL`），直接 grep 该串定位（本例全文件 179 处 `changeLocation` 仅 1 处坏，grep `changeL ` 即中）；
2. 对照**同文件同模板的正确写法**确认预期（本例其余 89 处、其他 4 个姿势子事件的收尾全是正确拼写）；
3. 判归属：**改前备份对照**——备份里就坏 = mod 原版 bug（本例 `bak=1 cur=1`），与自己的改动划清界限；
4. 修复用 bytes 替换 + 三步断言（写前恰 1 处 / 前向分段证明：替换点前后字节全同 / 反向按替换点切片还原 == 原文 / 写盘重读）。注意反向锚定不要用「上下文+目标串」——事件模板高度复制粘贴，长锚也会命中多处，**按替换点位置切片反向**才精确。

> 实例（2026-10-02 第七场）：山谷女孩 `MarriageEvents.json` L26 `10551_EmilyMissionary` 修复 1 处，备份 `汉化备份\2026-10-02-卧室事件切场命令修复\`；详见使用记录当日第七场章节。

---

### 22. Newtonsoft 容忍集**以 .NET 实测为准**——孤立逗号/尾逗号/注释/裸键全救，**缺冒号/缺逗号才是真坏**

**现象**：体检要扫 2972 个 JSON 并判定"哪些是 CP 能吃的方言、哪些是真坏"——凭记忆猜容忍集会把 1945 个正常 CP 文件误报成坏文件。

**原因**：CP 实际用 Newtonsoft.Json 解析（非标准 JSON）。用 .NET SDK 建临时项目对 Newtonsoft 13.x 实测 14 项对照：

| 输入 | Newtonsoft |
|---|---|
| 孤立逗号 `, ,` / 双逗号 | ✅ 容忍 |
| 尾逗号 `[..., ,]` / `{"a":1,}` | ✅ 容忍 |
| `//` 行注释、`/* */` 块注释 | ✅ 容忍 |
| 单引号字符串 `'x'` | ✅ 容忍 |
| 裸键 `key: 1`（无引号） | ✅ 容忍 |
| 前导小数 `.03` | ✅ 容忍 |
| 字符串内裸 tab | ✅ 容忍 |
| **缺冒号** `{"a" 1}` | ❌ FAIL |
| **缺逗号** `{"a":1 "b":2}` | ❌ FAIL |

**正确做法**：体检工具的"宽松层"按此表实现——`mod-doctor.py` 的 `strip_loose` 用**单正则交替**（字符串/注释/单引号/裸键带冒号/前导小数/尾逗号/孤立逗号分支保序匹配）一次剥离，**别拿标准 JSON parser 当裁判**；"语法坏"= 宽松层仍 FAIL 的结构级损坏（缺冒号/缺逗号/括号不配对）。另注意 CP 容忍不等于 SMAPI 容忍——日志里 0 条 JSON 解析 ERROR 才是"当前可用"的实证。

> 实例（2026-10-02 第八场）：`mod-doctor.py` json 检查项开发，宽松可救 1945 / 真坏 4 的判定即出自此表；实测脚本为临时 nstest 项目（跑完即删）。

---

### 23. CP 互斥 When 写 `"HasMod |contains=<UID>": false`——写成 `"HasMod": "<UID>": false` 是非法 JSON；幂等匹配必须用**裸子串**

**现象**（两个连环翻车，均在 dry-run 暴露）：
```
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 113 ...   ← 插入的 When 行非法
（dry-run 挂死，300s 超时零输出）                                      ← 幂等检查失效 → 死循环
```

**原因**：
1. `"When": { "HasMod": "uid": false }` = 一个键后跟**两个冒号**，非法 JSON。CP 的正确形态是**键带修饰符、值为布尔**：`"HasMod |contains=uid": false`（环境实例：朱丽叶/地质学家 content.json 大量在用；`"HasMod": "uid"`（值=UID 字符串）是"要求存在"的另一语义，**没有 false 简写**）；
2. 新语法里 UID 前是 `=` 不是 `"` → 幂等检查若写 `'"uid"' in seg` 永远 False → 每轮 while 重复插入同一条 When → 死循环且无输出（管道下 print 还被全缓冲，症状更隐蔽）。

**正确做法**：
```python
ins = '\n%s"When": { "HasMod |contains=%s": false },' % (ind, uid)   # 插入互斥守卫
if uid in seg:                                                        # 幂等：裸子串
    saw_idem = True; continue                                         # （UID 含点号不会误报）
```
批量编辑必须配**断言链**：宽松解析（防止插出非法 JSON）+ 逐步**反向还原 == 原文**（防止改错区域）+ 落盘重读 + `--dry-run` 先行；遇到"跑很久没输出"先怀疑幂等条件，再怀疑 print 缓冲（`python -u`）。

> 实例（2026-10-02 第八场）：`fix-load-conflicts.py` 修 9 对 Load 冲突，两个 bug 均在 dry-run 阶段被抓，零写盘。

---

### 24. SMAPI 日志行格式是 `[HH:MM:SS ERROR mod]`——按 `[ERROR]` 检索数出 0 条 ≠ 无 ERROR；**基线随每次启动刷新**

**现象**：写日志基线读取时按 `[ERROR]` 检索得 0，与目视（日志里明明有 2 条 changeL ERROR）矛盾。

**原因**：SMAPI 4.x 行格式为 `[时间 级别 组件名] 消息`，**级别在时间后、方括号内**；且 CP 的 `Can't apply data patch ... doesn't match an existing target` 是 **WARN** 不是 ERROR——整片刷屏（本次约 73 行）也不进 ERROR 计数。

**正确做法**：
```python
re.findall(r'^\[\d{2}:\d{2}:\d{2} ERROR ', text, re.M)   # 行首锚定，级别位置正确
```
**日志基线是"最近一次启动"的快照**——修复后必须**重启游戏再读日志**验证：第八场重启后 ERROR x2 → x0（坑 21 的 changeL 随修复消失）；旧基线是修复前现场，别拿它当修复后结果。另：日志里 0 条 JSON 解析 ERROR ≠ 无坏文件——坏文件可能被 `HasMod` 条件挡着或根本没被引用（按需加载）。

> 实例（2026-10-02 第八场）：`mod-doctor.py` 日志基线模块；坑 21 的修复在本轮重启验证归零。

### 25. "未翻键"判定口径是 **zh 值 == default 英文值**——只看"值含英文"会误判 3 万+；豁免必须分层

**现象**：`_untranslated(v)` 只判"值含英文字母"→ 全环境扫出 30727 个"未翻"（体检真实数字是 81）——大量正常中文译文含英文单词/缩写被误判。

**原因**：体检报"未翻"的真实口径是三重条件：`v == ov`（zh 值与 default 英文**完全相同**=照抄没翻）且值是英文且不在豁免里。逐键导出 81 条定性：**真未翻 = 0**——45 键山谷女孩 `$v …` 事件命令、8 键 SVE 金额 `2,500g`、7 键 RSV 配偶名单/`{Greeting}` token、4 键 ZoomLevel 页面内部 id（界面标题已汉化）、2 键 `/shake` 事件命令、其余 = 虚构语言/打鼾 ZZZ/作者名/键名=值。

**正确做法**：豁免分三层——
1. **通则**（值模式级）：含中文、值含 `''`、以 `$X` 或 `/` 开头、`\d+g` 金额、`z{3,}` 打鼾、剥离 token（`$…`/`#…#`/`{…}`/`%item`/`^`/`~`/`@`/`/cmd`）后无英文字母；
2. **键=值**（`k != v`）：值是键名本身的回退占位，天然无可翻内容；
3. **显式白名单** `INTENTIONAL = {(pack, key), …}`：无法模式化的有意不翻（虚构语言、曲名作者、选项值、内部 id）——**必须带注释写明理由**，让"未翻 0"是诚实的而非藏问题。

> 实例（2026-10-02 第九场）：`mod-doctor.py` `_untranslated` 通则扩展 + `INTENTIONAL` 白名单 13 键；未翻 81 → 0。

### 26. CP `When` **值互斥**判定——同键不同值 = 永不同真，体检可判互斥不报冲突；**同键相同值不算**

**现象**：给两 patch 写互斥条件后（一方 `"Lewis …": "True"`、另一方 `"Lewis …": "False"`），体检工具仍报"条件冲突"——它只认 `HasMod |contains=…: false` 一种互斥形态。

**原因**：`When` 是 AND 语义——两包在同资源的 When 若存在**同键不同值**，两个 When 永远不可能同时为真 = 互斥。判定必须**逐 patch 组合**（任一组合缺同键异值 → 整体不互斥，存在无条件 patch → 不互斥）；值比较用 `str(v).strip()` 原样比（不 casefold——字面量大小写一致性由 mod 生态保证，`"False"` 是配置 token 自己的写法）。

**正确做法**：
```python
def _val_exclusive(wa_list, wb_list):   # 完整实现见 mod-doctor.py
    for wa in (wa_list or [None]):
        for wb in (wb_list or [None]):
            if not isinstance(wa, dict) or not isinstance(wb, dict):
                return False            # 存在无条件 patch → 可同时生效
            if not any(str(wa[k]).strip() != str(wb[k]).strip() for k in set(wa) & set(wb)):
                return False            # 无同键异值 → 不互斥
    return True
```

> 实例（2026-10-02 第九场）：夜市/节日 2 对用 `"Lewis…": "False"` 精确互斥后升入 mutex 桶；意外收获 RomRas×地质学家 `Characters/Toddler*`——双方 When 同键 `Spouse`（`Wizard` vs `Jasper`）= 真互斥，条件 2 → 互 2 无误判（脚本 dump 逐 When 核实）。

### 27. 跨包引用对方的 config token → **整个 patch 被 Ignored**——用 CMCT 的 `Query:` 条件（环境有现成依赖与实例）

**现象**：把 `"Lewis should pass a law…": "False"` 写进 DaisyNiko/淫乱节日 的 `When`（照抄单身汉自己包内的写法，静态断言全过），启动日志：
```
Ignored 【地图美化】DaisyNiko's低饱和度大地 > Load Maps/night_market_tilesheet_objects: the When field is invalid: 
'Lewis should pass a law…' can't be used as a token because that token could not be found.
```
**3 个 patch 全部被忽略**——比修复前更差（美化夜市/淫乱节日图完全不生效）。

**原因**：config token 只在**定义它的 pack 的 context** 里可解析（CP 文档："Config tokens contain mod options **you define**"）；`When` 键在**本包** context 求值 → 其他包找不到该 token → CP 判整个 patch **语法级无效并 Ignored**（不是"条件不成立"）。体检工具静态看 `When` 是互斥的，但**无法验证 token 可解析性**——静态绿灯 ≠ 游戏内生效，**必须以启动日志为准**。

**正确做法**（环境现成三件套，照抄【NPC】女法师的 67 处实例）：
1. 用 `【前置】跨MOD兼容性`（Spiderbuttons.CMCT，已安装）的 Query 条件：
```json
"When": {
    "Query: '{{Spiderbuttons.CMCT/Config: <对方UID>, <config名>}}' = '<值>'": true
}
```
2. 本包 `manifest.json` 加 `Dependencies`：CMCT `IsRequired: true` + 被查询包 `IsRequired: false`（女法师模式）；
3. **`=` 比较的值以运行时 `config.json` 实际存储为准**——GMCM 写入小写（单身汉 config 存 `"false"`），manifest Default 是 `"False"`——大小写以实测为准，别照抄 Default；
4. 语法（`Query: '{{…}}' = '…'`）只能从**环境既有成功实例**学——日志无 Ignored 的实例才是有效证据。

> 实例（2026-10-02 第九场）：第一次修复用裸 config 键 → 启动 3 条 Ignored → 回滚（备份 hash 双匹配）→ 改 CMCT Query + manifest 依赖重修 → doctor `_val_exclusive` 增加 Query 归一化识别 → **2026-10-04 重启实证：0 patch Ignored、ERROR 0、WARN 84→81（恰少 3 条 Ignored）**。

### 28. 模组 manifest 带注释——标准 JSON 解析必炸，剥注释+尾逗号再读

现象：`json.loads` 报 `Expecting property name enclosed in double quotes` / `Expecting ',' delimiter`——本环境 **37/152** 个 manifest.json 直接解析失败。

**原因**：ModManifestBuilder 等工具生成的 manifest 含 `/* */` 块注释与**行尾 `//` 注释**（GMCM、Lumisteria 图块集、V1cty 立绘、熊家-ES 等）；JSON 标准不容忍注释，但 SMAPI 用的 Newtonsoft 容忍，所以游戏里加载正常——**脚本读 manifest 会炸，游戏不会**。

**正确做法**：解析前依次剥：① `/* */` 块注释 → ② 行尾 `//` 注释（必须**引号感知**，否则误伤字符串里的 URL `https://`）→ ③ 尾逗号，再 `json.loads`：

```python
# 完整实现见 发布\build-release.py 的 _strip_line_comments / _loose_json
text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)   # 块注释
text = _strip_line_comments(text)                    # 行尾注释（状态机判引号）
text = re.sub(r",(\s*[}\]])", r"\1", text)           # 尾逗号
```

> 实例（2026-10-04 第十场）：`build-release.py` 生成 mod-manifest.csv，37 个失败 → 宽松解析后 **0 失败**，剩 16 个是真没有 manifest（目录级合并项）。

---

## 六、常用工具与位置

| 工具 | 位置 | 用途 |
|---|---|---|
| **dnSpy** | `D:\Tools\dnSpy\dnSpy.Console.exe` | 反编译 .NET DLL（**不在 PATH**，用绝对路径） |
| **7-Zip** | `C:\Program Files\7-Zip\7z.exe` | 解压/校验（`7z t` 测完整性） |
| **dnfile** | Python 库 | 读 .NET 元数据、验证 DLL 结构完整性 |
| **SMAPI 日志** | `%APPDATA%\StardewValley\ErrorLogs\SMAPI-latest.txt` | 唯一权威的运行证据 |

> dnSpy 用法：`dnSpy.Console.exe -o 输出目录 目标.dll`（输出含 .csproj，可直接 VS 打开）

---

## 七、判定「是不是真问题」的方法

**优先看 SMAPI 日志**，它记录实际发生的事：

| 日志级别 | 含义 |
|---|---|
| **ERROR** | 真问题，必须处理 |
| **ALERT** | 通常只是「有更新可用」 |
| **WARN** | 多为正常提示（如 SpaceCore 改存档序列化器） |

### 已核实的「假问题」（不用管）

- **10 条「Nexus mod ID 无效」**：SVE / East Scarp / RSV / Frontier Farm 的子组件，作者**故意**填 `Nexus:???` 关闭更新检查。副作用是这些子组件收不到更新提醒。
- **SpaceCore「changed save serializer」警告**：正常提示，但**不可卸载 SpaceCore**（卸了存档打不开）。
- **派大星马内容补丁语法过时**：CP 已自动迁移，功能正常。

### 读「Can't apply data patch」类黄字：三分支定位法（2026-10-01 黄字研究实战）

报错形如 `Can't apply data patch "… > EditData Data/Characters #N": the field 'X' doesn't match an existing target`，含义固定 = **补丁执行那一刻，目标键 X 不存在**。根因三选一：

1. **键大小写不匹配**（永久失败，与时机无关）：行存在但拼写不同。实例：Avian 写 `Sens`、影子人创建 `SenS`，.NET 字典区分大小写 → 查不到。**先逐字对两边的确切字符串**。
2. **创建者补丁被静默跳过**（最隐蔽）：创建行的 `Entries` 若含 save 依赖 token（`Relationship:*`、`{{spouse}}` 查询等），启动期 token 未就绪 → **CP 的 `IsReady=false 直接返回、不打任何日志**（`UnreadyTokens`/`AddUnreadyToken` 方法名实证 + 三创建者 0 WARN 旁证）。**0 WARN ≠ 补丁成功**。
3. **创建包没装**：grep 全 Mods `"Target": "Data/…"` 找不到创建者。

**排查步骤**：

1. grep 目标资产（如 `Data/[Cc]haracters`）列全部 patch，分清三类：`Load`（全量替换，最危险）、`Entries`（创建行）、`TargetField`（改已有行）；
2. 对创建者读其 Entries 里的 `{{...}}` token → 查定义与就绪条件：**i18n / ConfigSchema 立即就绪；`Relationship:` / `Query spouse` 需存档**；
3. 找一个**成功**的同类 patch 做对照——token 差异即根因（实例：Meredith 只用 i18n/config token → 成功；Rodney 多 `{{RodneyDatability}}` → 失败）；
4. **加载序（SMAPI TRACE）只是排除项，不是证据**——先查加载序排除顺序问题，再查 token（本次实测创建者全部先于 Avian 加载，顺序假设被推翻）。

**×2 现象**：同一警告成对出现在两个时间点 = 该资产被加载两次（启动 + 进档），CP 各 apply 一次，属正常时序，不是重复报错。

> 实例：2026-10-01 整合包 74+32 条黄字研究，详见 [整合包环境-使用记录.md](整合包环境-使用记录.md) 文末「黄字根因研究」段。

---

## 八、MOD 更新后的注意事项

以下汉化**会因 MOD 本体更新而丢失**，需重打：

| MOD | 汉化方式 | 重打方法 |
|---|---|---|
| Xtardew 三件套 | 直接替换 `content.json` | 覆盖 content.json + Dialogue 文件夹 |
| MailServicesMod | 改 DLL（等长替换） | 重做 52 串替换 |
| PolyamorySweet 兰塔娜 | 替换 `content.json` + Dialogue | 覆盖 3 个文件 |
| VALLEY GIRLS 事件 | 替换 `Events.json` / `MarriageEvents.json` | 覆盖 2 个文件 |
| 各 MOD 的 i18n | 加 `i18n/zh.json` | 若更新只覆盖 MOD 自带文件，zh.json 通常在，需确认 |

---

## 九、怎么查原版贴图的真实尺寸（判断「帧号越界」类 bug 的基准）

**问题**：MOD 替换 `Characters/<NPC>`、`Portraits/<NPC>` 时，如果新图比原版**矮**，越界帧会画出空白（NPC 站着不动）；如果比原版**高**，一般是安全的（动画帧追加在下方）。所以必须知道**原版到底多大**。

**方法（不需解压 xnb）**：XNB 头里有未压缩长度，纹理按 4 字节/像素存储，头部开销实测恒为 **177 字节**：

```
像素数 = (usize - 177) / 4
角色图宽 = 64   → 高 = 像素数 / 64
立绘宽  = 128  → 高 = 像素数 / 128
```

```python
import struct
d = open(path, 'rb').read()
usize = struct.unpack('<I', d[10:14])[0]      # XNB 头偏移 10
px = (usize - 177) // 4
print(px // 64)                                # Characters 的高（每行 4 帧 × 16px = 64）
```

**已验证的常数依据**（2026-10-01）：用同一公式反推 `Maps/townInterior` 得 512×1088、`Maps/DesertTiles` 得 256×368、`Maps/Festivals` 得 512×512，与 MOD 提供的**整表替换图**尺寸逐张精确吻合 → 公式和 177 这个常数是对的。

### 原版 1.6 实测尺寸（供比对，勿再凭记忆）

| NPC | Characters | Portraits |
|---|---|---|
| Abigail | 64×448 | 128×320 |
| Emily / Sam / Harvey | 64×448 | 128×256 / 128×384 / 128×384 |
| Haley / Leah / Penny | 64×416 | 128×448 / 128×320 / 128×448 |
| Alex / Elliott / Shane | 64×416 | 128×384 / 128×320 / 128×384 |
| Sebastian | 64×480 | 128×320 |
| Caroline / Jodi | 64×224 | 128×128 / 128×192 |
| Marnie / Pam / Robin | 64×288 / 64×320 / 64×320 | 128×192 / 128×192 / 128×256 |
| Sandy / Krobus | 64×160 / 64×144 | 128×128 / 128×320 |
| Clint / Demetrius / Kent | 64×352 / 64×256 / 64×160 | 128×256 / 128×256 / 128×192 |
| Lewis / Gus / Willy / Wizard / Marlon / Pierre | 64×256 / 224 / 352 / 192 / 128 / 224 | 128×192 / … / 128×128 |

**整表类**：`Maps/springobjects` = 384×624（24 列 × 39 行，936 个物品格）、`Maps/townInterior` = 512×1088、`Maps/Festivals` = 512×512、`Maps/DesertTiles` = 256×368。

> 实例：2026-10-01 核对整合包拓展的成人 MOD 时，发现文档里"原版 Haley = 64×672 = 84 帧"是错的（实际 64×416）；同一批核对确认 Nude Girls 的 26 张核心贴图**与原版逐张一致**，Horny Bachelors 的男性贴图**全部 ≥ 原版**。

### 三种替换方式的风险差别

| CP Action | 效果 | 风险 |
|---|---|---|
| `Load` | 整张资源替换 | 新图比原版**小** → 后面的帧全废；也会**盖掉**之前所有包对这张图的 `EditImage` |
| `EditImage`（带 ToArea/FromArea） | 只贴一块 | ToArea 超出原版尺寸 → 可能被静默忽略 |
| `EditImage`（不带区域） | 整张替换（同 Load） | 会**抹掉**其他包（含山谷女孩/Xtardew）对同一张立绘的局部修改 |

**判断两个包会不会互踩**：先看它们对同一条 `Target` 用的是 `Load` 还是 `EditImage`，再看**加载顺序**（见下条）。

## 十、SMAPI 的 MOD 加载顺序不是字母序

**实测**（2026-10-01，读整合包环境上次启动日志）：SMAPI 按**文件系统枚举顺序**加载，**不做排序**。日志里 `LetsMoveIt` 夹在 `【前置】内容补丁`、`【前置】生产者框架` 之间，ASCII 目录名与中文目录名交错 → 不是字母序，也不是"中文最后"。

**后果**：两个包改同一张 `Target` 时，谁后加载谁生效，**无法靠文件夹命名可靠控制**。

**正确做法**：装完启动一次，在 `%APPDATA%\StardewValley\ErrorLogs\SMAPI-latest.txt` 里定位 `Loading mods...` 段，按 `(from Mods\<文件夹>\...)` 抽取真实顺序，确认新包落在预期的位置；不符合预期就改文件夹名再验证。

> 同日实测：装整合包拓展的成人 MOD 时，日志里的顺序是 `CJBItemSpawner → FastAnimations → GenericModConfigMenu → GameSpeedToggle → 【前置】内容补丁 → LetsMoveIt → …`，足以证伪"按名字排序"的假设。

### ⭐ 补充规则（2026-10-01 实测，非常重要）：`Load` 永远先于 `EditImage` 执行

**不是**"谁后加载谁生效"，而是**分两轮**：

1. **第一轮**：所有对该资源的 `Load` 补丁（整体替换）先执行；
2. **第二轮**：所有 `Edit*` 补丁（局部修改）再按内容包顺序执行。

**日志实证**：`HornyBachelors` 在加载顺序里排 **134**，`【优化】去除弓形腿` 排 **37**、`【山谷女孩】行为设置` 排 **112**，但日志里的执行顺序是：

```
Content Patcher loaded asset 'Characters/Harvey' (for the 'HornyBachelors' content pack).
Content Patcher edited Characters/Harvey (for the '【优化】去除弓形腿' content pack).
Content Patcher edited Characters/Harvey (for the '【山谷女孩】行为设置' content pack).
```

→ 后加载的包**不会**把自己的 `Load` 插到前面去；`Load` 是打底，`Edit` 是叠加。

**推论（判断覆盖关系时的正确算法）**：

| 场景 | 谁生效 |
|---|---|
| A 包 `Load` + B 包 `Edit` 同一资源 | **A 打底，B 叠加** —— 与包顺序无关 |
| A 包 `EditImage` + B 包 `EditImage` 同一资源 | 按内容包顺序，**后面的盖前面的** |
| **A 包、B 包都 `Load` 同一资源** | 🔴 **CP 把 `Load` 视为 `Exclusive`（独占）优先级 → 两个都不生效，退回游戏原版**，并在日志里记一条 **ERROR**：<br>`Two content packs want to load the 'X' asset with the 'Exclusive' priority (A and B). Neither will be applied.` |

> ⚠️ **2026-10-01 更正**：早先本节曾写"本环境没有两个包 Load 同一资源"——那是**只看启动日志得出的错误结论**（资源是按需加载的，启动时没被请求的资产看不出冲突）。正确做法是**静态扫描全部内容包的 `Load` 目标**（脚本：`_暂存-整合包拓展\scripts\scan-load-conflicts.py`），实测本环境有 **3 处**：
>
> | 资源 | 冲突双方 | 触发条件 |
> |---|---|---|
> | `Characters/Wizard` | HornyBachelors × 【NPC-女法师附加】浪漫关系解锁-SVE兼容 | 恒触发（两者都有无条件分支）→ 已通过**移除 HB 的巫师补丁**修复 |
> | `Maps/Festivals` | 【成人】单身汉 × 【成人】淫乱节日 | 仅当开启「刘易斯颁布裸体法律」**且**恰逢淫乱节日的日期 |
> | `Maps/night_market_tilesheet_objects` | 【成人】单身汉 × 【地图美化】DaisyNiko's低饱和度大地 | 仅当开启「刘易斯颁布裸体法律」 |
> | `Portraits/Wizard_Beach` | 【NPC】女法师 × Xtardew Portraits&Sprites | **装前就存在的旧冲突**，与本次安装无关 |
>
> **排查口诀**：两个包同时 `Load` 一张图 → 一定出事；一个 `Load` 多个 `Edit` → 没事。

**实例**：Horny Bachelors 把 `Characters/Wizard` **整表替换**（男性版），而「女法师 RomRas」和「Xtardew」对该资源是 `EditImage`（贴女性版）→ 因为 Load 先执行，**女法师的女性贴图仍然叠得上去，不会被顶掉**。若按"包顺序"推断就会得出相反的错误结论。

**但真正的坑在这里（2026-10-01 实战踩到）**：「女法师附加包」也 `Load` 了 `Characters/Wizard`（用来切换 vanilla / new 精灵图）→ 与 Horny Bachelors 的 `Load` **同为 Exclusive** → CP 判两个都不生效。**结果**：底图退回原版男巫师，然后 RomRas 的 `EditImage`（女性贴图）照常叠上去 → **玩家看到的仍是女法师**，所以肉眼完全看不出问题，只有日志里多一条 `ERROR Content Patcher`。

**教训**：
1. 可见效果正常 **≠** 没有冲突——CP 的 Exclusive 冲突是**静默降级**成原版，容易被 `Edit` 补丁补救回来；
2. 只读启动日志不足以发现冲突（资源按需加载），要**静态扫全部内容包的 `Load` 目标**；
3. 排查时优先 grep 日志里的 `Two content packs want to load`。

> 同理可解释：HB 的裸体男性贴图（`Load`）打底，山谷女孩/NTR 与去除弓形腿的 `Edit` 叠在上面 —— 裸体不会被"加回衣服"。

**注意**：`Load` 的图**比原版小**才会砍帧（见第九节）；比原版大是安全的（HB 的 Wizard 角色图 64×256 vs 原版 64×192，立绘 128×128 vs 原版 128×64）。
