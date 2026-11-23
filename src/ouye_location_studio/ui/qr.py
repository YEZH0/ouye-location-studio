"""QR code generation for the author / repository link area.

Only the verified repository URL (``brand.QR_TARGET_URL``) is ever encoded.
No unverifiable social-media URL is generated.
"""

from __future__ import annotations

import io

from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_M


def make_qr_pixmap(text: str, box_size: int = 7, border: int = 2):
    """Render ``text`` as a QR code and return a QPixmap (or None on failure)."""
    try:
        from PySide6.QtGui import QImage, QPixmap
    except ImportError:  # pragma: no cover - non-GUI environment
        return None

    qr = QRCode(error_correction=ERROR_CORRECT_M, box_size=box_size, border=border)
    qr.add_data(text)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    image.convert("RGBA").save(buffer, format="PNG")
    data = buffer.getvalue()
    qimage = QImage.fromData(data)
    if qimage.isNull():  # pragma: no cover
        return None
    return QPixmap.fromImage(qimage)
