"""Генерирует QR-коды для квеста и лист A4 для печати.

Запуск:  pip install qrcode reportlab pillow
         python3 make_qr.py [БАЗОВЫЙ_URL]

По умолчанию адрес — GitHub Pages этого репозитория.
Ключи этапов берутся из index.html (поле key: "ulika-...").
"""
import re
import sys
from pathlib import Path

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = Path(__file__).parent
BASE = sys.argv[1] if len(sys.argv) > 1 else "https://casper1ded1.github.io/podryad/kvest/"
QR_SIZE = 3.5 * cm          # сторона QR на печати (3–4 см)
CARD_W, CARD_H = 5.2 * cm, 6.4 * cm

html = (HERE / "index.html").read_text(encoding="utf-8")
keys = re.findall(r'key:\s*"(ulika-[a-z0-9]+)"', html)
out = HERE / "qr"
out.mkdir(exist_ok=True)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
pdfmetrics.registerFont(TTFont("Serif", FONT))

pngs = []
for i, key in enumerate(keys, 1):
    url = f"{BASE}#{key}"
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2, box_size=20)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2b1e19", back_color="white").convert("RGB")
    path = out / f"ulika-{i}.png"
    img.save(path)
    pngs.append((i, path, url))
    print(f"QR №{i}: {url}")

pdf = canvas.Canvas(str(HERE / "qr-dlya-pechati.pdf"), pagesize=A4)
pw, ph = A4
cols = 3
gap_x = (pw - cols * CARD_W) / (cols + 1)
gap_y = 1.0 * cm
pdf.setFont("Serif", 9)
pdf.setFillColorRGB(.45, .38, .3)
pdf.drawString(gap_x, ph - 1.2 * cm, "Вырезать по пунктиру. QR 3,5 см. №1 — вручаешь сам, остальные кладёшь к подаркам по маршруту.")
for n, (i, path, _) in enumerate(pngs):
    r, c = divmod(n, cols)
    x = gap_x + c * (CARD_W + gap_x)
    y = ph - 2 * cm - (r + 1) * CARD_H - r * gap_y
    pdf.setDash(3, 3)
    pdf.setStrokeColorRGB(.6, .6, .6)
    pdf.rect(x, y, CARD_W, CARD_H)
    pdf.setDash()
    pdf.setFillColorRGB(.17, .12, .1)
    pdf.setFont("Serif", 11)
    pdf.drawCentredString(x + CARD_W / 2, y + CARD_H - 0.8 * cm, f"Улика № {i}")
    pdf.drawImage(ImageReader(str(path)), x + (CARD_W - QR_SIZE) / 2, y + 1.2 * cm, QR_SIZE, QR_SIZE)
    pdf.setFont("Serif", 7.5)
    pdf.setFillColorRGB(.64, .09, .18)
    pdf.drawCentredString(x + CARD_W / 2, y + 0.6 * cm, "Наведи камеру, детектив")
pdf.showPage()
pdf.save()
print("PDF:", HERE / "qr-dlya-pechati.pdf")
