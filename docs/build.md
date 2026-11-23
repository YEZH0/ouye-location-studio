# 构建说明 / Build

## 环境

- Windows 10/11 x64
- Python 3.11+（建议 3.12/3.13）
- Apple Mobile Device USB 驱动（随 iTunes 或 Microsoft Store「Apple 设备」提供）

## 依赖安装

```sh
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## 运行测试

```sh
pytest -q                                  # 单元测试（wire/profile/auth/state/presets/auth_helper）
pytest -q tests/test_engine_mock.py        # 模拟设备测试（脚本化 iAP2 对端，无真机）
```

真机验收需单独执行并单独报告，见文末清单。

## 构建 EXE

```sh
python packaging/build_windows.py
```

脚本依次用 PyInstaller 构建两个产物：

1. `ouye-auth-helper.exe`（控制台，认证助手，持有私钥）
2. `OUYELocationStudio.exe`（窗口化 GUI，运行时会拉起旁边的认证助手）

产物输出到 `dist/`。认证助手与 GUI 放置在同一目录。

> 若本机未安装 Apple 驱动、未连接真机或未配置认证材料，构建产物仍可启动，
> 但定位链路与认证会如实失败，不会伪造结果。

## 真机验收清单（待真机验证）

以下条目需要真机与合法认证材料，**无法由单元/模拟测试替代**，请逐项确认：

1. USB 连接后 GUI 能检测到设备；iPhone 弹出「信任此电脑」并成功配对。
2. CarKit 服务打开成功，iAP2 握手完成。
3. 身份识别被接受（`0x1D02`）。
4. 配置合法认证材料后，认证成功（`0xAA05`）；未配置时如实报错。
5. 设备请求定位（`0xFFFA`）后，GGA/RMC 语句被链路 ACK。
6. 在 iPhone 上**人工确认**地图蓝点是否移动到目标位置（工具不代为判定）。
7. 点击「停止定位」后，设备停止请求（`0xFFFC`），并人工确认位置恢复。
8. 异常场景：无设备、认证失败、中途断开、超时、重复点击、窗口退出均能清理会话。

## 常见问题

- **未检测到设备**：确认数据线支持数据传输、已安装 Apple 驱动、iPhone 已解锁并点击「信任」。
- **认证失败（AA04）**：证书/私钥不匹配或不被设备接受；请使用合法且匹配的配件身份。
- **设备断开**：重新插拔并重新「检测设备」。
