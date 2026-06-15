from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "Type_icon"
SIZE = 1254
BG = (250, 250, 248)
STEEL = (185, 190, 198)
STEEL_DARK = (88, 96, 108)
STEEL_LIGHT = (226, 229, 234)
BLUE = (69, 131, 203)
PURPLE = (107, 72, 171)
CONCRETE = (212, 210, 206)
TEXT = (26, 29, 34)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = font(88, bold=True)


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (SIZE, SIZE), BG + (255,))
    draw = ImageDraw.Draw(img)
    return img, draw


def shadow(draw: ImageDraw.ImageDraw, box, blur_offset=(16, 16), radius=32):
    x1, y1, x2, y2 = box
    ox, oy = blur_offset
    draw.rounded_rectangle(
        (x1 + ox, y1 + oy, x2 + ox, y2 + oy),
        radius=radius,
        fill=(220, 220, 220),
    )


def title_bar(draw: ImageDraw.ImageDraw, type_id: str):
    x1, y1, x2, y2 = 240, 1060, 1014, 1178
    draw.rounded_rectangle((x1, y1, x2, y2), radius=42, fill=PURPLE)
    text = f"TYPE-{type_id}"
    bbox = draw.textbbox((0, 0), text, font=TITLE_FONT)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((SIZE - tw) / 2, y1 + (y2 - y1 - th) / 2 - 8), text, fill="white", font=TITLE_FONT)


def cylinder_h(draw: ImageDraw.ImageDraw, x1, y, length, dia, fill=STEEL):
    x2 = x1 + length
    r = dia / 2
    draw.rounded_rectangle((x1, y - r, x2, y + r), radius=int(r), fill=fill, outline=TEXT, width=5)
    draw.ellipse((x1 - r * 0.3, y - r, x1 + r * 0.3, y + r), fill=STEEL_LIGHT, outline=TEXT, width=5)
    draw.ellipse((x2 - r, y - r, x2 + r, y + r), fill=STEEL_LIGHT, outline=TEXT, width=5)
    inner = r * 0.55
    draw.ellipse((x2 - inner, y - inner, x2 + inner, y + inner), outline=STEEL_DARK, width=5)
    draw.line((x1 + 20, y - r * 0.35, x2 - 25, y - r * 0.35), fill=(240, 241, 244), width=8)


def cylinder_v(draw: ImageDraw.ImageDraw, x, y1, length, dia, fill=STEEL):
    y2 = y1 + length
    r = dia / 2
    draw.rounded_rectangle((x - r, y1, x + r, y2), radius=int(r), fill=fill, outline=TEXT, width=5)
    draw.ellipse((x - r, y1 - r * 0.35, x + r, y1 + r * 0.35), fill=STEEL_LIGHT, outline=TEXT, width=5)
    draw.ellipse((x - r, y2 - r * 0.35, x + r, y2 + r * 0.35), fill=fill, outline=TEXT, width=5)
    draw.line((x - r * 0.2, y1 + 20, x - r * 0.2, y2 - 20), fill=(240, 241, 244), width=8)


def plate(draw: ImageDraw.ImageDraw, x, y, w, h, depth=18, fill=(228, 229, 232), holes=0):
    shadow(draw, (x, y, x + w, y + h), blur_offset=(10, 10), radius=8)
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline=TEXT, width=5)
    draw.polygon(
        [(x, y + h), (x + depth, y + h + depth), (x + w + depth, y + h + depth), (x + w, y + h)],
        fill=(175, 176, 180),
        outline=TEXT,
    )
    draw.polygon(
        [(x + w, y), (x + w + depth, y + depth), (x + w + depth, y + h + depth), (x + w, y + h)],
        fill=(197, 198, 202),
        outline=TEXT,
    )
    if holes:
        gap = w / (holes + 1)
        for i in range(holes):
            cx = x + gap * (i + 1)
            draw.ellipse((cx - 10, y + h / 2 - 10, cx + 10, y + h / 2 + 10), fill=(100, 100, 100))


def anchor_bolts(draw: ImageDraw.ImageDraw, x, y, w, spacing=160):
    start = x + (w - spacing) / 2
    for offset in (0, spacing):
        bx = start + offset
        cylinder_v(draw, bx, y - 48, 54, 16, fill=(120, 120, 126))
        draw.rectangle((bx - 24, y - 12, bx + 24, y + 8), fill=(115, 116, 122), outline=TEXT, width=4)


