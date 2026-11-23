# 来源与致谢 / Sources

本实现由公开的协议研究与互操作性分析支撑。下列参考资料用于说明协议行为；第三方二进制、
身份文件、抓包会话均不包含在本仓库内。

- [JJTech0130 的 CarKit 探测](https://gist.github.com/JJTech0130/a878496479afedb93dd02399551e3aec)：
  USB lockdown 服务与控制会话协商。
- [wiomoc 的 MFi/iAP 研究](https://wiomoc.de/misc/posts/mfi_iap.html) 与
  [iap2 实现](https://github.com/wiomoc/iap2)：帧结构、身份识别、认证与蓝牙传输。
- [xcertplay](https://github.com/shilapi/xcertplay)：控制消息标识、嵌套能力声明、定位订阅与上报间隔。
- [Showcase](https://github.com/amineross/showcase)：BAA 证书消息布局。
- [PlayPort](https://github.com/youcci/playport) 与 [DiPlay](https://github.com/shihabal3amri/DiPlay)：
  本地 MFi-v3 认证、challenge/signature 编码与身份配置背景。
- [accessory-location 研究](https://nvme0n1p.dev/posts/ios-location-modify) 与
  [CarPlay 认证研究](https://nvme0n1p.dev/posts/about-carplay-mfi)：配件提供定位与认证边界背景。
- [Apple 定位来源文档](https://developer.apple.com/documentation/corelocation/cllocationsourceinformation/isproducedbyaccessory)：
  区分「配件产生」与其他定位来源。

Python USB 传输使用 [pymobiledevice3](https://github.com/doronz88/pymobiledevice3)。
加密运算使用 [cryptography](https://cryptography.io/)。图形界面使用 Qt for Python (PySide6)。

## 直接上游

| 项目 | 提交 SHA | 许可 |
| --- | --- | --- |
| xmz28/tetherpin-ios | `791b308ae51343b344a76afe5a3f7a02a5aa6dbf` | GPL-3.0-only |
| YEZH0/ios-location-studio（仅参考交互/品牌） | `6d896872c7c97bdf49e0893a53262f4764e88d47` | MIT |

> 协议兼容性说明：TetherPin 发布版 **v1.0.0**（tag，提交 `b918be4`）与其最新 main 的协议核心
> （wire/link/profile/auth/transport/cli）逐字节一致（SHA-256 相同），本项目复用即等价于 v1.0.0 的协议核心。
> 详见 `docs/real_device_path.md`。
