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
├── platforms/     平台适配（Windows USB，macOS 预留）
├── ui/            PySide6 图形界面
├── state.py       统一状态接口（Windows / macOS 共用）
├── auth_helper.py 本地 MFi-v3 认证助手（私钥不进入引擎进程）
├── presets.py     坐标预设
└── brand.py       品牌与出处信息
```

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

真机验收见 `docs/build.md` 末尾的「真机验收清单」。

## 构建 Windows EXE

```sh
python packaging/build_windows.py
```

产物输出到 `dist/`。详见 `docs/build.md`。

## 许可

GPL-3.0-only。见 `LICENSE` 与 `THIRD_PARTY_NOTICES.md`。