def u_bolt(draw: ImageDraw.ImageDraw, x, y, width, height):
    draw.arc((x, y, x + width, y + height), 180, 360, fill=TEXT, width=8)
    draw.line((x, y + height / 2, x, y + height + 36), fill=TEXT, width=8)
    draw.line((x + width, y + height / 2, x + width, y + height + 36), fill=TEXT, width=8)
    for bx in (x, x + width):
        draw.rectangle((bx - 14, y + height + 14, bx + 14, y + height + 28), fill=(100, 100, 106), outline=TEXT, width=3)


def spring(draw: ImageDraw.ImageDraw, x, y1, y2, radius=36, turns=8):
    span = (y2 - y1) / (turns * 2)
    points = []
    y = y1
    direction = 1
    for _ in range(turns * 2 + 1):
        points.append((x + radius * direction, y))
        y += span
        direction *= -1
    draw.line(points, fill=BLUE, width=12, joint="curve")


def steel_beam(draw: ImageDraw.ImageDraw, x, y, w, h):
    draw.rectangle((x, y, x + w, y + h), fill=(145, 149, 156), outline=TEXT, width=5)
    draw.rectangle((x, y + 20, x + w, y + h - 20), outline=(120, 123, 130), width=4)


def wall(draw: ImageDraw.ImageDraw, x, y1, y2):
    draw.rectangle((x, y1, x + 82, y2), fill=(214, 214, 210), outline=TEXT, width=5)
    for yy in range(y1 + 30, y2, 72):
        draw.line((x + 12, yy, x + 72, yy), fill=(170, 170, 168), width=3)


def concrete(draw: ImageDraw.ImageDraw, x, y, w, h):
    draw.rectangle((x, y, x + w, y + h), fill=CONCRETE, outline=TEXT, width=5)
    for dx in range(28, w, 64):
        for dy in range(18, h, 52):
            draw.ellipse((x + dx, y + dy, x + dx + 9, y + dy + 9), fill=(135, 135, 135))


def stopper(draw: ImageDraw.ImageDraw, x, y, w=24, h=90):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=BLUE, outline=TEXT, width=4)


def gusset(draw: ImageDraw.ImageDraw, pts, fill=(173, 177, 184)):
    draw.polygon(pts, fill=fill, outline=TEXT)


def draw_type_10(draw):
    cylinder_h(draw, 360, 300, 360, 86)
    cylinder_v(draw, 470, 312, 180, 74)
    plate(draw, 355, 520, 250, 28, depth=14, holes=2)
    for bx in (378, 562):
        cylinder_v(draw, bx, 458, 88, 18, fill=(108, 108, 112))
    for bx in (420, 520):
        cylinder_v(draw, bx, 458, 88, 18, fill=(108, 108, 112))
    cylinder_v(draw, 480, 560, 220, 88)
    plate(draw, 385, 720, 210, 30, depth=18, holes=4)
    concrete(draw, 338, 765, 306, 140)
    for bx in (408, 552):
        anchor_bolts(draw, bx - 36, 760, 72, spacing=0)


def draw_type_11(draw):
    cylinder_h(draw, 355, 300, 340, 86)
    cylinder_v(draw, 470, 312, 115, 68)
    draw.rectangle((442, 422, 498, 450), fill=(126, 126, 130), outline=TEXT, width=4)
    cylinder_v(draw, 470, 450, 46, 18, fill=(110, 110, 115))
    spring(draw, 470, 500, 660)
    cylinder_v(draw, 470, 660, 90, 18, fill=(110, 110, 115))
    cylinder_v(draw, 470, 752, 160, 82)
    plate(draw, 380, 920, 190, 28, depth=14)
    concrete(draw, 330, 954, 285, 112)


def draw_type_12(draw):
    cylinder_h(draw, 300, 280, 430, 92)
    cylinder_v(draw, 470, 330, 210, 80)
    gusset(draw, [(430, 330), (520, 330), (470, 430)])
    plate(draw, 410, 228, 120, 24, depth=10)
    plate(draw, 390, 680, 180, 28, depth=14)
    concrete(draw, 336, 720, 290, 150)


