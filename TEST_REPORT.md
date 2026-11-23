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

## 3. 真机验收（待真机执行，无法由上述测试替代）

见 `docs/build.md` 末尾清单。需要：iPhone + USB 数据线 + Apple 驱动 + 合法认证材料。

**必须由用户本人完成的动作**（工具不会代答或代判定）：

1. 在 iPhone 点击「信任此电脑」并输入锁屏密码；
2. 在 iPhone 地图 / 目标 App 确认目标位置；
3. 确认健康 App 及定位相关设置状态；
4. 会话结束后确认位置已恢复真实定位。

## 总览

- 单元 + 模拟设备测试：**39 项全部通过**。
- 真机验收：**未执行**（当前环境无真机/认证材料），列于待办。
