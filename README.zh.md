# osu-checker

<img src="assets/logo.png" width="96" align="right">

面向 **SayoDevice O3C**（Gateron KS-20 磁轴）的 osu! 游戏分析工具。它把你的
手和手指实际做了什么，与游戏实际判定了什么放在一起对比，并把失误归类为技术、
设备设置和游戏设置三类。

语言：**[English](README.md) · [Українська](README.uk.md) · 中文**

---

## 下载

从 [Releases](../../releases) 下载 `osu-checker-windows.zip`，解压到任意目录，
运行 `osu-checker.exe`。仅支持 Windows，无需安装 Python。

## 各标签页

### 分析

把 `.osr` 拖到窗口里，或点击「最新的 osu! 回放」。osu!stable 和从 osu!lazer
导出的回放都支持。

**总览** — 左右手各自的击打误差与 UR、带 300/100 判定窗标记的直方图、整张谱面
的误差变化，以及按 BPM 的分组表。关键的一列是 **漂移**：一段连打从开头到结尾
误差增加了多少。

**瞄准** — 光标相对圆圈中心的落点。这里把三件常被混为一谈的事分开：

| 指标 | 含义 |
|---|---|
| 偏移 | 光标总是落在某一侧 |
| 离散度 | 落点围绕中心，但离得远 |
| 过冲 | 冲过目标再回来 |

另外还有按跳跃距离和按八个方向的细分。

**问题片段** — 谱面中失分最多的片段，附带时间、失分和原因：*跟不上*、
*抢拍*、*离散*、*瞄准*。

### 录制

同时记录三个来源：

| 来源 | 内容 | 频率 |
|---|---|---|
| Raw Input | 仅来自 O3C 的按键 | 事件驱动，约 1 毫秒 |
| HID 轮询 | 三个键的行程，微米 | 约 2660 Hz（0.37 毫秒） |
| GetCursorPos | 光标位置 | 按 500 Hz 轮询 |

之所以需要它，是因为 osu! 回放每秒只写入约 62 帧，把所有时间数据都取整到约
16 毫秒。停止后，该页会显示每个键的真实按压深度，以及距离触发点还剩多少余量。

保存下来的录制可以在「分析」页附加进去，这样结论里就多了按压深度这一项，而这
是回放本身根本不包含的。

### 训练

训练计划由上一次分析的数据生成。每个训练项都带有**可验证的标准**，本程序会在
你的下一个回放里检查它。「从我的谱面库中挑选」会在你自己的谱面里寻找目标 BPM
的连打图。

### 设置

语言、osu! 路径，以及谱面索引（MD5 → `.osu`）。

## 各种原因如何区分

| 数据表现 | 结论 |
|---|---|
| 误差从连打开头到结尾持续增加 | 速度不够，手维持不住节奏 |
| 按键次数多于音符，误差本身平稳 | 多打 |
| 左右手平均误差不同 | 双手不同步，属于技术问题 |
| 多个回放上都存在平稳的偏移 | 音频偏移或延迟 |
| 同一个键上快于 45 毫秒的重复按键 | 双击触发，Rapid Trigger |
| 该片段光标远离圆心 | 问题在瞄准，不在敲击 |
| 按压深度勉强越过阈值 | 按得不够深，应降低触发点 |

## 关于设备

SayoDevice O3C，`VID 0x8089 / PID 0x0009`。本程序**只读**：只发送状态读取请求，
从不改动设备配置。

协议是**请求/应答**，不是数据流。设备在被询问之前保持沉默；网页配置器大约每秒
轮询 20 次，所以从外面看起来像是数据流。

上限取决于设备本身设置的 USB 轮询频率。在 **8000 Hz** 下，一次往返约
**0.37 毫秒**，大致是三个 USB 帧，因此三个键可以每秒采样约 2660 次。在
1000 Hz 下，一次往返大约需要 2 毫秒。

请求，usage page `0xFF12`，1024 字节包：