def draw_type_13(draw):
    cylinder_h(draw, 295, 280, 440, 92)
    u_bolt(draw, 405, 214, 80, 70)
    cylinder_v(draw, 470, 330, 210, 80)
    gusset(draw, [(430, 330), (520, 330), (470, 430)])
    plate(draw, 390, 680, 180, 28, depth=14)
    concrete(draw, 336, 720, 290, 150)


def draw_type_14(draw):
    cylinder_h(draw, 410, 260, 300, 86)
    plate(draw, 430, 346, 180, 26, depth=12)
    stopper(draw, 612, 298)
    draw.rectangle((470, 374, 530, 690), fill=(164, 170, 178), outline=TEXT, width=5)
    plate(draw, 400, 700, 220, 28, depth=16, holes=4)
    concrete(draw, 350, 740, 330, 150)


def draw_type_15(draw):
    cylinder_h(draw, 410, 260, 300, 86)
    plate(draw, 430, 346, 180, 26, depth=12)
    stopper(draw, 612, 298)
    draw.rectangle((470, 374, 530, 690), fill=(164, 170, 178), outline=TEXT, width=5)
    plate(draw, 400, 700, 220, 28, depth=16)
    steel_beam(draw, 320, 760, 380, 110)


def draw_type_16(draw):
    cylinder_h(draw, 320, 280, 420, 92)
    plate(draw, 692, 236, 26, 102, depth=10)
    cylinder_v(draw, 470, 330, 250, 82)
    plate(draw, 390, 710, 180, 28, depth=14)
    concrete(draw, 336, 748, 290, 140)


def draw_type_19(draw):
    cylinder_h(draw, 250, 260, 420, 88)
    draw.polygon([(420, 355), (470, 355), (625, 690), (575, 690)], fill=(168, 172, 178), outline=TEXT)
    plate(draw, 540, 710, 160, 26, depth=12)
    concrete(draw, 510, 746, 220, 120)
    plate(draw, 420, 360, 74, 20, depth=8)


def draw_type_20(draw):
    cylinder_h(draw, 360, 250, 360, 88)
    u_bolt(draw, 470, 180, 70, 86)
    draw.rectangle((430, 336, 590, 382), fill=(186, 190, 196), outline=TEXT, width=5)
    draw.rounded_rectangle((475, 346, 545, 372), radius=12, fill=BG, outline=BLUE, width=4)
    draw.polygon([(430, 382), (396, 600), (454, 600), (488, 382)], fill=(166, 171, 177), outline=TEXT)
    plate(draw, 360, 615, 180, 24, depth=14)
    concrete(draw, 326, 650, 250, 135)


def draw_type_21(draw):
    wall(draw, 205, 260, 840)
    draw.polygon([(285, 460), (520, 460), (520, 520), (340, 520)], fill=(170, 174, 180), outline=TEXT)
    cylinder_h(draw, 395, 390, 270, 82)
    u_bolt(draw, 465, 328, 74, 74)


def draw_type_22(draw):
    cylinder_h(draw, 380, 270, 280, 82)
    u_bolt(draw, 455, 210, 74, 74)
    draw.polygon([(340, 470), (520, 470), (520, 525), (394, 525)], fill=(170, 174, 180), outline=TEXT)
    draw.rectangle((372, 525, 430, 780), fill=(166, 171, 177), outline=TEXT, width=5)
    plate(draw, 310, 790, 190, 28, depth=14)
    concrete(draw, 270, 824, 265, 126)


def draw_type_23(draw):
    steel_beam(draw, 320, 170, 450, 92)
    draw.rectangle((520, 262, 578, 570), fill=(166, 171, 177), outline=TEXT, width=5)
    draw.polygon([(420, 520), (600, 520), (600, 578), (462, 578)], fill=(170, 174, 180), outline=TEXT)
    cylinder_h(draw, 440, 446, 255, 78)


def draw_type_24(draw):
    wall(draw, 230, 180, 860)
    draw.polygon([(314, 320), (372, 320), (372, 700), (330, 700), (330, 378), (470, 378), (470, 320), (314, 320)], fill=(168, 172, 178), outline=TEXT)
    cylinder_h(draw, 420, 300, 255, 78)
    u_bolt(draw, 458, 238, 72, 74)


