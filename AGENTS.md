# AGENTS.md — 多 Agent 协作与分支规范

本仓库由两个平台 Agent 并行开发同一套代码库：

- **Windows Agent**（分支 `feat/windows-iap2-v1`）
- **macOS Agent**（分支 `feat/macos-iap2-v1`）

本文档是双方必须遵守的文件所有权、接口契约与分支协作规则。

## 1. 分层与共享边界

```
src/ouye_location_studio/
├── core/            # 共享：iAP2 协议核心（wire/link/profile/auth/engine）
├── state.py         # 共享：统一状态接口（Windows/macOS 前端共用）
├── ui/              # 共享：PySide6 GUI（跨平台）
├── platforms/       # 平台层：每个平台一个 adapter，互不修改对方文件
│   ├── base.py      # 共享：DeviceStream / PlatformAdapter 抽象契约
│   ├── windows.py   # Windows 独占
│   └── macos.py     # macOS 独占
├── auth_helper.py   # 共享：本地 MFi-v3 认证助手（JSONL 契约不变）
├── brand.py         # 共享：品牌/作者/社媒（未确认 URL 不得编造）
├── presets.py       # 共享：定位预设
├── paths.py         # 共享：运行时路径解析
└── version.py       # 共享：版本
```

## 2. 文件所有权矩阵

| 文件/目录 | 所有者 | 规则 |
| --- | --- | --- |
| `core/**` | 双方共享 | 改动须保持协议行为不变；接口变更需同步对方 |
| `state.py` | 双方共享 | 事件名/数据契约是跨平台 ABI，**不得随意改字段** |
| `ui/**` | 双方共享 | 只做跨平台兼容改动，不引入平台专用 API |
| `platforms/windows.py` | Windows Agent | macOS Agent 不得修改 |
| `platforms/macos.py` | macOS Agent | Windows Agent 不得修改 |
| `platforms/base.py`、`platforms/__init__.py` | 双方共享 | 新增平台 adapter 须在 `create_platform()` 注册 |
| `packaging/build_windows.py`、`*windows*`、`entry_gui.py` | Windows Agent | 独占 |
| `packaging/build_macos.py`、`*macos*`、`entry_macos.py` | macOS Agent | 独占 |
| `packaging/OUYELocationStudio.spec`、`auth_helper.spec` | Windows Agent | 独占 |
| `tests/test_macos_usb.py` | macOS Agent | 独占 |
| 其余 `tests/*` | 双方共享 | 增加用例不删改对方断言 |
| `AGENTS.md` | 双方共享 | 结构变更须双方同意 |

## 3. 分支规则

- 默认分支：`main`（只接受 PR 合并）。
- 每个平台在自己的 `feat/*` 分支开发，**禁止直接 push 到 `main`**。
- **禁止覆盖或 force-push 对方的分支**；force-push 仅限自己的功能分支。
- 合并路径：`feat/*` → PR → 评审 → `main`；不自动合并。
- 共享文件冲突时，先 rebase 自己分支到最新 `main`，再解决冲突，不得用 `-X theirs` 丢弃对方改动。

## 4. 跨平台接口契约（不可破坏）

- `PlatformAdapter` / `DeviceStream`（`platforms/base.py`）是引擎唯一依赖的传输抽象。
- `LocationEngine`（`core/engine.py`）只依赖 `PlatformAdapter` + `state`，不 import 任何平台文件。
- `state.py` 的事件名、`EngineEvent` 字段是 Windows/macOS 前端共用的协议，改动必须向下兼容。
- 新增平台 adapter 只需实现 `open()/close()/list_devices()`，在 `platforms/__init__.py` 的 `create_platform()` 按 `sys.platform` 分发即可，**无需改动 core/ui**。

## 5. 合规红线（双方强制）

1. **不内置、不分发任何 MFi 证书或私钥**；认证材料由使用者外部配置（`OUYE_LOCATION_STUDIO_CERT_FILE` / `KEY_FILE`）。
2. **不伪造定位成功**：发送成功、链路 ACK、引擎 active 都不等于手机已定位成功；`phone_location_verified` 恒为 `False`，须由用户本人确认。
3. **不沿用旧项目 DVT 强制检查**，不做开发者模式绕过。
4. **隐私**：不采集/不输出序列号、UDID、Apple ID、健康数据或真实位置。
5. 单活动定位会话；异常退出须尽力清理（`finally` 关闭 link/adapter/auth）。
6. 社媒 URL 无法确认时**不得编造**，只保留「搜索提示」；二维码只编码可验证的 GitHub 地址。
7. 不提取第三方 EXE 内置私钥，不复制无授权的认证材料。

## 6. 提交流程

- 提交信息用 `type(scope): 描述` 中文约定（feat/fix/test/docs/chore）。
- 测试分三类报告：单元测试、模拟设备测试、真机验收（见 `TEST_REPORT.md`）。
- 真机测试需用户在手机上点击/确认时，工具**必须**明确提示并等待真实确认，不得代答。
