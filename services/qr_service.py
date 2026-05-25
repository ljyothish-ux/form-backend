import qrcode
import io
from qrcode.image.pure import PyPNGImage

def generate_qr(url: str) -> bytes:
    """
    Takes a URL string
    Returns QR code as PNG bytes
    """

    # QR code settings
    qr = qrcode.QRCode(
        version=1,                          # 1 = smallest, auto-grows if needed
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # H = 30% damage recovery
        box_size=10,                        # size of each box in pixels
        border=4                            # white border around QR (minimum is 4)
    )

    qr.add_data(url)
    qr.make(fit=True)                       # auto pick best version for data size

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to bytes buffer instead of a file
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer.getvalue()