def draw_type_25(draw):
    wall(draw, 230, 220, 820)
    draw.polygon([(312, 620), (372, 620), (372, 380), (620, 380), (620, 320), (312, 320)], fill=(168, 172, 178), outline=TEXT)
    cylinder_h(draw, 440, 254, 245, 78)


def draw_type_26(draw):
    wall(draw, 180, 240, 860)
    draw.polygon([(262, 620), (322, 620), (322, 410), (560, 410), (560, 350), (262, 350)], fill=(168, 172, 178), outline=TEXT)
    draw.polygon([(262, 500), (322, 500), (322, 760), (262, 760)], fill=(168, 172, 178), outline=TEXT)
    cylinder_h(draw, 420, 284, 250, 78)


def draw_type_27(draw):
    cylinder_h(draw, 360, 260, 330, 88)
    draw.polygon([(450, 348), (600, 348), (600, 404), (450, 404)], fill=(170, 174, 180), outline=TEXT)
    draw.rectangle((490, 404, 548, 740), fill=(166, 171, 177), outline=TEXT, width=5)
    plate(draw, 418, 750, 210, 30, depth=16)
    concrete(draw, 370, 786, 300, 134)


def draw_type_28(draw):
    cylinder_h(draw, 365, 310, 320, 86)
    draw.polygon([(330, 380), (390, 380), (390, 770), (330, 770)], fill=(168, 172, 178), outline=TEXT)
    draw.polygon([(660, 380), (720, 380), (720, 770), (660, 770)], fill=(168, 172, 178), outline=TEXT)
    draw.polygon([(330, 380), (720, 380), (720, 438), (330, 438)], fill=(168, 172, 178), outline=TEXT)
    plate(draw, 286, 780, 180, 28, depth=14)
    plate(draw, 622, 780, 180, 28, depth=14)
    concrete(draw, 250, 814, 584, 136)


def draw_type_30(draw):
    wall(draw, 210, 220, 850)
    steel_beam(draw, 700, 240, 200, 120)
    draw.polygon([(292, 610), (352, 610), (770, 360), (710, 360)], fill=(166, 171, 177), outline=TEXT)
    cylinder_h(draw, 520, 275, 220, 76)


def draw_type_32(draw):
    steel_beam(draw, 300, 180, 430, 92)
    draw.polygon([(372, 272), (432, 272), (432, 740), (372, 740)], fill=(168, 172, 178), outline=TEXT)
    draw.polygon([(598, 272), (658, 272), (658, 740), (598, 740)], fill=(168, 172, 178), outline=TEXT)
    draw.polygon([(372, 682), (658, 682), (658, 740), (372, 740)], fill=(168, 172, 178), outline=TEXT)
    cylinder_h(draw, 420, 598, 210, 78)


def draw_type_33(draw):
    wall(draw, 215, 220, 860)
    draw.polygon([(302, 640), (360, 640), (360, 760), (302, 760)], fill=(168, 172, 178), outline=TEXT)
    draw.polygon([(302, 640), (610, 640), (610, 698), (302, 698)], fill=(168, 172, 178), outline=TEXT)
    draw.polygon([(552, 330), (610, 330), (610, 698), (552, 698)], fill=(168, 172, 178), outline=TEXT)
    cylinder_h(draw, 372, 566, 230, 78)


def draw_type_34(draw):
    wall(draw, 215, 220, 860)
    draw.polygon([(552, 330), (610, 330), (610, 698), (552, 698)], fill=(168, 172, 178), outline=TEXT)
    draw.polygon([(302, 330), (610, 330), (610, 388), (302, 388)], fill=(168, 172, 178), outline=TEXT)
    cylinder_h(draw, 360, 254, 230, 78)


def draw_type_35(draw):
    wall(draw, 220, 210, 850)
    draw.polygon([(302, 420), (700, 420), (700, 478), (302, 478)], fill=(168, 172, 178), outline=TEXT)
    draw.polygon([(302, 570), (700, 570), (700, 628), (302, 628)], fill=(168, 172, 178), outline=TEXT)


def draw_type_57(draw):
    steel_beam(draw, 270, 540, 540, 132)
    cylinder_h(draw, 390, 430, 260, 88)
    u_bolt(draw, 465, 360, 80, 88)
    draw.line((505, 450, 505, 540), fill=TEXT, width=6)


