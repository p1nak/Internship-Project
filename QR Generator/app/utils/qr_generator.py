import qrcode
from PIL import Image
import os


def generate_qr(machine_id, base_url, save_dir):
    """Generate QR code for a machine and save as PNG."""
    url = f"{base_url}/machine/{machine_id}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#1a1a2e', back_color='white').convert('RGB')
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{machine_id}.png"
    filepath = os.path.join(save_dir, filename)
    img.save(filepath)
    return filename
