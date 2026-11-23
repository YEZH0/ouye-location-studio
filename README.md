# OUYE Location Studio（Windows）

欧耶哥爱数码 · 基于 iAP2 配件协议的 iPhone 模拟定位工作台（Windows 版）。

仅面向 iOS 定位相关功能的技术研究。**禁止**用于考勤打卡、游戏作弊、薅羊毛、轨迹造假等欺诈用途。

> 本工具**不会**把「发送成功 / ACK / 引擎 active」自动判定为手机定位成功；手机是否真正应用定位，
> 必须由使用者本人在 iPhone 上确认。

## 与参考项目的关系

- iAP2 协议核心复用并适配自 [TetherPin](https://github.com/xmz28/tetherpin-ios)（GPL-3.0-only）。
  保持其认证流程、USB 通信、NMEA 编码、ACK、订阅与停止逻辑不变，仅做命名与分层适配。
- 用户交互、设备诊断、品牌与教程入口参考 [ios-location-studio](https://github.com/YEZH0/ios-location-studio)，
  **不**沿用其 DVT 核心与旧界面架构。
- 未修改任何已有仓库；仅在 `feat/windows-iap2-v1` 分支开发。

## 分层结构

```
src/ouye_location_studio/
├── core/          iAP2 协议核心（wire/link/profile/auth/engine）
├── platforms/     平台适配（Windows USB；macOS 见 feat/macos-iap2-v1）
├── ui/            PySide6 图形界面（跨平台）
├── state.py       统一状态接口（Windows / macOS 共用）
├── auth_helper.py 本地 MFi-v3 认证助手（私钥不进入引擎进程）
├── presets.py     坐标预设
└── brand.py       品牌与出处信息
```

## 图形界面特性

- 设备检测、坐标预设（含自定义坐标）、会话时长 / 发送间隔、倒计时与进度条。
- 开始定位前的**三项强制确认**（信任、地图位置、健康 App 状态），只能由你本人在 iPhone 上完成。
- 停止后**定位恢复确认**弹窗；异常均以红色横幅如实提示，不会出现虚假的「定位成功」。
- **浅色 / 深色主题**一键切换（窗口右上角「主题」按钮，自动记忆）。
- 首次使用须知、关于作者、开源许可页；抖音 / 小红书仅提供「搜索关键词」引导，不编造 URL；二维码只编码本仓库地址。

## 跨平台协作

本项目由 Windows 与 macOS 两个分支并行开发，共享 `core/`、`state.py`、`ui/` 与 `platforms/base.py`
接口；每个平台只维护自己的 adapter 与打包脚本。分工与分支规则见 `AGENTS.md`。

## 快速开始（源码）

```sh
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
ouye-location-studio           # 或 python -m ouye_location_studio
```

## 认证材料（阻断项）

配件认证需要一份合法的 **MFi-v3 配件身份**（`certificate.p7b` + `identity.pk8`）。本仓库不提供、
不内置、不分发任何证书或私钥。未配置时应用仍可完整运行其余流程，但配件认证会如实失败。

在 GUI 的「认证材料」区域填入你自己合法持有的文件即可；也可通过环境变量配置：

```sh
set OUYE_LOCATION_STUDIO_CERT_FILE=C:\path\to\certificate.p7b
set OUYE_LOCATION_STUDIO_KEY_FILE=C:\path\to\identity.pk8
```

详见 `docs/authentication.md`。

## 测试

```sh
pytest -q                        # 单元测试
pytest -q tests/test_engine_mock.py   # 模拟设备测试（无真机）
```

真机验收见 `docs/build.md` 末尾的「真机验收清单」；真机完整验收路径研究与合规边界见 `docs/real_device_path.md`。

## 构建 Windows EXE

```sh
python packaging/build_windows.py
```

产物输出到 `dist/`。详见 `docs/build.md`。

## 许可

GPL-3.0-only。见 `LICENSE` 与 `THIRD_PARTY_NOTICES.md`。
