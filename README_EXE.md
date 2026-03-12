# Battle Simulator GUI + EXE 打包说明

## 1. 启动图形界面（源码方式）
在项目目录执行：

```powershell
python battle_gui.py
```

界面支持左右玩家分别设置操作模式：

- 左侧角色可单独选择自动或手动。
- 右侧角色可单独选择自动或手动。
- 混合模式下（例如左自动右手动），系统会自动执行自动方回合，并在手动方回合停下等待你操作。

手动技能选择区位于窗口右下角“手动回合控制”面板中。

## 2. 打包成单文件 EXE
双击运行 `build_exe.bat`，或在终端执行：

```powershell
.\build_exe.bat
```

打包成功后会得到：

- `dist\battle_simulator.exe`
- 项目根目录同名副本：`battle_simulator.exe`

## 3. 对外发布建议
你可以只对外提供 `battle_simulator.exe`。

注意：
- 首次运行可能被 Windows Defender/SmartScreen 扫描。
- 若目标机器缺少某些系统运行库，建议在目标机器上做一次试运行验证。
- 如果你后续修改了源码，需要重新执行 `build_exe.bat` 再发布新的 EXE。
