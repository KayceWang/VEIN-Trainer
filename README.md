# VEIN修改器 · VEIN Trainer

适用于 Windows 64 位的本地 VEIN 单机辅助工具。界面集中展示角色、物品与配方、属性、载具、天气、物理和传送功能，支持快捷键与明暗主题。

> 当前只适配一个已核对的游戏版本；程序会校验游戏文件，版本不符时停止修改。需要自行安装正版游戏和 Python 3.11，不包含游戏程序或存档。

## 使用

1. 安装 [Python 3.11](https://www.python.org/downloads/) Windows 64 位版本，保留 Tcl/Tk 和 Python Launcher 组件。
2. 下载并解压本仓库，或下载 Releases 中的 Windows ZIP。所有文件应放在同一个目录中。
3. 双击 `启动VEIN修改器.vbs`。也可以在目录内运行：

   ```powershell
   py -3.11 vein_helper.py
   ```

4. 进入 VEIN 本机单机世界，关闭背包、菜单、聊天框和控制台，再点击“开始修改”。
5. 点击功能按钮或设置快捷键。持续功能默认关闭，开启和关闭有不同的提示音；再次点击顶部运行按钮停止并恢复本次修改的物理参数。

程序自动读取 Steam 库路径。如果安装在无法自动识别的位置，可以在启动前指定完整游戏程序路径：

```powershell
$env:VEIN_GAME_EXE = 'D:\SteamLibrary\steamapps\common\Vein\Vein\Binaries\Win64\Vein-Win64-Test.exe'
py -3.11 vein_helper.py
```

## 功能

| 分组 | 内容 |
| --- | --- |
| 角色 | 治疗角色、治疗所有玩家、无敌模式、无限耐力 |
| 物品 | 1,362 种物品的中文分类与搜索、数量选择、一键添加、给予每种物品 |
| 配方与耐久 | 学习所有配方、学习所有建造、恢复手持物品耐久 |
| 属性与状态 | 选择技能增加经验、设置角色状态 |
| 载具与目标 | 给予车辆钥匙、修复轮胎、解锁和撬开准星目标 |
| 世界 | 天气、发现所有地点、清除尸体、增加时间、随机时间、生成尸潮 |
| 物理与传送 | 超级速度、超级跳跃、低重力、291 个地点的传送选择 |
| 界面 | 中文、英语、西班牙语、法语、俄语；白天和夜间模式 |

除刷物品外，功能通过附带的本地连接模块在游戏线程中调用原生功能，或直接读写已核对的角色状态，不弹出控制台、不模拟输入。刷物品仍使用游戏控制台自动发送。

快捷键在游戏或修改器位于前台且修改器正在运行时生效；其他应用在前台时不触发。快捷键、语言和主题保存在本地，不随仓库分发。

界面与分类支持五种语言。当前物品名称保留中文，外语界面中的地点使用原生英文名称。

## 实测与适配范围

- 治疗已验证通过新的游戏线程调用入口被游戏接受。
- 手持物品修复已实测：同一物品损坏值从 6.7333% 降到 0%，耐久恢复为 100%。修复目标是手里拿着的武器或工具。
- 无限耐力的状态写入、物理参数回读和关闭后的恢复已检查。尚未完成长时间奔跑测试。
- 19 项直接操作均检查过不调用控制台输入；不等于已经逐项验证所有游戏效果。未为测试而批量执行清尸体、改时间、传送等世界操作。
- 支持版本的游戏可执行文件 SHA-256：

  ```text
  97707445b6e3b940c9efddca605124aac64d577f2945019efaa98122818344d5
  ```

仅支持本机单机世界。学习配方、经验、物品、传送等操作可能由游戏保存；关闭开关不会撤销这些一次性操作。请正常退出工具，以便恢复持续功能。备份功能排除 `start.vns`，不覆盖或恢复原存档。

## 源码与检查

运行不依赖第三方 Python 包，使用标准库、Tkinter 和 Windows API。`vein_native.dll` 是由本仓库的 `native_bridge.c` 编译的 64 位模块。它使用目标游戏线程的消息钩子传递请求，限制可执行操作，验证版本、单机世界及角色身份；不改写游戏磁盘文件。

```powershell
py -3.11 tests/test_helper.py
py -3.11 tests/test_hotkey_dispatch.py
py -3.11 tests/test_windows_backend.py
py -3.11 tests/test_native_bridge.py
py -3.11 tests/test_direct_routing.py
py -3.11 tests/test_ui.py
py -3.11 tests/test_preferences.py
py -3.11 tests/test_game_path.py
```

这些检查不加载游戏存档；部分会创建隐藏的 Tk 窗口，需 Windows 桌面环境。原生模块检查使用测试进程验证消息传递和错误版本拒绝，不对游戏执行操作。

如需重新编译原生模块，安装 [Zig](https://ziglang.org/download/) 后运行：

```powershell
zig cc -shared -O2 -s native_bridge.c -o vein_native.dll -luser32
```

本次发布使用 Zig 0.15.2 构建。修改器源文件与游戏对应关系见 [使用说明](使用说明.txt)；游戏图标与目录数据来源见 [第三方说明](THIRD_PARTY_NOTICES.md)。

## English

A Windows x64 local single-player VEIN trainer with hotkeys, distinct toggle sounds, five UI languages, and light/dark themes. Requires Python 3.11 with Tkinter and the exact verified game build. Non-item actions run through the game's own execution path or verified state access without opening the console; item spawning still uses console input. Item display names currently remain Chinese. Not all game effects have been tested. See the translated help files in `docs/`.

这是独立开发的辅助工具，与游戏官方没有隶属关系。当前尚未指定开源许可证；游戏名称、图标和原生文本的权利归各自权利人。
