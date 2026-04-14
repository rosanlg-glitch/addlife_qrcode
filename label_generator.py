import os
from PIL import Image, ImageDraw, ImageFont
import qrcode

DPI = 300
MM_TO_PX = DPI / 25.4

LABEL_HEIGHT_MM = 36
LABEL_HEIGHT_PX = int(LABEL_HEIGHT_MM * MM_TO_PX)

PADDING_PX = int(3 * MM_TO_PX)
BORDER_PX = 3
LOGO_AREA_PX = int(30 * MM_TO_PX)
QR_SIZE_PX = int(22 * MM_TO_PX)
GAP_PX = int(4 * MM_TO_PX)

FONT_CANDIDATES = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "arial.ttf",
]


def load_font(size):
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def text_size(font, text):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def make_qr(data, size_px):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img.resize((size_px, size_px), Image.LANCZOS)


def load_logo(path, max_h, max_w):
    if not path or not os.path.exists(path):
        return None
    logo = Image.open(path).convert("RGBA")
    ratio = min(max_w / logo.width, max_h / logo.height)
    new_size = (max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio)))
    return logo.resize(new_size, Image.LANCZOS)


def generate_label(part_no, part_name, logo_path=None, output_path="label.png"):
    part_font = load_font(int(9 * MM_TO_PX))
    name_font = load_font(int(9 * MM_TO_PX))

    pn_w, _ = text_size(part_font, part_no)
    name_w, _ = text_size(name_font, part_name)
    text_col_w = max(pn_w, name_w)

    width = (
        BORDER_PX + PADDING_PX + LOGO_AREA_PX + GAP_PX
        + text_col_w + GAP_PX
        + QR_SIZE_PX + PADDING_PX + BORDER_PX
    )
    height = LABEL_HEIGHT_PX

    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)

    draw.rectangle(
        [0, 0, width - 1, height - 1],
        outline="black",
        width=BORDER_PX,
    )

    logo_max_h = height - 2 * PADDING_PX
    logo = load_logo(logo_path, logo_max_h, LOGO_AREA_PX)
    logo_x = BORDER_PX + PADDING_PX
    if logo:
        logo_y = (height - logo.height) // 2
        canvas.paste(logo, (logo_x, logo_y), logo if logo.mode == "RGBA" else None)
    else:
        draw.rectangle(
            [logo_x, PADDING_PX, logo_x + LOGO_AREA_PX, height - PADDING_PX],
            outline="gray",
            width=1,
        )
        draw.text(
            (logo_x + LOGO_AREA_PX // 2, height // 2),
            "LOGO",
            fill="gray",
            font=load_font(int(4 * MM_TO_PX)),
            anchor="mm",
        )

    text_x = BORDER_PX + PADDING_PX + LOGO_AREA_PX + GAP_PX
    pn_h = text_size(part_font, part_no)[1]
    nm_h = text_size(name_font, part_name)[1]
    total_text_h = pn_h + nm_h + GAP_PX
    text_y = (height - total_text_h) // 2
    draw.text((text_x, text_y), part_no, fill="black", font=part_font)
    draw.text((text_x, text_y + pn_h + GAP_PX), part_name, fill="black", font=name_font)

    qr_data = f"Part No: {part_no}\nPart Name: {part_name}"
    qr_img = make_qr(qr_data, QR_SIZE_PX)
    qr_x = width - BORDER_PX - PADDING_PX - QR_SIZE_PX
    qr_y = (height - QR_SIZE_PX) // 2
    canvas.paste(qr_img, (qr_x, qr_y))

    canvas.save(output_path, dpi=(DPI, DPI))
    return output_path, width, height


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    logo = os.path.join(here, "assets", "logo.png")
    out = os.path.join(here, "output", "sample_label.png")
    path, w, h = generate_label("ADD-0001", "Name of the Part", logo, out)
    print(f"Saved: {path}  ({w}x{h}px)")
