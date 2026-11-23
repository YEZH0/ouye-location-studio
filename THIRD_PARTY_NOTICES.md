# 第三方声明 / Third-party notices

OUYE Location Studio 包含对 TetherPin 的修改与适配：

- 上游：https://github.com/xmz28/tetherpin-ios （GPL-3.0-only）
- TetherPin 源自 xpqball/iap2-location-bridge-windows（baseline `3d0af910ac6868df99978f593adb2fcbd2de8cc1`），
  其本身源自 aur3l14no/accessory-location。
- 本项目保留 GPL-3.0-only 许可。详见 `LICENSE`、`docs/sources.md`、`docs/protocol.md`。

本仓库只复用协议核心（wire/link/profile/auth/transport 的 iAP2 帧结构、认证流程、
USB 通信、NMEA 编码、ACK、订阅与停止逻辑），并保留了 GPL-3.0-only 许可与来源说明。
作者个人宣传素材（图片、二维码、社媒链接等）未复制，品牌信息由本项目在 `src/ouye_location_studio/brand.py`
中独立维护。

## 认证材料（重要）

TetherPin 的发布产物中包含一份来自 DiPlay v0.2.7 APK 的实验性配件证书与对应私钥，该材料
未被 GPL 重新许可，且未包含在其 Git 源码中。**本仓库同样不包含、不内置、不分发任何 MFi
证书或私钥**，不提供自动下载或导入上述第三方身份文件的工具。

本应用通过外部配置接口（用户自备的 `certificate.p7b` 与 `identity.pk8`）接入合法的认证材料；
未配置时，配件认证会如实失败并明确提示阻断项，不伪造成功。认证材料的授权与分发责任由使用者
自行承担。详见 `docs/authentication.md`。

## 依赖

打包的 Windows 应用使用 Python、Qt (PySide6)、pymobiledevice3、cryptography、Pillow、
qrcode、pywin32 及其依赖。各依赖保留其自身许可。GPL-3.0 适用于本项目源码；各依赖的许可
文件在可执行文件解包目录的 `third_party_licenses` 下按需打包。

- PySide6：LGPL-3.0 / GPL-3.0 双许可
- pymobiledevice3：GPL-3.0
- cryptography：Apache-2.0 / BSD-3-Clause
- Pillow：HPND（历史许可）
- qrcode：BSD-3-Clause
- pywin32：PSF-2.0

地图数据（如未来接入）遵循 OpenStreetMap 许可；当前 Windows 版不内置地图瓦片。
