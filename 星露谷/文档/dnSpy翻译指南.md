# 使用dnSpy翻译MOD配置菜单指南

> ## ⚠️ 阅读前必看（2026-10-01 校准）
>
> **本文写于早期，部分做法已被更好的方案取代，也有已核实为错误的地方。** 对照现状：
>
> | 本文说法 | 实际情况 |
> |---|---|
> | Unlockable Bundles「用 dnSpy 改硬编码字符串」 | ❌ **它走 i18n**。代码里有 `ub_overview_button`、`ub_parrot_ask` 等键 → 建 `i18n/zh.json` 即可（已建，11 键）；另有 4 处真硬编码已用等长替换处理 |
> | SkipFishingMinigame「没有 i18n 文件夹，需先创建」 | ⚠️ 它的 **i18n 目录是空的**，选项名硬编码在 DLL 里 → 只能改 DLL（已做 1 处等长替换） |
> | 各 MOD「改 N 处硬编码 + 建 zh.json」 | ✅ 方向对，但**本文列出的具体串需重新核对**（版本可能已变） |
>
> **改 DLL 前必读** → [技术笔记-汉化与DLL修改.md](技术笔记-汉化与DLL修改.md)
> （含等长替换原理、**长串优先**的陷阱、三项必做校验、6 条踩坑记录）
>
> **本文仍有效的部分**：dnSpy 的**操作步骤**（第 1-6 步、常见问题、验证方法）——那是工具用法，不受版本影响。

---

## 概述

这7个MOD不支持i18n翻译，需要使用dnSpy修改DLL中的硬编码英文字符串。

## 准备工作

1. 确保dnSpy已安装：`D:\Tools\dnSpy\dnSpy.exe`
2. 确保已安装.NET Desktop Runtime（dnSpy需要）

## 操作步骤

### 步骤1：备份原始DLL

