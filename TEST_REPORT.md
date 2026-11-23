# 测试记录 / Test report

三类测试**分开报告**：单元测试、模拟设备测试、真机验收。

## 1. 单元测试（无设备、无凭证）

覆盖协议帧、坐标/NMEA、认证边界、状态接口、预设与品牌。

```sh
pytest -q tests/test_wire.py tests/test_profile.py tests/test_auth.py \
          tests/test_state.py tests/test_presets.py tests/test_auth_helper.py
```

结果（Windows x64，Python 3.13）：

| 文件 | 内容 | 结果 |
| --- | --- | --- |
| test_wire.py | 帧编解码、校验和、消息分片/重组、非法标记/短消息拒绝 | 通过 |
| test_profile.py | 坐标格式化、越界拒绝、NMEA 校验和、身份声明 | 通过 |
| test_auth.py | BAA/MFi 证书参数、挑战透传、非法响应拒绝 | 通过 |
| test_state.py | 事件序列化、状态快照、剩余秒数 | 通过 |
| test_presets.py | 预设坐标合法、ID 唯一、品牌无未验证 URL | 通过 |
| test_auth_helper.py | 自签名测试身份：匹配/不匹配校验、证书+签名往返、签名前置检查 | 通过 |

> test_auth_helper.py 使用**临时生成的短时自签名测试身份**，不使用任何真实证书或私钥。

## 2. 模拟设备测试（无真机、无 USB、无凭证）

脚本化进程内「手机」对端驱动完整 iAP2 会话：握手 → 身份识别 → 认证 → 定位订阅 → 停止。

```sh
pytest -q tests/test_engine_mock.py
```

| 用例 | 验证点 | 结果 |
| --- | --- | --- |
| test_full_session_event_sequence | 完整事件序列；`phone_location_verified` 恒为 False（不自动判定手机定位成功） | 通过 |
| test_nmea_sent_matches_target | 引擎写出 GGA/RMC，坐标片段与目标一致 | 通过 |
| test_stop_is_requested_cleanly | 跨线程停止；`stop_reason == "stopped"` | 通过 |
| test_missing_auth_material_is_reported | 未配置认证材料时如实报错 | 通过 |

## 3. 真机验收

### 3.1 环境检测（2026-11-23 执行）

| 项目 | 结果 |
| --- | --- |
| Apple Mobile Device USB 驱动 | 已安装（注册表 USBAAPL64 命中） |
| USB 设备检测 | 1 台 iPhone/iPad 通过 USB 连接 |
| lockdown 信任状态 | 已信任（会话建立成功） |
| 设备型号 | iPhone15,4（iPhone 15 Pro） |
| 系统版本 | iOS 27.0.1 |
| 认证材料（MFi v3 证书 + 私钥） | **未配置**（阻断项，见下） |

> 设备诊断只读取通用型号/系统版本信息，**不读取、不输出**序列号、UDID、Apple ID 或健康数据。

### 3.2 真机负向验收（2026-11-23 执行，无认证材料）

走真实 iAP2 链路，验证「无认证材料时如实报错并干净清理」，全程不发送 NMEA、不改变手机位置：

| 步骤 | 结果 |
| --- | --- |
| 打开 `com.apple.carkit.service`（iAP2 服务） | 成功 |
| iAP2 握手 | 成功（link_ready） |
| 身份识别（0x1d00 → 回复 → 0x1d02） | 设备接受（identification_accepted） |
| 设备发起认证要求（0xaa00） | 引擎如实报错：`需要配件认证，但尚未配置认证材料（证书与私钥）` |
| 会话清理 | 干净退出（link + adapter 均关闭） |

结论：**真实 iAP2 协议链路已打通到「认证请求」一步**，USB 通信、消息解析、身份识别、事件流、阻断与清理行为均正确。剩余定位（认证 → 订阅 → NMEA → 手机实际定位）因认证材料缺失而**如实阻断**，未伪造成功。

### 3.3 真机定位验收（待用户配置合法认证材料后执行）

见 `docs/build.md` 末尾清单。需要：合法 MFi v3 `certificate.p7b` + `identity.pk8`（GUI 认证材料区填写路径）。

**必须由用户本人完成的动作**（工具不会代答或代判定）：

1. 在 iPhone 点击「信任此电脑」并输入锁屏密码；
2. 在 iPhone 地图 / 目标 App 确认目标位置；
3. 确认健康 App 及定位相关设置状态；
4. 会话结束后确认位置已恢复真实定位。

## 总览

- 单元测试：**35 项全部通过**。
- 模拟设备测试：**4 项全部通过**。
- 真机环境检测 + 负向验收：**通过**（iAP2 链路打通至认证请求）。
- 真机定位验收：**阻断**——待用户提供合法 MFi 认证材料后执行（不伪造、不绕过）。
