# Steam 环境 MOD 记录

> **对象**：`D:\Apps\Steam\Steam\steamapps\common\Stardew Valley`（Steam 启动）
> **规模**：59 mods + 34 content packs，0 ERROR
> **方法论与踩坑**：见 [技术笔记-汉化与DLL修改.md](技术笔记-汉化与DLL修改.md)
> **整合包环境**：见 [整合包环境-使用记录.md](整合包环境-使用记录.md)
> 最后更新：2026-10-01

---

## 目录

- 早期工作（2026-09-05）：立绘修复、Happy Birthday、男性美化盘点
- [2026-09-25 上午：汉化修复](#2026-09-25-修复记录)
- [2026-09-25 下午：GMCM 英文清理](#2026-09-25-下半场gmcm-英文清理--整合包核对)
- [2026-09-25 第三场：PolyamorySweet 兰塔娜汉化](#2026-09-25-第三场polyamorysweet-兰塔娜lantana汉化补装)
- [2026-09-26：VALLEY GIRLS 事件对话汉化](#2026-09-26-valley-girls-事件对话汉化海滩酒馆婚后剧情)
- [2026-09-26 下半场：成人动画空白诊断](#2026-09-26-下半场成人动画空白诊断世界中-npc-站立不动)
- [汉化来源记录](#汉化来源记录2026-09-25-核实)
- [文件位置](#文件位置)

> ⚙️ 机制说明与方法论已移至 [技术笔记-汉化与DLL修改.md](技术笔记-汉化与DLL修改.md)，本文只留**实际做了什么**。

---

## 早期工作（2026-09-05）：本次对话完成内容

### 1. 修复角色立绘不显示问题

**问题原因**：`Seasonal Cute Characters` (SCC) 的 `SlightlyCuter*` 选项全部为 `true`，会在 `Mud Skimpy Portraits` 加载角色精灵图后再次编辑同一资源，把Mud的修改覆盖掉。

**修复方法**：将 `D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods\Seasonal Cute Characters\config.json` 中所有 `SlightlyCuter*` 设为 `"false"`。

**原理**：
- Mud Skimpy Portraits → 加载 `Characters/Abigail` ✓
- Seasonal Cute Characters → 编辑 `Characters/Abigail`（覆盖了Mud的修改）✗
- 关闭SlightlyCuter后，SCC不再修改基础角色精灵图

### 2. 修复Happy Birthday MOD错误

**问题1**：英文和中文Content Pack冲突，都以 `Exclusive` 优先级加载同一资源。

**修复**：删除英文Content Pack，只保留中文版：
- 删除：`D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods\HappyBirthdayContentPack en-US`
- 保留：`D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods\HappyBirthdayContentPack zh-CN`

**问题2**：`TimeOfDay` token错误 — `Content\Mods\Omegasis.HappyBirthday\Strings\Misc.xnb` 文件不存在。

**修复**：创建 `D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods\HappyBirthday\i18n\Misc.json`，包含英文字符串。

**注意**：此警告是Happy Birthday 3.21.4的已知兼容性问题，mod代码使用旧的xnb加载API，SDV 1.6+已改用i18n/JSON格式。不影响核心功能。

### 3. 安装Happy Birthday Content Pack

- 安装中文Content Pack：`HappyBirthdayContentPack zh-CN`

### 4. 检查男性角色美化MOD

**当前已安装MOD中的男性角色情况**：
| MOD | 男性角色 | 包含单身男性？ |
|-----|----------|----------------|
| Mud Skimpy Portraits | 无 | ✗ |
| OO's Anime Style Skimpy Portraits | Clint, George, Gunther, Kent, Lewis, Linus, Marlon, Pierre, Willy, Wizard | ✗（全部是非单身NPC） |

**结论**：已安装的MOD中没有单身男性（Alex, Sam, Sebastian, Shane, Elliott, Harvey）的美化。

**可用的男性美化MOD**：`CP Portrait Anime Mods OhoDavi` 包含所有6个单身男性动漫立绘（Alex, Elliott, Harvey, Sam, Sebastian, Shane），同时包含海滩和冬季变体。

## 已知问题

### Happy Birthday TimeOfDay错误
- 警告内容：`Custom token 'Omegasis.HappyBirthday/TimeOfDay' failed`
- 原因：mod使用旧的 `LocalizedContentManager.LoadString()` API加载xnb文件
- 影响：不影响核心功能，只是警告
- 解决方案：等待mod作者更新到SDV 1.6+兼容版本

### 角立绘验证
- 修改SCC config后需要重启游戏才能生效
- Mud Skimpy Portraits的Load操作已确认在SMAPI日志中成功加载
- 需要与NPC对话验证头像变化，观察地图行走模型

## MOD安装状态总览

### 已安装的主要MOD
- **框架MOD**：Content Patcher, SpaceCore, SMAPI 4.5.2
- **大型扩展**：Stardew Valley Expanded, Ridgeside Village, East Scarp REMASTERED
- **功能性MOD**：Happy Birthday, PolyamorySweet, SkipFishingMinigame, Visible Fish
- **角色美化**：Mud Skimpy Portraits（女性）, OO's Anime Style Skimpy Portraits（非单身NPC）
- **季节美化**：Seasonal Cute Characters（SlightlyCuter已关闭）
- **恋爱MOD**：Romanceable Rasmodia（女巫）

### 待安装
- `CP Portrait Anime Mods OhoDavi`（单身男性动漫立绘）— 用户确认后安装

## 文件位置

- 游戏目录：`D:\Apps\Steam\Steam\steamapps\common\Stardew Valley`
- MOD目录：`D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods`
- MOD下载源：`D:\星露谷MOD`
- 解压MOD：`D:\星露谷MOD\解压`
- SMAPI日志：`%APPDATA%\StardewValley\ErrorLogs\SMAPI-latest.txt`
- **存档备份**：`D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\save-backups\`（SMAPI 每日一份 zip，不是 %APPDATA% 下）

---

## 2026-09-25 修复记录

### 1. 打上 Xtardew Valley 汉化

**问题**：`[CP]Xtardew Valley`、`[CP]Xtardew Portraits&Sprites`、`[CP]Xtardew Valley Poly Leah&Abigail` 三个 MOD 的 `content.json` 与英文原版包**逐字节一致**，目录里连 `i18n` 都没有 → 全程英文。

**处理**：从 `D:\星露谷MOD\03-成人MOD\X.V.3.20 translation.zip-12954-3-2-0-1736208189.zip` 解出 21 个文件，按目录结构覆盖到游戏三个 MOD 目录。

**为什么安全**：覆盖前核实过汉化包是**等量文本替换**——三个 `content.json` 的 Changes 条数完全相等（59/119/41），汉化独有条目 0、游戏独有条目 0；Dialogue 文件游戏内 14 个全覆盖。覆盖后复核 Changes 条数仍为 59/119/41，21 个文件哈希与包内一致。

**注意**：Xtardew 的汉化是**直接替换 content.json**（不走 i18n 机制），所以 **MOD 本体更新会覆盖掉汉化，需要重打**。

### 2. 合并 CJB 作弊菜单汉化

**问题**：CJB 有两个汉化包，都写同一个文件 `CJBCheatsMenu\i18n\zh.json`：

| 汉化包 | 键数 | 独有内容 |
|---|---|---|
| CJBCheatMenu Chinese 1.42.0（原先生效） | 153 | CJB 1.42 新增功能：作物自动灌溉、工具附魔、天气等 16 个键 |
| CJB Cheats Menu Warps for RSV-CHS | 207 | 70 个 RSV 传送点地名：安仙儿的家、山脊崖边、皮卡餐厅…… |

两者**互不包含**，先前只生效一个 → 缺 RSV 地点名汉化。

**处理**：文本级合并成 223 键（= 153 + 70），写入 `Mods\CJBCheatsMenu\i18n\zh.json`（8834 → 12826 字节）。

**为什么安全**：重叠 137 键中有 9 个值不同，**Warps 版那 9 个是英文**（`Default tab`、`The keybind held to grow crops...`），故以游戏内中文为准。合并用文本插入（非 JSON 重写），**保留了原文件的 BOM 和注释**。合并后复核：原 153 键值全部未变、Warps 版 207 键全在。

### 3. 备份位置

改动前的原文件已备份到 `D:\星露谷MOD\汉化备份\2026-09-25-修复前\`（22 项，含 Xtardew 三个 MOD 的 content.json + Dialogue 文件夹、CJBCheatsMenu 的 zh.json），全部哈希校验通过。

### 4. 修复 OO 动漫立绘被「季节可爱角色SVE」遮挡

**问题**：`Seasonal Cute Characters SVE` 子包的 21 个 `SlightlyCuter*` 开关**全是 `true`**（2026-09-05 那次只修了主包 SCC 的 47 个，漏了 SVE 和 ES 两个子包）。SCC-SVE 会给 SVE 角色提供季节立绘（`Portraits/GuntherSilvian_Spring` 等），而 OO 的规则只覆盖基础名（`Portraits/GuntherSilvian`）→ **游戏春季请求季节变体，OO 的规则永不触发**。表现为刚瑟等 NPC 显示原版风格的季节立绘。

**处理**：关闭 `Mods\Seasonal Cute Characters SVE\[CP] Seasonal Cute Characters SVE\config.json` 里这 9 项，交给 OO：

`SlightlyCuterGunther`（→`GuntherSilvian.json`）、`SlightlyCuterClaire`、`SlightlyCuterLance`、`SlightlyCuterOlivia`、`SlightlyCuterSophia`、`SlightlyCuterVictor`、`SlightlyCuterMarlon`（→`MarlonFay.json`）、`SlightlyCuterMorris`（→`MorrisTod.json`）、`SlightlyCuterSandy`

**保留 12 项**，其中 **`SlightlyCuterMagnus` 必须保留**——巫师走「可恋爱的女巫」，而女法师是 **Edit 模式**，需要 SCC-SVE 先提供底图（`Portraits/Magnus_Spring`），关掉反而会让女性化立绘失效。其余 11 项是 SCC-SVE 独有、OO 不覆盖的 NPC。

**日志实证**：修改前 OO 处理 18 个角色 → 修改后 **26 个**，新增的正是刚瑟、克莱尔、奥利维亚、索菲亚、维克托、马龙、莫里斯、桑迪。巫师序列保持 `季节可爱角色SVE(load) → 可恋爱的女巫(edit)`。

**⚠️ 写入时注意**：这个 config 里所有值都是**字符串**（`"true"`/`"false"`），不是 JSON 布尔值。写成布尔会导致 Content Patcher 条件判断异常。

**取舍**：这 9 个 NPC 交给 OO 后**不再有季节/节日立绘**（OO 只提供基础图 + 夏/冬/海滩装）。

### 5. 安装 Mail Framework Mod（框架）

v1.20.0，Nexus 1536，装到 `Mods\MailFrameworkMod\`。压缩包归入 `01-框架MOD\`。

它是**纯框架**（"Utility classes and content packs to add mail into the game"），自身不提供任何寄件功能——装了但没有 MOD 使用它时不会有可见效果。

### 6. 安装 Mail Services Mod + 汉化（实现「铁匠工具快递」）

**来源**：Nexus 7842（v1.6.2）本体 + Nexus 32320（v1.0.1）汉化，装到 `Mods\MailServicesMod\`。压缩包分别归入 `03-功能性MOD\` 和 `08-中文翻译\`。

**依赖**：`DIGUS.MailFrameworkMod` ≥ 1.16.0（已装 1.20.0 ✓）、`spacechase0.GenericModConfigMenu` ≥ 1.12.0（可选，已装 1.16.0 ✓）

**汉化选择**：本体自带 `i18n/zh.json`（30 键），汉化包是 33 键的**超集**且译文更自然，故用汉化包覆盖（3739 字节）。

**提供的服务**：
- **克林特工具快递**——工具升级完成后寄到你的邮箱（`Delivery.Clint.UpgradeLetter`）
- 克林特工具升级寄送——把工具+锭+钱寄给铁匠
- 任务物品寄送
- 马龙物品找回服务（邮件找回遗失物品）
- 礼物寄送

---


## 汉化来源记录（2026-09-25 核实）

以下 5 处汉化的**实际生效版本与仓库压缩包内容不一致**。它们现在是正常的，但**更新 MOD 或重装时不要用仓库旧包覆盖**：

| MOD | 游戏内生效 | 仓库包 | 判断 |
|---|---|---|---|
| Romanceable Rasmodia | 355050 字节 | 355065 字节 | 键数相同，同源微调，无需处理 |
| Alternative Textures | 3126 字节 | 3330 字节（`I18n 49149`） | 同源不同版 |
| Lookup Anything | 37121 字节 | 33817 字节 | **游戏内更全**（多 44 键），仓库那个只是「钓鱼点补充」 |
| East Scarp NPCs config / 理发店 | 2400 / 340 字节 | 1983 / 193 字节 | 不同版本 |
| Elle's Seasonal Buildings | 94 键 | 186 键 | **游戏内才对**——仓库那个是旧格式（`values` 而非 `description`），**千万别覆盖** |

### 已核实、无需处理的「假问题」

- SMAPI 日志里 10 条「Nexus mod ID 无效」：SVE / East Scarp / RSV / Frontier Farm 的子组件，作者**故意**填 `Nexus:???` 关闭更新检查，文件完好。副作用是这些子组件收不到更新提醒。
- 日志里 SpaceCore 的「changed save serializer」警告：正常提示，但**不可卸载 SpaceCore**（卸了存档打不开）。
- 派大星马的内容补丁语法过时警告：CP 已自动迁移，功能正常。

---

# 2026-09-25 下半场：GMCM 英文清理 + 整合包核对

## 一、问题定位（方法论已移至技术笔记）

玩家可见的「界面英文」分三层，**修法互不相同**：

| 层 | 位置 | 文本来源 | 能不能改 |
|---|---|---|---|
| **A** | GMCM 的 MOD 列表页 | `manifest.json` 的 `Name` 字段 | ✅ 改 Name |
| **B** | 配置页的选项名/说明 | DLL 硬编码 **或** CP 框架渲染 | ✅ 分情况 |
| **C** | 配置页里的人名 | `ConfigSchema` 的 `AllowValues`（NPC 内部 ID） | ❌ **不能改** |

**B 层两种类型**：
- **DLL 型**（MailServicesMod 等）→ 选项名硬编码 → **DLL 等长替换**
- **CP 内容包**（Frontier Farm 等）→ CP 自带 i18n → **加 `config.*` 键**

> **完整机制、CP 的 i18n 键名约定、三个已生效实例** → 见 [技术笔记-汉化与DLL修改.md](技术笔记-汉化与DLL修改.md) 第一~三节。

---

## 二、本次实际修改

### 1. A 层：三个 manifest 的 Name 改中文

| MOD | 改前 | 改后 | UniqueID（未变） |
|---|---|---|---|
| Frontier Farm | `Frontier Farm` | **边境农场** | `flashshifter.FrontierFarm` |
| MailServicesMod | `Mail Services Mod` | **邮件服务** | `Digus.MailServicesMod` |
| Valley Girls | `Valley Girls` | **山谷女孩** | `Trashracc.VG` |

验证：独立比对改前备份，**仅 Name 变化，其余字段完全一致**；SMAPI 日志确认三者列表页已是中文。

### 2. B 层①：MailServicesMod 的 DLL（52 个串）

反编译 `ConfigMenuController.cs` 确认 **0 处 `Translation.Get()`**，选项名全是硬编码字面量。

处理：**等长字节替换**，67072 字节不变。分组标题 8 个 + 选项名 20 个 + 说明 24 个。

关键功能项：
```
Tool Delivery Service  →  工具快递服务
说明: You will receive upgraded tools in the mailbox.
   →  升级完成的工具将寄到你的邮箱。
```

### 3. B 层②：Frontier Farm 加 22 个 i18n 键

`[CP] Frontier Farm/i18n/zh.json`：69 → 91 键（新增 11 个字段的 `.name` + `.description`）。
原 69 键值 **0 改动**。**未改 content.json、未改 DLL。**

### 4. Valley Girls：我误加了 6 个重复键，已回滚

**原因**：它的 zh.json 原本用**大写** `Config.` 前缀（`Config.ManualRecolourSelection.name`），我按**小写** `config.` 过滤检测时没看见它，于是加了小写的同名键。
**SMAPI i18n 键大小写不敏感** → 报 `Found duplicate translation keys`。
→ 已删除我加的 6 键，**252 键与备份完全一致**，重复消失。

---

## 三、踩的坑

> **已移至 [技术笔记-汉化与DLL修改.md](技术笔记-汉化与DLL修改.md)**（含 6 条完整踩坑记录 + 原因分析）。
>
> 本次涉及的坑简述：
> 1. SMAPI 的 i18n 键**大小写不敏感** → 改 zh.json 前必须做大小写归一化检查
> 2. "只有 zh.json 没有 default.json" **不是缺汉化**
> 3. 不要用弱检测器扫全量（先拿已知文件自检）
> 4. DLL 等长替换必须**长串优先**
> 5. 改动前先备份 + 改后**独立**比对

---

## 四、备份位置（本次）

**保留的备份**：`D:\星露谷MOD\汉化备份\2026-09-25-修复前\`
- `DLL-改动前\`：MailServicesMod.dll、Unlockable Bundles.dll、SkipFishingMinigame.dll、GameSpeedToggle.dll、WearMoreRings.dll
- `Frontier Farm\[CP] Frontier Farm\`：manifest.json、i18n/zh.json
- `[CP] VALLEY GIRLS\`：manifest.json、i18n/zh.json
- `MailServicesMod\`、`Seasonal Cute Characters SVE\` 等：manifest.json、config.json
- Xtardew 三个 MOD 的 content.json + Dialogue 文件夹、CJBCheatsMenu 的 zh.json
（全部改动前版本，哈希校验过，可用于回滚）

**已删除的中间文件**（本次分析脚本与反编译产物，位于 `%TEMP%`，可随时重新生成）。

---

# 2026-09-25 第三场：PolyamorySweet 兰塔娜（Lantana）汉化补装

## 一、问题

游戏内 NPC **兰塔娜**（英文名 **Lantana**，PolyamorySweet 新增 NPC）的名称与全部对话显示英文。

## 二、根因：CP 内容包硬编码，且汉化包漏装了文件

Lantana 的名称与对话**硬编码在 `[CP] Polyamory Sweet` 内容包里，不走 i18n**：

| 内容 | 位置 |
|---|---|
| NPC 显示名 | `content.json:1348` `"DisplayName": "Lantana"` |
| 地点名 | `content.json:458` `"Lantana Lagoon"` |
| 日常对话 | `Assets\Lantana\Dialogue.json`（周一~周日） |
| 分级对话 | `Assets\Lantana\DialoguePG.json` |

→ 所以只有 `i18n/zh.json`（仅 5 个键：兰塔娜礁、config 项）**翻不了对话和名称**。

汉化包 **PolyamorySweet-Chinese**（Nexus 29247，v1.6.1，2026-08-06）里**有**这 3 个文件的中文版，但游戏内**只装进了 `i18n/zh.json`**，另 3 个漏装：

| 文件 | 游戏内（改前） | 汉化包 |
|---|---|---|
| `[CP] Polyamory Sweet\content.json` | 英文（2026-07-03 原版） | 中文，132 处翻译 |
| `Assets\Lantana\Dialogue.json` | 英文 5826 B | 中文 6087 B |
| `Assets\Lantana\DialoguePG.json` | 英文 5594 B | 中文 5824 B |

## 三、处理与验证

从汉化包覆盖上述 3 个文件。覆盖前验证：

- content.json 两边**均为 1713 行**，132 处差异**全部是英文→中文**（DisplayName / Description / 对话 / 事件脚本），**无任何条目增删**（132 对 132 完全对称），同版本 1.6.1 → 安全。
- 覆盖后 md5 与汉化包逐一一致；改前文件已备份。

**顺带修复**：content.json 里 **Abigail / Leah / Haley** 的多角恋对话（`Target` 见 `content.json:1495/1535/1576`）也是英文，一并变中文。

## 四、未改动

- **5 个 DLL**（Bed/Kiss/Love/Rooms/Wedding）：汉化包版本**比游戏内更小**（如 Love 226816 B vs 228864 B），疑似不同构建，覆盖有降级风险 → **不动**。本问题也与 DLL 无关。
- `config.json`、`i18n/zh.json`（后者本就与汉化包相同）。

## 五、备份

`D:\星露谷MOD\汉化备份\2026-09-25-PolyamorySweet修复前\[CP] Polyamory Sweet\`
- `content.json`（改前英文原版）
- `Assets\Lantana\Dialogue.json`、`DialoguePG.json`

（哈希校验通过，可回滚）

## 六、⚠️ 注意

PolyamorySweet 本体更新会覆盖 `content.json`，**汉化需重打**——重打时覆盖以上 3 个文件即可。


---

## 2026-09-26 VALLEY GIRLS 事件对话汉化（海滩/酒馆/婚后剧情）

**问题**：玩 Xtardew 时在海滩触发海莉+亚历克斯剧情，发现英文对话。排查后确认：**英文不在 Xtardew（三个包已 100% 汉化、零英文残留），而在 VALLEY GIRLS（山谷女孩）**。

**根因**：VALLEY GIRLS 的成人剧情对话**硬编码在事件脚本**（Events.json / MarriageEvents.json），不走 i18n 机制（事件脚本内 i18n 引用为 0 处）。之前装的汉化（i18n/zh.json，252 键，已完整覆盖 default.json 192 键）**只能覆盖非事件对话**（偷窥/自慰等），覆盖不到事件剧情。

**涉及剧情**（Nexus 15838 v3.6.0）：
- 海滩裸体剧情：事件 10536/10538（男）/ 10540/10542（女），data/events/Beach，主角 Alex+Haley
- 酒馆剧情：10535/10537（男）/ 10539/10541（女），data/events/Saloon，主角 Sam+Abigail+Sebastian
- 婚后剧情：10550-10561，data/events/FarmHouse，6 个可结婚女性（Abigail/Emily/Haley/Leah/Maru/Penny）× 男/女玩家

**处理**：直接汉化游戏内 ssets\Jsons\Events\Events.json（93 条唯一文本 → 海滩+酒馆+2 封邮件）和 MarriageEvents.json（148 条唯一文本），共翻译约 240 条，替换 750+ 处。保留全部表情代码（\/\ 等）、换行符、@ 玩家名占位符；JSON 结构完整（Events 18 个、MarriageEvents 90 个，事件键未变）。

**验证**：两文件转义引号内英文对话残留 = 0；JSON 解析正常；mail 信件（山姆 SaloonSession、海莉 BeachNaked）已汉化。

**备份**：`D:\星露谷MOD\汉化备份\2026-09-26-VALLEYGIRLS修复前\[CP] VALLEY GIRLS\`（Events.json、MarriageEvents.json 原版）

**⚠️ 注意**：VALLEY GIRLS 本体更新会覆盖这两个文件，**汉化需重打**。

---

# 2026-09-26 下半场：成人动画空白诊断（世界中 NPC 站立不动）

## 一、问题现象（用户多轮澄清后的最终定义）

| 现象 | 详情 |
|---|---|
| 世界中 NPC 站立不动 | 女性按日程到特定地点（女厕所/浴室/海滩/自家卧室），但自慰动作不播放，原地站着 |
| 剧情对话框有文字但无动画 | 亚历克斯等男性在性爱场景站着；海莉等临时角色能动 |
| 对话界面正常 | 文字 + Mud 立绘（静态头像），界面本就不播动画，非故障 |

## 二、根因（已核实，非冲突/非配置/非汉化问题）

**VALLEY GIRLS 的动画帧号按"大贴图"设计，1.6 原版 NPC 贴图只有 64×672（84 帧），帧号全部越界。**

1. `config.json` Pleasure 列表 = 10 女性，`When: {"Pleasure": "Haley"}` 条件满足 → **日程生效**（SMAPI 日志确认 patch 应用，小写 `entries` 也被 CP 接受）
2. 女性被安排去 `Custom_FemaleToilet`（女厕所）/ `Custom_BathroomVG`（浴室）/ `Custom_MaleToilet`（男厕所）/ 海滩 / 各家卧室
3. `{{haley_r}}` → `haley_pleasure{{Random:1-8}}` → `Data/animationDescriptions` 帧 **196-269**
4. **断点**：1.6 原版 `Characters/Haley` = 64×672 = **84 帧**（Haley.xnb 文件头 LZ4 usize≈106KB 证实；文件 5KB 左右，符合 64×672 像素艺术贴图量级），帧 196-269 全部越界

   > ⚠️ **2026-10-01 更正**：这个尺寸数字算错了。用 xnb 未压缩长度反推（`(usize-177)/4 = 像素数`，常数 177 已用 4 个文件交叉验证），`Characters/Haley.xnb` 的 usize 是 106673 → **实际 64×416（52 帧）**，不是 64×672。
   > 原版实测尺寸：Haley 角色 64×416 / 立绘 128×448、Abigail 64×448 / 128×320、Alex 64×416 / 128×384、Sam 64×448 / 128×384。
   > **结论不变**（VG 的帧 196-269 照样越界，而且越得更远），只是基准数字要改。反推方法见 [技术笔记-汉化与DLL修改.md](技术笔记-汉化与DLL修改.md) 第九节。
5. VG 用 EditImage 把动画帧贴图（`Haley_Sprites.png` 64×896）贴到 `ToArea Y:1600` → 超出 672px 贴图边界，**CP 静默忽略该 patch**（日志无 ERROR）
6. 动画播放时指向贴图外空白区域 → NPC 站着不动

**剧情同病根**：`animate Alex` 帧 247-250 越界（亚历克斯不动）；`HaleyNude`/`HaleyExtra` 用 VG 独立 Load 的小贴图（20/12 帧），帧号匹配 → **海莉能动**（这就是"有时候有动画"的原因）。

**结论**：VALLEY GIRLS 与星露谷 1.6 原版贴图尺寸不兼容。立绘（Mud）、文字、日程全部正常，缺的只是场景里的动作动画。

## 三、本次实际改动（仅 1 项，已恢复原样）

**Mud Skimpy Portraits：删除 6 个 Breath Disable → 已恢复**

- 曾误判用户要"呼吸动画"，删除了 Penny/Haley/Emily/Maru/Abigail/Leah 的 `Breather: false` 条目（Changes 46→40）
- 用户澄清要的是"成人动作"后，从备份恢复：`D:\星露谷MOD\汉化备份\2026-09-26-美化冲突修复前\Mud-SkimpyPortraits-content.json`
- 恢复后已验证 Changes = 46，与装前一致

**结论：当前 MOD 环境 = 原装 + 一份 VG 汉化，无任何未验收修改。**

## 四、未改动（待用户决定后再动）

- **VG 自慰/性爱动画修复**：需为 10 位女性（+Alex 等男性）制作"原版 + VG 动画帧"合成大贴图（64×2560，动画帧放 y=1600 区域），用 Load 补丁替换 → 用户说先不修，**未做**
- **DDF 字典问题**（OO/OO-SVE 引用 Mud 不存在 8 角色）：用户确认对话有文字后已排除，**未改**

## 五、本次新确认的事实（供后续参考）

- **VG 的阿比盖尔/莉亚日程**含 `HasMod |contains=Pseudodiego.LAtardewValley: false` → 装了 Poly（Xtardew Poly Leah&Abigail）时 VG **自动关闭这两位女性的自慰日程**，其余 8 位不受影响
- **人物美化 MOD 盘点**：SCC（季节服装，日常行走图）、Mud（泳装/性感立绘 + 夏天外观）、OO 系列（商店 NPC 肖像）、Xtardew P&S（仅剧情事件裸体角色）——互不打架，SMAPI 无 CP 报错
- **Xtardew 只存在于剧情**（36 个事件 + 事件专用角色贴图），日常世界无 Xtardew 内容；VG 负责日常演出（日程驱动）
- VG 自慰/性爱演出全清单（人物 × 地点 × 时间）已整理，见对话记录