在修改前，先备份原始DLL到 `D:\星露谷MOD\DLL备份\`

### 步骤2：使用dnSpy打开DLL

1. 双击运行 `D:\Tools\dnSpy\dnSpy.exe`
2. 点击菜单 File → Open → 选择MOD的DLL文件
3. 在左侧面板展开程序集，找到ModEntry类

### 步骤3：找到GMCM注册方法

在ModEntry类中找到 `OnGameLaunched` 或类似的方法，搜索 `GenericModConfigMenu` 或 `AddBoolOption`

### 步骤4：修改代码

将硬编码的英文字符串改为使用 `base.Helper.Translation.Get()` 调用

**原始代码示例：**
```csharp
api.AddBoolOption(base.ModManifest, () => this.config.EnableMod, delegate(bool val)
{
    this.config.EnableMod = val;
}, () => "Mod Enabled", null, null);
```

**修改后代码：**
```csharp
api.AddBoolOption(base.ModManifest, () => this.config.EnableMod, delegate(bool val)
{
    this.config.EnableMod = val;
}, () => base.Helper.Translation.Get("EnableMod"), null, null);
```

### 步骤5：编译并保存

1. 点击菜单 File → Save Module → 选择保存位置（覆盖原DLL）
2. 关闭dnSpy

### 步骤6：创建i18n翻译文件

在MOD的i18n文件夹中创建或编辑zh.json文件

---

## 各MOD详细修改指南

### 1. VisibleFish (showFishInWater.dll)

**文件位置：** `D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods\VisibleFish\showFishInWater.dll`

**需要修改的代码（在OnGameLaunched方法中）：**

找到以下代码并修改：

| 原始字符串 | 修改为 | 翻译键 |
|-----------|--------|--------|
| `() => "Maximum fish"` | `() => base.Helper.Translation.Get("MaximumFish")` | MaximumFish |
| `() => "Maximum number of fish..."` | `() => base.Helper.Translation.Get("MaximumFish.description")` | MaximumFish.description |
| `() => "Fish Density"` | `() => base.Helper.Translation.Get("FishDensity")` | FishDensity |
| `() => "0.1 (i.e. 10%)..."` | `() => base.Helper.Translation.Get("FishDensity.description")` | FishDensity.description |
| `() => "Show Treasure in the water"` | `() => base.Helper.Translation.Get("ShowTreasure")` | ShowTreasure |
| `() => "Enable trash outside Farm"` | `() => base.Helper.Translation.Get("TrashOutside")` | TrashOutside |
| `() => "Enable trash on Farm"` | `() => base.Helper.Translation.Get("TrashFarm")` | TrashFarm |
| `() => "Disable trash on Fishing 10"` | `() => base.Helper.Translation.Get("DisableTrashLvl10")` | DisableTrashLvl10 |
| `() => "Draw shadows under trash."` | `() => base.Helper.Translation.Get("DrawItemShadows")` | DrawItemShadows |
| `() => "Draw shadows under fish."` | `() => base.Helper.Translation.Get("DrawFishShadows")` | DrawFishShadows |
| `() => "Rotate algae/seaweed"` | `() => base.Helper.Translation.Get("RotateAlgae")` | RotateAlgae |
| `() => "Hide eel-like fish"` | `() => base.Helper.Translation.Get("FilterEels")` | FilterEels |

**zh.json内容：**
```json
{
    "MaximumFish": "最大鱼数",
    "MaximumFish.description": "最大鱼数。如果卡顿请降低。默认：500",
    "FishDensity": "鱼密度",
    "FishDensity.description": "0.1（即10%）-> 每10个格子有一条鱼。遵循最大鱼数选项。默认：0.2",
    "ShowTreasure": "在水中显示宝箱",
    "TrashOutside": "启用农场外垃圾",
    "TrashFarm": "启用农场垃圾",
    "DisableTrashLvl10": "钓鱼10级时禁用垃圾",
    "DrawItemShadows": "在垃圾下绘制阴影",
    "DrawFishShadows": "在鱼下绘制阴影",
    "RotateAlgae": "旋转藻类/海带",
    "FilterEels": "隐藏鳗鱼类鱼"
}
```

---

### 2. DialogueDisplayFramework (DialogueDisplayFramework.dll)

**文件位置：** `D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods\DialogueDisplayFramework\DialogueDisplayFramework.dll`

**需要修改的代码：**

| 原始字符串 | 修改为 | 翻译键 |
|-----------|--------|--------|
| `() => "Mod Enabled"` | `() => base.Helper.Translation.Get("EnableMod")` | EnableMod |
| `() => "Dialogue Width Offset"` | `() => base.Helper.Translation.Get("DialogueWidthOffset")` | DialogueWidthOffset |
| `() => "Size offset to the dialogue box's width..."` | `() => base.Helper.Translation.Get("DialogueWidthOffset.description")` | DialogueWidthOffset.description |
| `() => "Dialogue Height Offset"` | `() => base.Helper.Translation.Get("DialogueHeightOffset")` | DialogueHeightOffset |
| `() => "Size offset to the dialogue box's height..."` | `() => base.Helper.Translation.Get("DialogueHeightOffset.description")` | DialogueHeightOffset.description |
| `() => "Dialogue X Offset"` | `() => base.Helper.Translation.Get("DialogueXOffset")` | DialogueXOffset |
| `() => "Position offset to the dialogue box's x position..."` | `() => base.Helper.Translation.Get("DialogueXOffset.description")` | DialogueXOffset.description |
| `() => "Dialogue Y Offset"` | `() => base.Helper.Translation.Get("DialogueYOffset")` | DialogueYOffset |
| `() => "Position offset to the dialogue box's y position..."` | `() => base.Helper.Translation.Get("DialogueYOffset.description")` | DialogueYOffset.description |

**zh.json内容：**
```json
{
    "EnableMod": "启用模组",
    "DialogueWidthOffset": "对话框宽度偏移",
    "DialogueWidthOffset.description": "对话框宽度的大小偏移。负数会缩小。\n别忘了调整x偏移。",
    "DialogueHeightOffset": "对话框高度偏移",
    "DialogueHeightOffset.description": "对话框高度的大小偏移。负数会缩小。\n别忘了调整y偏移。",
    "DialogueXOffset": "对话框X偏移",
    "DialogueXOffset.description": "对话框x位置的位置偏移。负数会向左移动。",
    "DialogueYOffset": "对话框Y偏移",
    "DialogueYOffset.description": "对话框y位置的位置偏移。负数会向上移动。"
}
```

---

### 3. GameSpeedToggle (GameSpeedToggle.dll)

**文件位置：** `D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods\GameSpeedToggle-v1.0.0-42406-1-0-0-1771194418\GameSpeedToggle.dll`

**需要修改的代码：**

| 原始字符串 | 修改为 | 翻译键 |
|-----------|--------|--------|
| `() => "Toggle Key"` | `() => base.Helper.Translation.Get("ToggleKey")` | ToggleKey |
| `() => "Press to toggle custom game speed."` | `() => base.Helper.Translation.Get("ToggleKey.description")` | ToggleKey.description |
| `() => "Speed Multiplier"` | `() => base.Helper.Translation.Get("SpeedMultiplier")` | SpeedMultiplier |
| `() => "Multiplier by which to multiply default game speed"` | `() => base.Helper.Translation.Get("SpeedMultiplier.description")` | SpeedMultiplier.description |
| `() => "Enable On Load"` | `() => base.Helper.Translation.Get("EnableByDefault")` | EnableByDefault |
| `() => "If enabled, custom game speed turns on automatically whenever a save is loaded."` | `() => base.Helper.Translation.Get("EnableByDefault.description")` | EnableByDefault.description |
| `() => "Enable On Sleep"` | `() => base.Helper.Translation.Get("EnableOnSleep")` | EnableOnSleep |
| `() => "If enabled, custom game speed turns on automatically each morning..."` | `() => base.Helper.Translation.Get("EnableOnSleep.description")` | EnableOnSleep.description |
| `() => "Affect Fishing Minigame"` | `() => base.Helper.Translation.Get("AffectFishingMinigame")` | AffectFishingMinigame |
| `() => "If enabled, the fishing minigame follows the configured speed multiplier."` | `() => base.Helper.Translation.Get("AffectFishingMinigame.description")` | AffectFishingMinigame.description |

**zh.json内容：**
```json
{
    "ToggleKey": "切换按键",
    "ToggleKey.description": "按下切换自定义游戏速度。",
    "SpeedMultiplier": "速度倍数",
    "SpeedMultiplier.description": "默认游戏速度的乘数倍数",
    "EnableByDefault": "加载时启用",
    "EnableByDefault.description": "启用后，加载存档时自定义游戏速度会自动开启。",
    "EnableOnSleep": "睡觉时启用",
    "EnableOnSleep.description": "启用后，每天早上自定义游戏速度会自动开启。仅在启用"加载时启用"时有效。",
    "AffectFishingMinigame": "影响钓鱼小游戏",
    "AffectFishingMinigame.description": "启用后，钓鱼小游戏将遵循配置的速度倍数。"
}
```

---

### 4. SkullCavernElevator (SkullCavernElevator.dll)

**文件位置：** `D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods\SkullCavernElevator\SkullCavernElevator.dll`

**需要修改的代码：**

| 原始字符串 | 修改为 | 翻译键 |
|-----------|--------|--------|
| `() => "Elevator Step"` | `() => base.Helper.Translation.Get("ElevatorStep")` | ElevatorStep |
| `() => "This value determines how often elevators appear"` | `() => base.Helper.Translation.Get("ElevatorStep.description")` | ElevatorStep.description |
| `() => "Difficulty"` | `() => base.Helper.Translation.Get("Difficulty")` | Difficulty |
| `() => "This value also effects how often elevators appear..."` | `() => base.Helper.Translation.Get("Difficulty.description")` | Difficulty.description |
| `() => "FirstLevelElevatorActive"` | `() => base.Helper.Translation.Get("FirstLevelElevatorActive")` | FirstLevelElevatorActive |
| `() => "Set this to true, to move the elevator entry to the first level..."` | `() => base.Helper.Translation.Get("FirstLevelElevatorActive.description")` | FirstLevelElevatorActive.description |
| `() => "ElevatorCostPerStep"` | `() => base.Helper.Translation.Get("ElevatorCostPerStep")` | ElevatorCostPerStep |
| `() => "Set this to a higher number than 0 to enable payment..."` | `() => base.Helper.Translation.Get("ElevatorCostPerStep.description")` | ElevatorCostPerStep.description |

**zh.json内容：**
```json
{
    "ElevatorStep": "电梯间隔",
    "ElevatorStep.description": "此值决定电梯出现的频率",
    "Difficulty": "难度",
    "Difficulty.description": "此值也影响电梯出现的频率。难度值越高，电梯越少，需要下降更远才能解锁新电梯",
    "FirstLevelElevatorActive": "第一层电梯启用",
    "FirstLevelElevatorActive.description": "设置为true可将电梯入口移到第一层。如果在洞穴入口看不到电梯，请启用",
    "ElevatorCostPerStep": "每层电梯费用",
    "ElevatorCostPerStep.description": "设置为大于0的数字可启用使用电梯时支付每层费用。公式为（显示的电梯位置）* 每层电梯费用。此费用将从当前可用资金中扣除。如果没有足够的资金，电梯将不会被使用"
}
```

---

### 5. PolyamorySweetKiss (PolyamorySweetKiss.dll)

**文件位置：** `D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods\PolyamorySweet\PolyamorySweetKiss\PolyamorySweetKiss.dll`

**需要修改的代码：**

| 原始字符串 | 修改为 | 翻译键 |
|-----------|--------|--------|
| `() => "Mod Enabled"` | `() => base.Helper.Translation.Get("EnableMod")` | EnableMod |
| `() => "Roommate kisses"` | `() => base.Helper.Translation.Get("RoommateKisses")` | RoommateKisses |
| `() => "Min Hearts For Marriage Kiss"` | `() => base.Helper.Translation.Get("MinHeartsForMarriageKiss")` | MinHeartsForMarriageKiss |
| `() => "Hearts For Friendship"` | `() => base.Helper.Translation.Get("HeartsForFriendship")` | HeartsForFriendship |
| `() => "Unlimited Daily Kisses"` | `() => base.Helper.Translation.Get("UnlimitedDailyKisses")` | UnlimitedDailyKisses |

**注意：** 需要继续查看后面的代码，可能会有更多选项。

**zh.json内容：**
```json
{
    "EnableMod": "启用模组",
    "RoommateKisses": "室友亲吻",
    "MinHeartsForMarriageKiss": "婚姻亲吻最低心数",
    "HeartsForFriendship": "友谊心数",
    "UnlimitedDailyKisses": "每日无限亲吻"
}
```

---

### 6. Unlockable Bundles

**文件位置：** `D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods\Unlockable Bundles\Unlockable Bundles.dll`

**操作步骤：**
1. 用dnSpy打开DLL
2. 搜索 `GenericModConfigMenu` 或 `AddBoolOption`
3. 找到GMCM注册代码
4. 按照上述模式修改硬编码字符串
5. 创建i18n/zh.json文件

---

### 7. SkipFishingMinigame

**文件位置：** `D:\Apps\Steam\Steam\steamapps\common\Stardew Valley\Mods\SkipFishingMinigameDotnet5\SkipFishingMinigame.dll`

**操作步骤：**
1. 用dnSpy打开DLL
2. 搜索 `GenericModConfigMenu` 或 `AddBoolOption`
3. 找到GMCM注册代码
4. 按照上述模式修改硬编码字符串
5. 创建i18n文件夹和zh.json文件

**注意：** 此MOD目前没有i18n文件夹，需要先创建。

---

## 常见问题

### Q1: dnSpy打开DLL后看不到代码？
A: 确保已安装.NET Desktop Runtime。dnSpy需要它来反编译.NET程序集。

### Q2: 修改后编译出错？
A: 确保添加了正确的程序集引用。在dnSpy中，点击Edit Method后，如果出现红色错误，点击"Add Assembly Reference"按钮，添加SMAPI的DLL。

### Q3: 修改后MOD无法加载？
A: 恢复备份的DLL，重新操作。

### Q4: MOD更新后需要重新修改？
A: 是的，MOD更新会覆盖修改。建议保留修改记录，方便更新后重新操作。

---

## 完成后的验证

1. 启动游戏
2. 打开SMAPI控制台，确认没有错误
3. 进入选项 → MOD配置，查看翻译是否生效

## 备份位置

所有原始DLL备份在：`D:\星露谷MOD\DLL备份\`