```
0x00  report_id 0x22
0x01  echo 0x03
0x02  checksum u16 LE  （把整包按 u16 求和，校验位先清零）
0x04  len u16 LE = 0x0004
0x06  id 0x15
0x07  index 0x01       <- index=1 才返回毫米值
```

应答为 `len=0x000a`，随后是三个 `u16`：按键行程，单位微米，静止为 `0`，
4 毫米全行程为 `4000`。`index=0` 返回单个键的原始 ADC，`index=2` 返回三个键的
原始 ADC。按键索引为 `P = 0, V = 1, B = 2`。

接口 `0xFF11` 使用同一套协议，包长 64 字节；请求 `0x1F` 会返回单个键的 16 个
连续采样，但无法切换是哪个键，因此实际使用的是 `0xFF12`。

轮询频率可以在「录制」页限制，但意义不大：不限制时约占用单核的 9%，这比任何精确
的限制都更省——在 Windows 上等待时间片消耗的资源比省下的还多。

### 已知限制

- 50 和 miss 的统计与 osu! 略有出入，因为游戏会单独判定滑条头。300 的统计误差
  在 0.1% 以内，敲击分析正是建立在这一项上的。
- 录制与回放的关联目前是手动的：按压深度按整个录制取汇总值，没有与单个音符对齐。
- 光标的游戏区域几何按 osu!stable 的公式计算（640×480 虚拟屏幕中的 512×384，
  向下偏移 8 个虚拟像素），并在 osu! 窗口处于前台时从窗口读取。

## 关于按键自动重复

按住一个键时，Windows 会在约 500 毫秒延迟后每约 30 毫秒发送一次
`WM_KEYDOWN`，Raw Input 同样会报告这些事件。录制器按键状态把它们过滤掉，否则
按住两秒会被记成 50 次按键。

## 隐私

录制器使用 Raw Input，它会报告设备的 HID 句柄。只有来自
`VID_8089&PID_0009` 的事件会被记录，并且默认只在 osu! 窗口处于前台时记录。
在普通键盘上输入的内容，本程序看不到。

## 从源码构建

Windows，Python 3.12 及以上。

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run.py
```

生成可分发的目录：

```
.venv\Scripts\python.exe -m pip install pyinstaller pillow
.venv\Scripts\python.exe tools\make_icon.py
.venv\Scripts\python.exe tools\build.py
```

结果是 `dist\osu-checker\`，把这个文件夹打包成 zip，就能在任何没有 Python 的
Windows 机器上运行。这里刻意使用 `onedir`：`onefile` 每次启动都要把约 160 MB
解压到临时目录。

## 诊断

打包后的程序带有自检模式，不会打开窗口，并把报告写入
`%APPDATA%\osu-checker\selftest.txt`：

```
osu-checker.exe --selftest
osu-checker.exe --selftest "路径\到\回放.osr"
```

它会检查 `osrparse` 的导入、图标、设备在 HID 上是否可见、谱面索引的大小，以及
在给出路径时完整分析一个回放。这一项正是为打包版准备的：有些问题只在
PyInstaller 之后才出现，而无控制台的窗口程序不会显示它们。

## 程序数据

开发模式下在 `data/` 目录。打包后在 `%APPDATA%\osu-checker`：`config.json`、
谱面索引 `beatmap_index.json`，以及配置缓存 `map_profiles.json`。

## 如何添加语言

复制 `osuchecker/translations/en.py`，翻译其中的值，保持键名和 `{占位符}` 不变，
然后把语言代码加入 `osuchecker/i18n.py` 中的 `LANGUAGES`。

## 致谢

O3C 的 HID 协议是在设备上实测得出的，包结构参考了
[khang06](https://gist.github.com/khang06/6186543b560548370ce7cc08cad7f710)
公开的逆向笔记，以及 clean-room 固件项目
[ankurCES/sayofw-o3c](https://github.com/ankurCES/sayofw-o3c)。

回放解析使用 [osrparse](https://github.com/kszlim/osu-replay-parser)。

本项目与 osu! 和 SayoDevice 均无关联。

## 许可证

MIT，见 [LICENSE](LICENSE)。
