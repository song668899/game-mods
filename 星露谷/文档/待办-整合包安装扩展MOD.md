# 待办：给整合包环境安装成人 MOD（玩法类）

> **状态**：✅ **已于 2026-10-01 安装完成**（8 个新组件 + 山谷女孩改造），**等待启动验证**。安装记录见 [整合包环境-使用记录.md](整合包环境-使用记录.md) 第八节；本文继续作为**逐包档案 + 风险分析**保留。
> **目标环境**：`D:\星露谷MOD\游戏`（整合包环境，非 Steam 环境）
> **下载包位置**：`D:\星露谷MOD\整合包拓展\`（12 个压缩包，含 NTR 汉化包）
> **分析用暂存目录**：`D:\星露谷MOD\_暂存-整合包拓展\`（解压结果 + 分析脚本 + 安装器，可随时删除）
> **记录日期**：2026-10-01
> **接手须知**：第四节「风险评估」与第五节「硬性纪律」对**以后再加 MOD** 仍然适用。

---

## 一、用户的需求（原话归纳）

> 想给**整合包环境**安装一些**成人 MOD**，**主要是玩法类，不要美化类**。

**已明确的边界**：

| 要 | 不要 |
|---|---|
| ✅ 玩法类（系统机制、新事件、新 NPC、新恋爱线） | ❌ 美化类（立绘、肖像、服装、地图美化） |
| ✅ 装在整合包环境 | ❌ 不动 Steam 环境 |

**用户此前未采纳的建议**（记录备查）：
- 曾提议移植 Steam 独有的 13 个功能 MOD（跳过钓鱼、事件重复器等）→ **用户明确说"都不用安装"**
- 曾提议生成整合包版本快照 → 未回复
- 2026-10-01：用户表示"现在都不安装，先研究明白"

---

## 二、⚠️ 已知前提（动手前必读）

### 2.1 整合包**已有一套调好的成人 MOD 组合**

作者（师爷）已把 4 套成人内容**融合适配**过，它们是**互相调试过的整体**：

| 组件 | UniqueID | 版本 | 说明 |
|---|---|---|---|
| **Xtardew Core** | `hixega.XtardewCore` | 0.4.0 | **框架**（hixega 版，非 Pseudodiego 版） |
| **X露谷** | `Pseudodiego.XtardewValley` | 3.2.0 | SVE 版 |
| Xtardew P&S | `Pseudodiego.NudeNPC` | 0.1 | |
| XtardewValleyPolyLeah&Abigail | `Pseudodiego.LAtardewValley` | 1.0.0 | |
| **山谷女孩** | `Trashracc.VG` | 3.6.0 | 行为设置 |
| **女法师** | `Nom0ri.RomRas` | 3.4.2 | + `Parrot.RomRas` SVE兼容 1.6.3 |
| **甜蜜多角恋** | `ApryllForever.PolyamorySweet*` | 1.4.6 | 6 个组件（Bed/Kiss/Love/Rooms/Wedding/CP） |
| [MFM] Rasmodia Letters | `Nom0ri.RasmodiaMFM` | 1.0.0 | 女法师邮件 |

> 整合包作者自述：**X露谷这一个文件夹里融合了 7 个模块**（实验版、对话优化、原版立绘替换、实验版立绘替换、兼容补丁、X核心、两版汉化），是做好测试、文件融合的独立版本。

### 2.2 🔴 **两套环境的 Xtardew 是不同分支，不通用**

| | 整合包环境 | Steam 环境 |
|---|---|---|
| 版本 | hixega 的 **Xtardew Core** + 实验版融合 | Pseudodiego 的 **Xtardew Valley 3.2.0** |
| 特点 | 事件更多（含实验版扩展触发条件） | 标准版 + Poly Leah&Abigail |

**后果**：给 Pseudodiego 版做的成人 MOD，装到整合包**可能不兼容**。装前必须确认目标 MOD 面向哪个分支。

### 2.3 整合包的框架版本偏旧

| 框架 | 整合包 | 说明 |
|---|---|---|
| **Content Patcher** | **2.7.5** | 2025 年初版本，比 Steam 的 2.9.1 旧 |
| SpaceCore | 1.28.0 | |
| FarmTypeManager | 1.25.1 | |
| MEEP | 2.4.6 | |

**后果**：如果目标 MOD 要求 CP ≥ 2.8 或用了新语法，**装了会报错**。不要为了装它去升级 CP——会破坏整合包其他 168 个组件的适配。

### 2.4 用户已有存档

- 存档在 `%APPDATA%\StardewValley\Saves\`，**两套环境共用目录**
- 整合包存档**角色名「整合」**，用户已玩过新档，**游玩正常**
- Steam 存档角色名「富强」「文明」
- **存档靠角色名区分，不要混用**

> ⚠️ **成人 MOD 常改 NPC 好感度/关系数据**，卸载后残留可能坏档。装前**必须手动备份存档**（整合包环境**没有** `save-backups` 目录，SMAPI 自动备份不覆盖这里）。

---

## 三、已下载的 11 个包：逐个分析（2026-10-01 完成，未安装）

### 3.1 压缩包 → 组件对照表

| 压缩包（`整合包拓展\`） | 解出的组件 | UniqueID | 类型 |
|---|---|---|---|
| `Horny Bachelors-2564-1-6-5.zip` | `HB\` | `Girafarig.HB` | CP 内容包 |
| `Horny Bachelors - Chinese translation-30212-1-6-5.rar` | 汉化（content.json + i18n） | — | 翻译文件 |
| `Horny Festivals-10844-1-1-6.zip` | `HF\` + `FestivalWarps\` | `Girafarig.HF` / `Girafarig.FestivalWarps` | CP 包 + C# DLL |
| `Make Love-16003-2-0-0.zip` | `MakeLove\`（含 DLL + 12 个 NPC 贴图 + 模板） | `Kabulla.MakeLove` | C# DLL |
| `MakeLoveChinese-33949-1-0.zip` | `zh.json` | — | 翻译文件 |
| `MakeLove SVE Characters-34516-1-0-0.zip` | `[ML] SVE Characters\` | `Kabulla.SVEML` | ML 内容包 |
| `Make Love with SVE Bachelors chinese-34532.rar` | `zh.json` | — | 翻译文件 |
| `Amorous Valley-23588-0-4-0.zip` | `[CP]AmorousValley\` | `beepbopdubi.AmorousValley` | CP 内容包 |
| `Affairs with Married Women 41020 1.32.zip` | `Affairs with Married Women\`（自带 zh） | `Luxi1234.AnAffairwithRobin` | CP 内容包 |
| `Nude Girls-20277-2-0-0.zip` | `[CP] NUDE GIRLS\` | `Trashracc.NudeGirls` | CP 内容包（美化类） |
| `NetorareValley 40559 0.2.9.zip` | `[CP] VALLEY GIRLS\`（**无 manifest**） | — | 山谷女孩覆盖包 |

**共性结论**：11 个包里只有 7 个是可安装组件，另有 3 个汉化文件、1 个**作者模板**（不能装，见 3.4）。
**依赖检查**：所有组件的 `MinimumApiVersion` ≤ 4.5.2 ✓；必需的 `FlashShifter.StardewValleyExpandedCP`（SVE 1.15.11）已在整合包内 ✓；唯一"缺失"的 `Kabulla.MakeLove` 正是本次要装的 Make Love 本体。

---

### 3.2 逐包档案

#### ① Horny Bachelors（`Girafarig.HB` 1.6.5）—— 男性裸体 + 新对话 + 新日程

- **内容**：271 个 Change。给男性 NPC 换裸体贴图（`Load` 覆盖 `Characters/*` 与 `Portraits/*`），新增 **29 个 NPC 的对话**（含 Sam/Sebastian/Shane/Harvey/Elliott/Alex 的**婚后对话**）、**9 个 NPC 的日程**（去澡堂男更衣室/家里自慰）、4 个**原版节日**的裸体版本、澡堂与酒吧与镇内景（`Maps/Hospital`、`Maps/Saloon`、`Maps/townInterior`）与电影院贴图、`LooseSprites/Cursors`；新增 13 种物品 `hb.*cum`（有中文名/描述，可送礼）。
- **触发**：日程驱动 + 对话/事件；多个开关控制开关。
- **开关（12 项，括号内为默认值）**：单身汉打飞机（**开**）、其他男人也打飞机（**开**）、新对话（**开**）、单身汉偶尔"勾搭"（**开**）、刘易斯颁布裸体法律（关）、冬天也裸体（关）、农夫是否裸体（否）、农夫是否割包皮（是）、亚历克斯穿衬衫（关）、三位大叔阴毛（**开**）、裸体沙滩装（关）、裸体海盗部落（关）。
  → **默认就有 4 项是开的**，装上即生效，不是"静默包"。
- **节日改动**：`Data/Festivals/{spring24, summer11, fall16, winter8}`（花舞节 / 夏威夷宴会 / 星露谷博览会 / 冬日星盛宴）。
- **依赖**：Content Patcher ≥ 2.0.0（现有 2.7.5 ✓）；**不依赖 SVE**。
- **汉化**：另发的汉化包，做法是**整体替换 content.json** 并新增 `i18n/{default,zh}.json`（16 键，翻的是 CP 的 `config.*` 选项名）。抽样核对：本体 271 个 Change / 162 个 Target 与汉化版**一一对应**，ConfigSchema 12 个字段名与默认值**完全一致**。
- **⚠️ 坑**：本体 `content.json` 用的是 **SMAPI 宽松 JSON**（`{0: "文本"}` 键名不带引号，还有重复键），Python 标准 `json` 会直接解析失败；**汉化版是标准 JSON**。以后做文本比对要先想到这点。
- **冲突**：与 **27 个**现有包存在同名资源。最重的：`【立绘】Veronnica's 原版立绘`（44 个，HB 是 `Load`、Veronnica 是 `EditImage`）、`【大型拓展】ES\[CP] East Scarp NPCs`（23 个对话）、`爷爷的农场`（23 个对话）、`【优化】去除弓形腿`（男性 `Characters/*`）。

#### ② Horny Festivals（`Girafarig.HF` 1.1.6 + `Girafarig.FestivalWarps` 1.1.6）—— 4 个新节日

- **两个组件**：`HF`（CP 包，18 个 Change）+ `FestivalWarps`（C# DLL，"给节日加传送点，让你能离场"）。
- **4 个新节日**（`Data/Festivals/{spring19,summer20,fall12,winter13}` 整文件 Load）：

| 节日 | 名称 | 地点 / 时间 |
|---|---|---|
| spring19 | Virility Festival | 森林 9:00–14:00 |
| summer20 | Fuck Fest | 海滩 8:00–18:00 |
| fall12 | Phallic Celebration | 镇上 8:00–18:00 |
| winter13 | Day of Carnality | 种子店 9:00–18:00 |

- **商店**：spring19 里卖 13 种 `hb.*cum` 物品（1000–10000 金）→ **功能上依赖 Horny Bachelors 的物品定义**（manifest 里没有声明这个依赖！单装 HF 会出现卖不存在的物品）。
- **自绘地图**：`Woods_Fest` / `Beach_Fest` / `Town-Phallus` / `SeedShop-Fest` / `CommunityCenter_Refurbished-Fest`，并替换 `Maps/Festivals` 贴图（含 phallic / virility 变体）。
- **汉化**：❌ 无（节日名、对话、商店全英文）。
- **冲突**：与 8 个现有包同名——`Maps/Town`（EditMap，与 ES / 朱丽叶同 Target）、`Maps/Festivals`（与 `DaisyNiko's低饱和度大地`，HF 是 Load 而后者是 EditImage）、`Data/Shops`（与甜蜜多角恋 / HxW 家具目录）。

#### ③ Make Love（`Kabulla.MakeLove` 2.0.0，C#）+ [ML] SVE Characters

- **机制（已反编译确认）**：Harmony patch `NPC.checkAction`。**对已注册 NPC 右键交互**即触发，需同时满足：好感 ≥ **8 心**（GMCM 可调）、**正在交往**（`IsDating`，可关闭该要求）、NPC 静止/无对话/无临时消息/玩家手上没拿东西、NPC 面向 1 或 3。
- **GMCM 3 项**：`Disable Dating Requirement`（关）、`Required Friendship Level`（8）、`Add ending dialogue`（开）。
- **内容**：原版 12 个 NPC（Abigail/Emily/Haley/Leah/Maru/Penny/Sam/Sebastian/Alex/Harvey/Shane/Elliott）各自的 `<名字>_Love.png` 贴图 + 场景帧定义（standing / oral，主动或被动），事后对话 41 条。
- **`[ML] SVE Characters` 1.0.0**：给 SVE 的 **Olivia / Claire / Sophia / Victor** 加同样内容；依赖 `Kabulla.MakeLove ≥ 2.0.0` + SVE。
- **汉化**：✅ 两个 `zh.json`（41 键 / 18 键），与本体 `default.json` 的键集合**完全相同（0 缺 0 多）**，可直接放 `i18n\zh.json`。
- **冲突**：几乎为零——它新增 `Characters/*_Love` 资产，不覆盖现有资源。与甜蜜多角恋天然互补（能同时交往多人）。

#### ④ Amorous Valley（`beepbopdubi.AmorousValley` 0.4.0）

- CP 包，17 个 Change：13 张自定义角色贴图 + 4 个事件（`Data/Events/{HaleyHouse, ArchaeologyHouse, Beach, SeedShop}`）。
- **事件**：海莉按摩（多阶段 `quickQuestion` 选择 Shoulders/Waists/Legs/Ass/Pussy，分 3 轮递进）、海莉海滩、佩妮（含 Gunther）、阿比盖尔。
- **汉化**：❌ 无，事件内 `message` 全英文。
- **冲突**：5 个现有包同名 Target（Xtardew 的 `ArchaeologyHouse`/`HaleyHouse`、Mr. Ginger、地质学家等），但**事件 ID 不冲突**（新 ID 为 56742530 / 56742531 / 56742532）。

#### ⑤ Affairs with Married Women（`Luxi1234.AnAffairwithRobin` 1.32）—— 三条人妻线

- CP 包，138 个 Change，**61 个事件**，实为**三条独立故事线**：

| 线 | 事件键 | 涉及角色 | 主要地点 |
|---|---|---|---|
| **罗宾线** | `LuxiRobin1–16` + `LDemetrius1–3` | Robin / Demetrius / Maru / Sebastian / Lewis | 科学屋、山顶、铁路、镇上、农场 |
| **乔迪线** | `Luxijodi1–12` | Jodi / Kent / Vincent / Jas / Marnie / Caroline / Pierre / Abigail | 山姆家、镇上、皮埃尔商店、酒吧、铁路 |
| **卡罗琳线** | `LuxiCaroline1–10` | Caroline / Pierre / Abigail / Clint | 皮埃尔商店、公交站 |

- 附带：任务 `Robin1`/`Robin2`、邮件 4 条（`Demetrius1.2/1.3`、`Ljodimail1.2/1.4`）、新物品 `yang`/`mifang`、`Maps/Town` EditMap。
- **依赖**：**SVE 必需**（已装 1.15.11 ✓）。
- **汉化**：✅ 自带 `zh.json`，1101 键**全部中文**（A/B 两套命名空间，事件脚本分别引用；英文原文 1046 条纯英文 → 中文 1068 条含中文、**0 条残留英文**）。
- **冲突**：**无事件 ID 冲突**；与【立绘】Veronnica 等 6 个 `Portraits/*` EditImage 重叠；`Maps/Town` EditMap 与 ES、朱丽叶同名。

#### ⑥ Nude Girls（`Trashracc.NudeGirls` 2.0.0）—— ⚠️ 美化类

- CP 包，19 项配置，**全部默认关闭（OFF / false）**：每个女性 NPC 一个 `Nude <名字>`（Overworld / Island / Both / OFF）、`Nude Aerobics`（周二健美操）、`Lewd Krobus`、`Nude Mermaids`，外加地点白名单（Farm/Town/Beach/…，含山谷女孩的 `Custom_BathroomVG`）与天气/季节条件。
- **不手动开启 = 零效果**（这一条已核实：全部 EditImage 都带 `When` 条件）。
- **依赖**：可选 `Poltergeister.SeasonalCuteCharacters`（**未装**）、可选 `Poltergeister.SeasonalCuteSpritesSVE`（已装 3.0.0）。
- **冲突**：`Portraits/Krobus`（与 Veronnica）、`LooseSprites/temporary_sprites_1`（与 DaisyNiko 低饱和大地）。
- **汉化**：无 zh.json，仅 1 条对话文本。
- **性质**：这是**纯外观**包，与用户"不要美化类"的要求直接冲突 → 见第六节待确认。

#### ⑦ NetorareValley（`40559` 0.2.9）—— 🔴 高危：必须覆盖山谷女孩

- **无 `manifest.json`**（7z 完整性校验 `Everything is Ok`，确认不是解压丢失）→ 作为独立 MOD **根本无法加载**。
- **证据链（证明它是山谷女孩的改装版，而非独立新增包）**：
  1. 它引用了 115 个贴图/地图，其中 40 个本包没有；**34 个全部能在现有 `【大型拓展】山谷女孩` 里找到，两边都没有的 = 0**；
  2. 与现有山谷女孩**重叠 38 个 Target**（几乎全部），ConfigSchema 是 VG 3 字段的**超集**；
  3. i18n 是 VG 的**严格超集**（VG 的 192 键全含，另加 6523 键）；
  4. 事件 ID 与 VG 完全同一批（10536–10569 等）。
- **内容**：山谷女孩 3.6.0 的全部内容 + **NTR / NTS 剧情** + Emreld 的 *Unfaithful Valley Girls – MILFs and Poly Addon*（作者描述里自陈）。事件指南 121 条，按 NPC 分「First Time / First Time NTR / Second Time / NTS / Second NTS / Find out NTR / Repeatable NTR / Demetrius NTR / MMF / Poly」，含 incest 警告标注；另有 NTR 专属浴室地图与 `NetorareValleyPolyEvents.json`（529 KB，与甜蜜多角恋联动）。
- **新增 7 个开关**：`Cheating` / `Incest` / `Blacked` / `Lesbian` / `Threesome` **默认全部 On**、`Mode`（StoryMode / HoeMode）、`Testing`（Off）。
- **汉化**：✅ **已有汉化包**（用户 2026-10-01 下载 `VALLEY GIRLS 53132 1.rar`，核对结果见 3.6）：6715 键全中文，另附中文版事件指南。原包自带的英文 `i18n/default.json` 仍保留作回退层。
- **代价**：覆盖安装会**顶掉现有山谷女孩**，与本文第四节"绝不覆盖"纪律正面冲突（可整目录备份回滚）。

---

### 3.3 三个汉化包（都是"文件覆盖"式，不是独立 MOD）

| 汉化包 | 放到哪 | 核对结果 |
|---|---|---|
| Horny Bachelors 汉化 1.6.5 | 替换 `HB\content.json` + 新增 `HB\i18n\{default,zh}.json` | 版本号一致（1.6.5）；271 个 Change / 162 个 Target 一一对应；ConfigSchema 12 字段一致 ✓；**文本类字符串中文化率 ~100%**（余下 39 条是动画帧序列/资源路径，不是给人看的文本）✓ |
| MakeLoveChinese | `MakeLove\i18n\zh.json` | 41 键，与 `default.json` 键集合完全相同 ✓ |
| Make Love with SVE Bachelors chinese | `[ML] SVE Characters\i18n\zh.json` | 18 键，与 `default.json` 键集合完全相同 ✓ |

### 3.4 ❌ 不能装的东西

- `MakeLove\ContentPackTemplate\[ML] Love with Jodi\`：**作者模板**，UniqueID 还是占位符 `YourName.YourModName`，装了只会报依赖错误。

### 3.5 兼容性硬检查结果（2026-10-01，逐项实测）

| 检查项 | 结果 |
|---|---|
| **UniqueID 重复** | ✅ 无（与现有 169 个组件零重复） |
| **manifest 声明的依赖** | ✅ 全部满足（`Kabulla.MakeLove` 缺失项正是本批要装的） |
| **`MinimumApiVersion`** | ✅ 全部 ≤ 4.5.2 |
| **Content Patcher Format** | ✅ 最高 2.4.0（HF/HB/Nude Girls 2.0.0、Affairs 2.3.0、NTR 2.4.0），≤ 现有 CP 2.7.5 支持范围 |
| **C# 程序集目标框架** | ✅ `MakeLove.dll` / `FestivalWarps.dll` 目标 `.NETCoreApp v6.0`（与 SMAPI 4.5.2 一致），引用 API 正常 |
| **事件 ID 冲突** | ✅ 零（Affairs 61 个、Amorous 26 个，与整合包内全部 9 个含 `Data/Events` 的包无交集） |
| **数据表键级冲突** | ✅ 零（逐张比对 `Data/Objects`、`Data/Mail`、`Data/Quests`、`Data/Festivals`、`Data/Shops`、`Strings`、`Schedules`…）——**唯一例外是 NTR vs 现有山谷女孩（30 个同名键）** |
| **贴图尺寸** | ✅ 见下 |

**贴图尺寸逐张核对**（基准来自原版 xnb 反推，方法见 `技术笔记` 第九节）：

- **Nude Girls**：26 张核心贴图（13 个女性 NPC 的 `Characters` + `Portraits`）**与原版尺寸逐张完全一致（0 处不符）** → 不会帧号越界，也不会打乱其他包对同一张表的区域修改。
- **Horny Bachelors**：男性 `Characters/*` 全部 **≥ 原版**（如 Alex 原版 64×416 → HB 64×736，多的帧追加在下方），`Portraits/*` 同理 → 不砍帧。
- **整表替换**：HB 的 `Maps/springobjects` = 384×640（原版 384×624，多一行）、`Maps/townInterior` 512×1088、`Maps/DesertTiles` 256×368 均与原版一致或更大；HF 的 `Maps/Festivals` 512×512 与原版一致。

**⚠️ 唯一"manifest 没写、但功能上必须有"的依赖**：**Horny Festivals → Horny Bachelors**。HF 的节日商店卖 `hb.alexcum` 等 13 种物品，这些物品由 HB 的 `Data/Objects` 定义。单独装 HF 会出现卖不存在的物品。**两者必须同装。**

#### 依赖核对明细（2026-10-01 逐条带版本号比对）

| 新组件 | 依赖 | 要求 | 整合包现状 | 结论 |
|---|---|---|---|---|
| Horny Bachelors | Content Patcher | ≥ 2.0.0 | 2.7.5 | ✅ |
| Horny Festivals | Content Patcher | ≥ 1.10.1 | 2.7.5 | ✅ |
| FestivalWarps | 无 | — | — | ✅ |
| Make Love | GMCM（可选） | ≥ 1.3.1 | 1.16.0 | ✅ 配置菜单可用 |
| [ML] SVE Characters | Kabulla.MakeLove（必需） | ≥ 2.0.0 | 本批同装 2.0.0 | ✅ |
| [ML] SVE Characters | SVE（必需） | ≥ 1.0.0 | 1.15.11 | ✅ |
| Amorous Valley | Content Patcher | — | 2.7.5 | ✅ |
| Affairs with Married Women | SVE（必需） | — | 1.15.11 | ✅ |
| Nude Girls（本次不装） | SCC / SCC-SVE（可选） | — | 均未装 / SVE 版已装 | △可选 |

**隐式依赖（manifest 未声明，靠资源名能查出来）**：

- Horny Festivals 引用 `hb.*` 物品 ×26 处 → 需要 HB（**同批安装**）✅
- Affairs 引用 `Custom_SVESummit` / `Custom_E0xx` 等 SVE 自定义地点 ×31 处 → SVE 已装 ✅
- NetorareValley 引用 34 个只存在于现有山谷女孩的贴图/地图 → 山谷女孩已装 ✅
- Amorous Valley：未发现对外部 MOD 资源的引用 ✅

#### ⚠️ 缺口：可选依赖 `misscoriel.eventrepeater`（Event Repeater）未装

- NTR 与现有山谷女孩的 `content.json` 顶层都有 **`"RepeatEvents": [...]`** 列表（NTR 列了 30+ 个事件 ID）。
- **该字段不是 Content Patcher 的**（已在 `ContentPatcher.dll` 里查证：`RepeatEvents` 命中 0 次）；它由 **Event Repeater**（Nexus 3642）消费——作者文档写明"在你的 CP mod 的 content.json 里加 `RepeatEvents` 即可"。
- 整合包**没有装** Event Repeater，所以这份列表目前是**空转**的：NTR 里标注为 *Repeatable* 的场景（酒馆/海滩重复场景、各 NPC 的 Repeatable NTR、卧室重复场景）**不会重复触发，只能各看一次**。
- 影响级别：**不影响加载、不报错**，只是少了"重看"功能。

**✅ 已解决：本机就有货，不用去 N 网下**

| 来源 | 情况 |
|---|---|
| **Steam 环境已装** | `D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods\EventRepeater\` —— v**6.6**，`.NETCoreApp v6.0`，`MinimumApiVersion 2.10.0`（≤ 4.5.2 ✓），无任何依赖 |
| **仓库压缩包** | `01-框架MOD\Event Repeater-3642-6-6-0-1759598447.zip`（Nexus 3642，v6.6）—— **DLL 与 Steam 版 MD5 完全一致**（52 736 字节） |
| 两版差异 | 只有 `i18n\zh.json`（Steam 版的译文更地道）和 Steam 版多一个 `config.json`（键位）；`manifest.json` 仅差 BOM |

**建议**：直接用 **Steam 版整个文件夹**（DLL 同源，中文更好，带键位配置）。

**⚠️ 键位提醒**：Event Repeater 默认键位是 `LeftAlt + S`（普通跳过）、`LeftControl + S`（紧急跳过）、`LeftControl + I`（显示信息）；而整合包已把**左 Alt** 单独绑定给"快速堆叠/锁定物品"。组合键与单键理论上可共存，但如遇误触发，改 EventRepeater 的 `config.json` 即可。

**顺带扫描结论**：把本批 7 个新组件的全部依赖（含可选）对着两套环境都过了一遍，**除 Event Repeater 外没有别的缺口**。Steam 版另有 `Poltergeister.SeasonalCuteCharacters 6.1.3`（山谷女孩的另一个可选依赖），但那属美化类、且只是可选，**不建议**为它引入。


#### 补充修正：现有山谷女孩实际改的资源比我先前统计的多

从上次启动日志逐条抓取「Content Patcher edited XXX (for the '山谷女孩' pack)」得到实际清单：**67 个资源**，除了 10 位女性的 `Characters/*`、`Portraits/*`，还包括 **男性角色图**（`Characters/Alex`、`Sam`、`Sebastian`、`Harvey`、`Elliott`、`Shane`、`Pierre`、`Lewis`、`Demetrius`…）与 `Characters/schedules/*`。
先前用脚本扫 content.json 时低估了，因为 VG 的部分资源是通过**带 token 的 Include** 引入的，脚本无法展开。
**结论不变**（HB 的 `Load` 与 VG 的 `EditImage` 在男性角色图上重叠 → 谁后加载谁生效），但重叠面比先前所述更大，装后读日志这一步更必要。


**Nude Girls 会不会和现在的整合包冲突？**（本次专门查证）

| 面 | 结论 |
|---|---|
| 崩溃/报错 | ❌ 不会。图像尺寸与原版逐张一致，数据表无同名键 |
| 与 `Xtardew P&S`（`Pseudodiego.NudeNPC`） | ⚠️ **会互踩**：两者都改 `Characters/*` 与 `Portraits/*` 的女性 NPC。Xtardew P&S 用 `Load`（事件用裸体贴图），Nude Girls 用**整图 `EditImage`**（不带区域）→ 谁后加载谁覆盖谁 |
| 与 `【立绘】Veronnica's 原版立绘` | ⚠️ 同上（Veronnica 也是 `EditImage` 同一批立绘） |
| 与现有山谷女孩 | ⚠️ 同上（VG 用 `EditImage` 改同一批立绘，用于事件演出） |
| 默认状态 | ✅ **19 项开关全部默认关闭**，不手动开就没有任何效果；开启后仅对选中的 NPC + 地点 + 天气条件生效 |

→ 结论：**Nude Girls 不是"技术上不兼容"，而是"视觉上会和现有裸体/立绘包抢同一张图"**。它是整图替换，一旦开启，山谷女孩/Xtardew 在剧情里对该 NPC 立绘的局部修改可能被整张盖掉（或反之）。风险可控：默认关，想用就逐项开、出问题就关。

**用户决定（2026-10-01）：Nude Girls 暂不安装。**

### 3.6 NetorareValley 汉化包核对（`VALLEY GIRLS 53132 1.rar`，2026-10-01）

| 项 | 结果 |
|---|---|
| 压缩包 | `整合包拓展\VALLEY GIRLS 53132 1 2026-09-30T09-16Z Q8BPeyMTk.rar`（117 KB） |
| 内容 | `i18n\default.json`（629 875 字节）+ `z.NetorareValleyEventGuide.txt`（41 916 字节，中文版事件指南，原版 19 725 字节） |
| 键集合 | **6715 键，与 NTR 原包 `default.json` 完全一致**（0 缺、0 多） |
| 中文化率 | **97.9% 的键值含中文**；剩下 45 键是**事件脚本片段**（如 `$v AbigailNTS3 false false`）——那不是文本，本来就不该翻 → 实际等同 **100%** |
| 与现有山谷女孩 `zh.json` 的关系 | 现有 zh.json 的 192 键**全被新汉化包涵盖**，其中 160 键译文不同（新译文与 NTR 内容配套）→ 安装时应用新包**替换**旧 zh.json |
| 事件指南 | 有中文版，可一并替换英文原版 |

**建议装法**（覆盖 NTR 时一起做）：

1. NTR 的 `i18n\default.json`（英文，594 714 字节）**保留**
2. 把汉化包的同名文件**改名为 `zh.json`** 放进同一 `i18n\` —— 这样中文生效、缺键还能回退英文
   （若原样覆盖 `default.json`，就等于放弃英文回退层，功能上也行，只是丢了保险）
3. 覆盖掉旧山谷女孩的 `zh.json`（新包已含那 192 键）
4. 事件指南用中文版覆盖英文版

---

## 四、冲突与风险评估

### 4.1 逐包风险评级

| MOD | 类型 | 资源冲突面 | 汉化 | 风险 | 建议 |
|---|---|---|---|---|---|
| Horny Bachelors | 玩法+外观 | 与 27 个包同名资源（男性立绘/精灵图/对话） | ✅ 有 | 🟡 中 | 可装 |
| Horny Festivals | 玩法（新节日） | 与 8 个包同名；功能依赖 HB 物品 | ❌ 无 | 🟡 中 | 与 HB 同装 |
| Make Love + SVE 角色包 | 系统机制 | 几乎无重叠（新增 `*_Love` 资产） | ✅ 有 | 🟢 低 | 可装 |
| Amorous Valley | 新事件 | 与 5 个包同名 Target，**事件 ID 不撞** | ❌ 无 | 🟢 低 | 可装 |
| Affairs with Married Women | 新事件（3 条线） | 与 13 个包同名 Target，**事件 ID 不撞** | ✅ 全中文 | 🟢 低 | 可装 |
| Nude Girls | 纯外观 | 与 2 个包同名 Target；**尺寸与原版逐张一致**，不会像 VG 那样帧号越界 | — | 🟢 低（默认全关） | **本次不装**（用户 2026-10-01 决定） |
| NetorareValley | 覆盖式剧情改造 | 与现有山谷女孩重叠 38 个 Target | ❌ 新增全英文 | 🔴 **高** | **待定**（需覆盖 VG） |

### 4.2 已排除的疑虑

- **事件 ID 硬冲突：没有**。Affairs（61 个）、Amorous Valley（26 个）与整合包内**全部 9 个**含 `Data/Events` 补丁的包**零交集**；两个新包之间也零交集。
- **UniqueID 重复：没有**。新包 ID 与现有 169 个组件无一重复。
- **SMAPI/框架版本：全部满足**。新包最高要求 CP 2.0.0 / ML 2.0.0，现有 2.7.5；`MinimumApiVersion` 均 ≤ 4.5.2。
- **"假冲突"**：大量重叠是 `EditData` 改同一张表的不同条目（如 `Characters/Dialogue/*`），CP 按字段合并，属正常协作。

### 4.3 ⚠️ 尚未解决：加载顺序不可预测

- 已读上次启动日志（`%APPDATA%\StardewValley\ErrorLogs\SMAPI-latest.txt`，2026-09-27，确认是整合包环境）：**SMAPI 不排序，按文件系统枚举顺序加载**（日志里 `LetsMoveIt` 夹在中文目录中间，证明不是字母序）。
- 后果：HB 用 `Load` 换男性立绘，而【立绘】Veronnica / 去除弓形腿用 `EditImage`——**谁后加载谁生效**，而这一点无法靠文件夹命名保证。
- **应对**：装完第一次启动后，读日志的 "Loading mods..." 顺序确认新包的位置；若被美化包盖住，再调整文件夹名（改名即可，可逆）。

---

## 五、装新 MOD 的硬性纪律（整合包环境专用）

### 5.1 四条铁律

1. **绝不覆盖已有组件** —— 整合包 169 个组件（142 文件夹）**一个都别动**，只**新增**文件夹
   - 违反后果：如把 Steam 的 CP 2.9.1 复制过来，依赖旧版语法的包会全乱
   - **唯一例外**是 NetorareValley（它没有 manifest，只能覆盖山谷女孩）——必须单独授权 + 整目录备份

2. **装前必须查四项**

   ```
   □ 依赖是否满足（它的前置在整合包里吗？）
   □ UniqueID 是否与现有 169 个重复？
   □ 它需要的内容包框架（CP/FTM/CC/MEEP…）在吗？
   □ MinimumApiVersion ≤ 4.5.2 吗？
   ```

3. **装前备份存档** —— `%APPDATA%\StardewValley\Saves\整合_xxxxxxxx` 手动复制一份

4. **装后复扫结构** —— 重跑冲突检测（方法见 `技术笔记-汉化与DLL修改.md`）

### 5.2 检查脚本的现成方法

本次已写过扫描脚本（在 `D:\星露谷MOD\_暂存-整合包拓展\`，可重跑）：

| 脚本 | 作用 |
|---|---|
| `_scan_existing.py` | 扫描 `Mods\` 下全部 manifest → UniqueID / 版本 / 依赖 / 重名 / 缺依赖 |
| `_overlap.py` | 新包 × 现有包的**同名 Target** 重叠报告（含 Include 展开） |
| `_final_check.py` | Format 版本、Action 统计、事件键、`MinimumApiVersion` 检查 |
| `_content_overview.py` | 内容分布（改了哪些 NPC/节日/物品） |
| `_dossier.py` | ConfigSchema + 开关门控统计 |

**要点**：manifest 与 content.json 都必须用**宽松 JSON 解析器**（处理 BOM、`//` 与 `/* */` 注释、尾随逗号、**无引号键名**）。

### 5.3 命名与文件位置

- 新 MOD 统一用 `【成人】<中文名>` 前缀放进 `Mods\`，与整合包现有 `【功能】/【大型拓展】` 风格一致。
- 原压缩包保留在 `D:\星露谷MOD\整合包拓展\`（**注意：该目录当前不可写入**，解压/写入请改用 `D:\星露谷MOD\_暂存-整合包拓展\` 等工作区根目录下的路径）。

---

## 六、待用户确认的事项

- [x] ~~**Nude Girls 装不装？**~~ → **2026-10-01 决定：暂不装**
- [x] ~~其余 5 个 + NetorareValley + Event Repeater 是否安装？~~ → **2026-10-01 已全部安装**（8 个新组件 + 山谷女孩覆盖），见 [整合包环境-使用记录.md](整合包环境-使用记录.md) 第八节
- [x] ~~**启动验证**~~ → **2026-10-01 通过**：0 ERROR、71 mods + 106 content packs、新组件全部加载、Event Repeater 已接管 NTR 的 96 条重复事件（详见 [整合包环境-使用记录.md](整合包环境-使用记录.md) 第八节）
- [ ] **进游戏确认男性对话立绘**：HB 在加载顺序里排 134、【立绘】Veronnica 排 143（更晚）→ 可能被盖；跟 Alex/Sam 说句话即可判定，被盖就改 `【成人】单身汉` 的文件夹名后重启验证
- [ ] 试玩确认：三层场景（Horny Bachelors 默认开启的裸体演出、Make Love 需 ≥8 心且交往、Affairs 三条人妻线的触发）
- [ ] 扫一眼物品栏图标（HB 整表替换了 `Maps/springobjects`）
- [ ] **用在哪个存档？**（现有「整合」档，还是开新档）
- [ ] 能接受 Horny Bachelors 改现有男性 NPC 的日程与对话吗？（它会改 9 个 NPC 的日程、29 个 NPC 的对话）

---

## 七、接手后的标准流程

```
1. 拿到 MOD 名字/编号
2. 查它的依赖清单 + 面向的框架版本
3. 扫资源级冲突（不只是 UniqueID，要看是否抢同一批 Target 资源）
   —— 重点查：Characters/Dialogue/*、Data/events/*、Portraits/*、Maps/*
4. 确认它面向 hixega 还是 Pseudodiego 分支
5. 给出风险评级 + 是否建议安装
6. 用户确认后：
   a. 备份存档
   b. 只新增文件夹，不覆盖任何已有组件
   c. 装后复扫结构 + 启动验证（看 SMAPI 日志有无 ERROR）
   d. 读日志 "Loading mods..." 顺序，确认新包没有被美化包盖住
7. 把这次做了什么写进 整合包环境-使用记录.md（模板见 MD更新规则.md）
```

---

## 八、相关文档

| 文档 | 用途 |
|---|---|
| [整合包环境-使用记录.md](整合包环境-使用记录.md) | 整合包环境全景、已有 MOD 清单、已做改动 |
| [技术笔记-汉化与DLL修改.md](技术笔记-汉化与DLL修改.md) | 冲突检测方法、踩坑记录 |
| [Steam环境-MOD记录.md](Steam环境-MOD记录.md) | Steam 环境的成人 MOD 处理经验（VALLEY GIRLS 动画问题等） |
| [MD更新规则.md](MD更新规则.md) | 更新本文档时遵守的格式规范 |

---

## 九、本文档的维护

**状态变更时更新此处**：

| 日期 | 事件 |
|---|---|
| 2026-10-01 | 用户提出需求，完成风险分析，**未安装任何 MOD** |
| 2026-10-01 | 用户下载 11 个包到 `整合包拓展\`；完成全量分析（第三节逐包档案、第四节冲突评估），**仍未安装**；新增两处待确认（NetorareValley / Nude Girls） |
| 2026-10-01 | 用户给出 NTR 作者自述（"Valley Girls 的事件扩展"），与本文 3.2⑦ 的判定一致；补做**硬兼容性检查**（3.5）：贴图尺寸逐张核对、数据表键级比对、C# 目标框架、加载顺序实测 → 除 NTR 外全部通过 |
| 2026-10-01 | 用户下载 NTR 汉化包 `VALLEY GIRLS 53132 1.rar` 并核对（3.6：6715 键全中文 + 中文事件指南）；**决定 Nude Girls 暂不装**；其余 5 个包待用户确认后安装 |
| 2026-10-01 | 逐条依赖核对（带版本号）：manifest 必需依赖**全部满足**；发现可选依赖 **Event Repeater 未装**（NTR 的 `RepeatEvents` 列表空转，见 3.5）；据启动日志修正山谷女孩实际改动的资源数（67 个，含男性角色图） |
| 2026-10-01 | 用户提示"Steam 版应该有" → **核实：Steam 环境已装 Event Repeater v6.6**（.NET6 / MinApi 2.10.0 / 无依赖），仓库 `01-框架MOD` 亦有原包，DLL 同源；两套环境依赖对照完毕，**除它之外无缺口** |
| 2026-10-01 | 用户确认「方案 A + 方案 B + Event Repeater，开始干活」→ **安装完成**：8 个新组件（含从 Steam 复制的 Event Repeater）+ NetorareValley 覆盖山谷女孩 + 4 处汉化；装后静态校验全部通过。详见 [整合包环境-使用记录.md](整合包环境-使用记录.md) 第七节 |
| 2026-10-01 | **启动验证通过**：0 ERROR、71 mods + 106 content packs、新组件全部加载、Event Repeater 接管 NTR 的 96 条重复事件、男性裸体行走图确认生效；发现男性**对话立绘**可能被【立绘】Veronnica 盖住（加载顺序 134 vs 143），待游戏内确认 |