def _rgba(rgb, alpha=255):
    return (rgb[0], rgb[1], rgb[2], alpha)


def _clamp(value: float) -> int:
    return max(0, min(255, int(round(value))))


def _steel_tone(t: float, bias: float = 0.0) -> tuple[int, int, int, int]:
    base = 168 + 28 * math.cos((t - 0.48) * math.pi * 2)
    highlight = 54 * math.exp(-((t - 0.30) / 0.10) ** 2)
    shadow = -34 * math.exp(-((t - 0.78) / 0.15) ** 2)
    v = _clamp(base + highlight + shadow + bias)
    return (_clamp(v + 4), _clamp(v + 7), _clamp(v + 12), 255)


def _hex_points(cx: float, cy: float, r: float) -> list[tuple[float, float]]:
    pts = []
    for angle in (0, 60, 120, 180, 240, 300):
        rad = math.radians(angle)
        pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
    return pts


def _paste(img: Image.Image, sprite: Image.Image, x: int, y: int):
    img.alpha_composite(sprite, (int(x), int(y)))


def make_pipe_sprite(length: int, dia: int, angle: float = 0, open_right: bool = True) -> Image.Image:
    width = length + dia * 2 + 80
    height = dia + 80
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    x1 = 40 + dia // 2
    y1 = 40
    x2 = x1 + length
    y2 = y1 + dia
    radius = dia // 2

    for i in range(dia):
        color = _steel_tone(i / max(dia - 1, 1))
        draw.rounded_rectangle((x1, y1 + i, x2, y1 + i + 1), radius=radius, fill=color)

    draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, outline=_rgba(TEXT), width=4)
    draw.line((x1 + 24, y1 + dia * 0.26, x2 - 26, y1 + dia * 0.26), fill=(255, 255, 255, 165), width=max(6, dia // 12))
    draw.line((x1 + 24, y1 + dia * 0.60, x2 - 26, y1 + dia * 0.60), fill=(125, 132, 142, 110), width=max(4, dia // 16))

    draw.ellipse((x1 - dia * 0.42, y1, x1 + dia * 0.14, y2), fill=(230, 232, 236, 255), outline=_rgba(TEXT), width=4)
    if open_right:
        outer = (x2 - dia * 0.12, y1, x2 + dia * 0.88, y2)
        draw.ellipse(outer, fill=(226, 229, 233, 255), outline=_rgba(TEXT), width=4)
        pad = dia * 0.22
        inner = (outer[0] + pad, outer[1] + pad, outer[2] - pad * 0.85, outer[3] - pad)
        draw.ellipse(inner, fill=(69, 80, 94, 255), outline=(168, 173, 180, 255), width=4)
    else:
        draw.ellipse((x2 - dia * 0.15, y1, x2 + dia * 0.45, y2), fill=(216, 220, 225, 255), outline=_rgba(TEXT), width=4)

    if angle:
        img = img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    return img


def draw_threaded_rod(draw: ImageDraw.ImageDraw, cx: int, y1: int, y2: int, width: int, fill=(118, 123, 131)):
    draw.rectangle((cx - width // 2, y1, cx + width // 2, y2), fill=fill, outline=TEXT, width=3)
    step = max(8, width // 2)
    for yy in range(y1 + 4, y2, step):
        draw.line((cx - width // 2 + 2, yy, cx + width // 2 - 2, yy), fill=(220, 222, 226), width=2)


def draw_hex_nut(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, hole_r: int = 0):
    pts = _hex_points(cx, cy, radius)
    draw.polygon(pts, fill=(188, 191, 198), outline=TEXT)
    inner = _hex_points(cx, cy - 2, radius * 0.65)
    draw.polygon(inner, fill=(229, 231, 235), outline=(120, 126, 134))
    if hole_r:
        draw.ellipse((cx - hole_r, cy - hole_r, cx + hole_r, cy + hole_r), fill=(96, 101, 110), outline=(150, 156, 164))


def draw_washer(draw: ImageDraw.ImageDraw, cx: int, cy: int, outer_r: int, inner_r: int):
    draw.ellipse((cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r), fill=(224, 226, 230), outline=TEXT, width=3)
    draw.ellipse((cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r), fill=BG, outline=(145, 151, 160), width=3)


def draw_corner_bolt(draw: ImageDraw.ImageDraw, cx: int, top_y: int, upper_bottom: int, lower_top: int, lower_bottom: int, sleeve: bool = True):
    draw_threaded_rod(draw, cx, top_y, lower_bottom + 34, 14)
    draw_hex_nut(draw, cx, top_y + 26, 24, hole_r=8)
    draw_washer(draw, cx, top_y + 52, 23, 10)
    if sleeve:
        cylinder_v(draw, cx, upper_bottom + 8, max(24, lower_top - upper_bottom - 16), 24, fill=BLUE)
        draw_washer(draw, cx, upper_bottom + 12, 21, 9)
        draw_washer(draw, cx, lower_top - 10, 21, 9)
    draw_washer(draw, cx, lower_bottom + 10, 20, 9)
    draw_hex_nut(draw, cx, lower_bottom + 34, 20, hole_r=7)


def draw_anchor_bolt(draw: ImageDraw.ImageDraw, cx: int, plate_y: int):
    draw_threaded_rod(draw, cx, plate_y - 14, plate_y + 44, 14, fill=(124, 128, 136))
    draw_washer(draw, cx, plate_y + 8, 18, 8)
    draw_hex_nut(draw, cx, plate_y - 12, 20, hole_r=7)
    draw_hex_nut(draw, cx, plate_y + 28, 18, hole_r=7)


def draw_support_stack(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, concrete_h: int = 150, steel_base: bool = False):
    plate(draw, x, y, w, h, depth=18)
    bolt_centers = (x + 42, x + w - 42, x + 92, x + w - 92)
    if steel_base:
        steel_beam(draw, x - 40, y + 42, w + 120, 118)
    else:
        concrete(draw, x - 50, y + 40, w + 100, concrete_h)
    for cx in bolt_centers:
        draw_anchor_bolt(draw, cx, y)


def draw_type_10_detailed(img: Image.Image, draw: ImageDraw.ImageDraw):
    _paste(img, make_pipe_sprite(690, 116, angle=-8), 118, 88)
    cylinder_v(draw, 590, 314, 122, 70)
    draw_washer(draw, 590, 444, 62, 30)
    plate(draw, 362, 458, 338, 30, depth=16)
    plate(draw, 340, 538, 360, 28, depth=16)
    for cx in (390, 470, 610, 690):
        draw_corner_bolt(draw, cx, 382, 488, 538, 566, sleeve=True)
    draw_hex_nut(draw, 590, 518, 22, hole_r=8)
    cylinder_v(draw, 590, 568, 244, 84)
    draw_washer(draw, 590, 820, 56, 24)
    draw_support_stack(draw, 420, 832, 220, 28, concrete_h=150, steel_base=False)


def draw_type_11_detailed(img: Image.Image, draw: ImageDraw.ImageDraw):
    _paste(img, make_pipe_sprite(670, 110, angle=-8), 132, 92)
    cylinder_v(draw, 586, 316, 90, 64)
    draw_washer(draw, 586, 414, 54, 24)
    draw_hex_nut(draw, 586, 450, 22, hole_r=8)
    draw_threaded_rod(draw, 586, 448, 710, 18)
    draw_washer(draw, 586, 486, 44, 18)
    spring(draw, 586, 506, 640, radius=46, turns=8)
    draw_washer(draw, 586, 660, 44, 18)
    draw_hex_nut(draw, 586, 694, 22, hole_r=8)
    cylinder_v(draw, 586, 700, 172, 84)
    draw_washer(draw, 586, 880, 56, 24)
    draw_support_stack(draw, 420, 892, 220, 28, concrete_h=132, steel_base=False)


def draw_type_12_detailed(img: Image.Image, draw: ImageDraw.ImageDraw):
    _paste(img, make_pipe_sprite(690, 114, angle=-7), 118, 92)
    plate(draw, 520, 346, 134, 26, depth=12)
    cylinder_v(draw, 588, 372, 250, 84)
    gusset(draw, [(536, 384), (582, 384), (558, 476)], fill=(191, 194, 200))
    gusset(draw, [(594, 384), (640, 384), (620, 476)], fill=(177, 181, 188))
    draw.line((550, 386, 566, 444), fill=TEXT, width=4)
    draw.line((625, 386, 616, 444), fill=TEXT, width=4)
    draw_washer(draw, 588, 628, 58, 26)
    draw_support_stack(draw, 420, 640, 220, 28, concrete_h=145, steel_base=False)


def draw_type_13_detailed(img: Image.Image, draw: ImageDraw.ImageDraw):
    _paste(img, make_pipe_sprite(690, 114, angle=-7), 118, 92)
    draw.arc((500, 240, 676, 366), 192, 348, fill=TEXT, width=8)
    draw.line((526, 306, 526, 408), fill=TEXT, width=8)
    draw.line((648, 290, 648, 406), fill=TEXT, width=8)
    draw_hex_nut(draw, 526, 430, 18, hole_r=6)
    draw_hex_nut(draw, 648, 428, 18, hole_r=6)
    plate(draw, 516, 396, 148, 26, depth=12)
    cylinder_v(draw, 590, 420, 232, 84)
    gusset(draw, [(542, 430), (586, 430), (562, 516)], fill=(190, 194, 200))
    gusset(draw, [(596, 430), (640, 430), (618, 516)], fill=(176, 180, 186))
    draw_support_stack(draw, 420, 664, 220, 28, concrete_h=145, steel_base=False)


def draw_type_14_detailed(img: Image.Image, draw: ImageDraw.ImageDraw):
    _paste(img, make_pipe_sprite(520, 102, angle=-5), 196, 122)
    plate(draw, 480, 364, 224, 28, depth=14)
    stopper(draw, 690, 314, w=26, h=94)
    draw.rectangle((544, 392, 614, 722), fill=(163, 169, 177), outline=TEXT, width=5)
    draw.rectangle((560, 408, 598, 704), fill=(229, 232, 236), outline=(108, 114, 122), width=3)
    plate(draw, 458, 732, 242, 30, depth=16)
    draw_support_stack(draw, 458, 732, 242, 30, concrete_h=158, steel_base=False)


def draw_type_15_detailed(img: Image.Image, draw: ImageDraw.ImageDraw):
    _paste(img, make_pipe_sprite(520, 102, angle=-5), 196, 122)
    plate(draw, 480, 364, 224, 28, depth=14)
    stopper(draw, 690, 314, w=26, h=94)
    draw.rectangle((544, 392, 614, 722), fill=(163, 169, 177), outline=TEXT, width=5)
    draw.rectangle((560, 408, 598, 704), fill=(229, 232, 236), outline=(108, 114, 122), width=3)
    plate(draw, 458, 732, 242, 30, depth=16)
    steel_beam(draw, 372, 790, 420, 122)


DETAILED_DRAWERS = {
    "10": draw_type_10_detailed,
    "11": draw_type_11_detailed,
    "12": draw_type_12_detailed,
    "13": draw_type_13_detailed,
    "14": draw_type_14_detailed,
    "15": draw_type_15_detailed,
}


DRAWERS = {
    "10": draw_type_10,
    "11": draw_type_11,
    "12": draw_type_12,
    "13": draw_type_13,
    "14": draw_type_14,
    "15": draw_type_15,
    "16": draw_type_16,
    "19": draw_type_19,
    "20": draw_type_20,
    "21": draw_type_21,
    "22": draw_type_22,
    "23": draw_type_23,
    "24": draw_type_24,
    "25": draw_type_25,
    "26": draw_type_26,
    "27": draw_type_27,
    "28": draw_type_28,
    "30": draw_type_30,
    "32": draw_type_32,
    "33": draw_type_33,
    "34": draw_type_34,
    "35": draw_type_35,
    "57": draw_type_57,
}


def render(type_id: str):
    img, draw = canvas()
    if type_id in DETAILED_DRAWERS:
        DETAILED_DRAWERS[type_id](img, draw)
    else:
        DRAWERS[type_id](draw)
    title_bar(draw, type_id)
    img.convert("RGB").save(OUT_DIR / f"{type_id}.png")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for type_id in DRAWERS:
        render(type_id)
    print("generated:", ", ".join(sorted(DRAWERS)))
    print("skipped: 85")


if __name__ == "__main__":
    main()
