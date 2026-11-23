"""Single source of truth for branding and attribution.

All user-visible author identity lives here so the GUI serves it from one place.
Social-media references are *search hints only*: no unverifiable URL is encoded
or linked, per project policy.
"""

from __future__ import annotations

from typing import Any

# --- identity -------------------------------------------------------------

BRAND = "欧耶哥爱数码"
AUTHOR = "YEZH0"
AUTHOR_NAME = "YEZHI"
HOMEPAGE = "https://github.com/YEZH0/ouye-location-studio"

# Channels where the full walkthrough lives. The keyword is identical across
# platforms so a single search finds the tutorial. We deliberately do NOT ship
# per-platform URLs (they change and cannot be verified), only the keyword.
TUTORIAL_KEYWORD = "欧耶哥爱数码"

CHANNELS: list[dict[str, str]] = [
    {"platform": "抖音", "handle": TUTORIAL_KEYWORD},
    {"platform": "小红书", "handle": TUTORIAL_KEYWORD},
]

TUTORIAL_HINT = f"抖音 / 小红书 搜「{TUTORIAL_KEYWORD}」领取详细使用教程"
TUTORIAL_LONG = (
    f"完整教程、认证材料准备、认证失败排查、多设备切换，"
    f"请到抖音或小红书搜索「{TUTORIAL_KEYWORD}」。"
)

FOOTER_NOTE = f"{BRAND} · 原创工具，转载请注明出处"

# The only URL that is safe to encode in a QR code is the verified repository.
QR_TARGET_URL = HOMEPAGE

# --- disclaimer ------------------------------------------------------------

DISCLAIMER_TITLE = "免责声明"
DISCLAIMER_SHORT = "仅供 iOS 定位技术研究 · 禁止考勤打卡、游戏作弊、薅羊毛等欺诈用途"

DISCLAIMER: list[str] = [
    "本项目通过 iAP2 配件协议向 iPhone 提供模拟定位信息，仅面向 iOS 开发者做定位相关功能的技术研究。",
    "禁止用于企业考勤打卡、游戏作弊、活动薅羊毛、轨迹造假、虚假报备等欺诈、规避风控场景。",
    "本工具不会自动把「发送成功 / ACK / 引擎 active」判定为手机定位成功；"
    "手机是否真正应用定位，需要由使用者本人在 iPhone 上确认。",
    "使用者自行承担 Apple 账号风控、设备功能失效、平台封禁等全部后果，"
    "项目作者不对违规使用承担任何责任。衍生分发须遵循原开源协议（GPL-3.0-only）。",
]


def brand_payload() -> dict[str, Any]:
    """Serialisable branding block for the GUI and any future frontend."""
    return {
        "brand": BRAND,
        "author": AUTHOR,
        "author_name": AUTHOR_NAME,
        "homepage": HOMEPAGE,
        "tutorial_keyword": TUTORIAL_KEYWORD,
        "tutorial_hint": TUTORIAL_HINT,
        "tutorial_long": TUTORIAL_LONG,
        "footer_note": FOOTER_NOTE,
        "channels": CHANNELS,
        "qr_target_url": QR_TARGET_URL,
        "disclaimer_title": DISCLAIMER_TITLE,
        "disclaimer_short": DISCLAIMER_SHORT,
        "disclaimer": DISCLAIMER,
    }
