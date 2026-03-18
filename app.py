# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import base64, io, os

app = Flask(__name__)

W, H = 1000, 1500
URL = "spirituellersteckbrief.netlify.app"
BRAND = "DEIN SPIRITUELLER STECKBRIEF"

NAVY = (26, 26, 46)
NAVY_MID = (35, 35, 64)
GOLD = (184, 134, 11)
GOLD_L = (212, 168, 67)
IVORY = (249, 247, 242)
CREAM = (240, 237, 230)
WHITE = (255, 255, 255)
DT = (44, 44, 58)
MU = (107, 107, 123)
WM = (138, 138, 154)
BD = (138, 134, 100)
BL = (160, 157, 140)
DIM = (100, 100, 120)
TEXT_LIGHT = (218, 218, 226)
TEXT_DIM = (170, 170, 185)
CTA_MUTED = (125, 125, 145)

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")

def ff(n, s):
    p = {
        's': os.path.join(FONT_DIR, 'Lora-Regular.ttf'),
        'si': os.path.join(FONT_DIR, 'Lora-Italic.ttf'),
        'l': os.path.join(FONT_DIR, 'Poppins-Light.ttf'),
        'r': os.path.join(FONT_DIR, 'Poppins-Regular.ttf'),
        'b': os.path.join(FONT_DIR, 'Poppins-Bold.ttf'),
        'm': os.path.join(FONT_DIR, 'Poppins-Medium.ttf'),
    }
    return ImageFont.truetype(p[n], s)

def tw(d, t, ft):
    return d.textbbox((0, 0), t, font=ft)[2] - d.textbbox((0, 0), t, font=ft)[0]

def tlh(d, ft):
    return d.textbbox((0, 0), "Ag\u00fc", font=ft)[3] - d.textbbox((0, 0), "Ag\u00fc", font=ft)[1]

def ct(d, t, y, ft, fl):
    d.text(((W - tw(d, t, ft)) // 2, y), t, font=ft, fill=fl)

def wc(d, text, y, ft, fl, mw=820, ls=1.35):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(d, t, ft) <= mw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    lh = tlh(d, ft)
    for line in lines:
        ct(d, line, y, ft, fl)
        y += int(lh * ls)
    return y

def wc_left(d, text, y, ft, fl, x=80, mw=840, ls=1.35):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(d, t, ft) <= mw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    lh = tlh(d, ft)
    for line in lines:
        d.text((x, y), line, font=ft, fill=fl)
        y += int(lh * ls)
    return y

def gl(d, y, w=60):
    d.line([((W - w) // 2, y), ((W + w) // 2, y)], fill=GOLD, width=1)

def gl_left(d, y, x=80, w=80):
    d.line([(x, y), (x + w, y)], fill=GOLD, width=2)

def draw_star(d, x, y, s, c=GOLD_L):
    d.line([(x, y - s), (x, y + s)], fill=c, width=1)
    d.line([(x - s, y), (x + s, y)], fill=c, width=1)
    s2 = int(s * 0.6)
    d.line([(x - s2, y - s2), (x + s2, y + s2)], fill=c, width=1)
    d.line([(x + s2, y - s2), (x - s2, y + s2)], fill=c, width=1)

def draw_stars_scattered(d, offset_y=0):
    stars = [
        (90, 80, 9), (910, 60, 7), (830, 130, 5), (150, 160, 4),
        (60, 500, 4), (940, 480, 5), (920, 700, 3),
        (80, 900, 4), (930, 950, 3), (150, 1100, 3), (870, 1080, 4),
        (500, 80, 3), (700, 170, 3), (850, 1250, 3), (120, 1300, 4)
    ]
    for sx, sy, ss in stars:
        draw_star(d, sx, sy + offset_y, ss)

def draw_bottom_cta(d):
    d.line([(W // 2 - 50, H - 125), (W // 2 + 50, H - 125)], fill=GOLD, width=2)
    draw_star(d, W // 2 - 25, H - 100, 4)
    draw_star(d, W // 2, H - 93, 6)
    draw_star(d, W // 2 + 25, H - 100, 4)
    ct(d, "Entdecke dein Profil", H - 65, ff('m', 26), GOLD)
    ct(d, URL, H - 38, ff('l', 20), CTA_MUTED)

def draw_dots(d, y):
    for i in range(3):
        cx = W // 2 - 30 + i * 30
        d.ellipse([(cx - 3, y - 3), (cx + 3, y + 3)], fill=GOLD)

def star_old(d, y):
    ct(d, "\u2726", y, ff('s', 18), GOLD)

def to_base64(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG', quality=95)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def make_dark_statement(label, hook, body, insight, extra, variant='std'):
    """
    Template A — Dark Statement Pin (Pinterest-optimized v2)
    - Brand "DEIN SPIRITUELLER STECKBRIEF" top
    - Hook headline upper third, 56px Lora (dominant)
    - Short subtitle only (body), 28-30px
    - Scattered star decorations
    - Bigger CTA bottom (26px)
    - insight + extra used only if provided, smaller text
    """
    img = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(img)

    if variant == 'grad':
        for yl in range(H * 2 // 3, H):
            r = (yl - H * 2 // 3) / (H // 3)
            c = tuple(int(NAVY[i] + (NAVY_MID[i] - NAVY[i]) * r) for i in range(3))
            d.line([(0, yl), (W, yl)], fill=c)
    if variant == 'line':
        bl = tuple(int(NAVY[i] + (GOLD[i] - NAVY[i]) * 0.15) for i in range(3))
        d.rectangle([(0, 0), (3, H)], fill=bl)

    draw_stars_scattered(d)

    # Measure content to vertically center
    hook_f = ff('s', 56)
    hook_lines = []
    words = hook.split()
    cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(d, t, hook_f) <= 840:
            cur = t
        else:
            if cur:
                hook_lines.append(cur)
            cur = w
    if cur:
        hook_lines.append(cur)

    hook_h = len(hook_lines) * 72
    body_f = ff('l', 28)
    body_lines = []
    cur = ""
    for w in body.split():
        t = (cur + " " + w).strip()
        if tw(d, t, body_f) <= 840:
            cur = t
        else:
            if cur:
                body_lines.append(cur)
            cur = w
    if cur:
        body_lines.append(cur)
    body_h = len(body_lines) * 42

    # Calculate if insight/extra are provided
    has_insight = insight and len(insight.strip()) > 0
    has_extra = extra and len(extra.strip()) > 0
    insight_h = 0
    extra_h = 0

    if has_insight:
        ins_f = ff('si', 24)
        ins_lines = []
        cur = ""
        for w in insight.split():
            t = (cur + " " + w).strip()
            if tw(d, t, ins_f) <= 780:
                cur = t
            else:
                if cur:
                    ins_lines.append(cur)
                cur = w
        if cur:
            ins_lines.append(cur)
        insight_h = len(ins_lines) * 36

    if has_extra:
        ext_f = ff('l', 22)
        ext_lines = []
        cur = ""
        for w in extra.split():
            t = (cur + " " + w).strip()
            if tw(d, t, ext_f) <= 740:
                cur = t
            else:
                if cur:
                    ext_lines.append(cur)
                cur = w
        if cur:
            ext_lines.append(cur)
        extra_h = len(ext_lines) * 34

    # Total content height
    total = 50 + 40 + 40 + hook_h + 50 + body_h
    if has_insight:
        total += 50 + insight_h
    if has_extra:
        total += 45 + extra_h

    start_y = max(80, (H - total) // 2 - 40)

    y = start_y

    # Brand
    ct(d, BRAND, y, ff('m', 26), GOLD)
    y += 50

    # Gold line
    d.line([(W // 2 - 70, y), (W // 2 + 70, y)], fill=GOLD, width=2)
    y += 40

    # Label
    ct(d, label, y, ff('m', 22), GOLD_L)
    y += 50

    # Hook headline
    for line in hook_lines:
        ct(d, line, y, hook_f, IVORY)
        y += 72
    y += 45

    # Gold divider left
    gl_left(d, y)
    y += 40

    # Body / subtitle
    for line in body_lines:
        d.text((80, y), line, font=body_f, fill=TEXT_LIGHT)
        y += 42

    # Optional: insight block
    if has_insight:
        y += 35
        draw_dots(d, y)
        y += 40
        y = wc(d, insight, y, ff('si', 24), GOLD_L, mw=780, ls=1.5)

    # Optional: extra block
    if has_extra:
        y += 30
        gl_left(d, y, w=40)
        y += 30
        y = wc_left(d, extra, y, ff('l', 22), TEXT_DIM, x=80, mw=740, ls=1.5)

    # Bottom CTA
    draw_bottom_cta(d)

    ct(d, URL, H - 38, ff('l', 20), CTA_MUTED)
    return img


def make_split_card(lab1, big1, desc1, lab2, big2, desc2, connector, variant='std'):
    bg = IVORY if variant != 'dark' else NAVY_MID
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)

    split = 820
    if variant == 'std':
        d.rectangle([(0, 0), (W, split)], fill=NAVY)
        t1c, t1b, t1d = GOLD, WHITE, WM
        t2c, t2b, t2d = GOLD, DT, MU
    elif variant == 'rev':
        d.rectangle([(0, split), (W, H)], fill=NAVY)
        t1c, t1b, t1d = GOLD, DT, MU
        t2c, t2b, t2d = GOLD, WHITE, WM
    else:
        d.rectangle([(0, 0), (W, split)], fill=NAVY)
        d.rectangle([(0, split), (W, H)], fill=NAVY_MID)
        t1c, t1b, t1d = GOLD, WHITE, WM
        t2c, t2b, t2d = GOLD_L, WHITE, WM

    d.line([(0, split), (W, split)], fill=GOLD, width=2)

    # Top half - stars
    draw_star(d, 90, 60, 8)
    draw_star(d, 910, 45, 6)
    draw_star(d, 830, 100, 4)

    y = 70
    ct(d, BRAND, y, ff('m', 22), t1c)
    y += 50
    d.line([(W // 2 - 50, y), (W // 2 + 50, y)], fill=GOLD, width=2)
    y += 40
    ct(d, lab1, y, ff('m', 18), t1c); y += 45
    y = wc(d, big1, y, ff('s', 52), t1b, mw=830, ls=1.3); y += 20
    wc(d, desc1, y, ff('l', 21), t1d, mw=750, ls=1.5)

    y = split + 40
    ct(d, lab2, y, ff('m', 18), t2c); y += 45
    y = wc(d, big2, y, ff('s', 52), t2b, mw=830, ls=1.3); y += 20
    wc(d, desc2, y, ff('l', 21), t2d, mw=750, ls=1.5)

    cy = H - 160
    d.line([(350, cy), (650, cy)], fill=GOLD, width=1)
    fill_conn = DT if variant == 'std' else (WHITE if variant == 'dark' else DT)
    wc(d, connector, cy + 18, ff('si', 22), fill_conn, mw=600, ls=1.4)

    # Bottom CTA
    bfill = BD if variant in ['std', 'dark'] else BL
    ct(d, "Entdecke dein Profil", H - 80, ff('m', 22), GOLD)
    ct(d, URL, H - 50, ff('l', 18), bfill)
    return img


def make_infographic(title, items, cta_line=None):
    img = Image.new('RGB', (W, H), IVORY)
    d = ImageDraw.Draw(img)

    y = 50
    ct(d, BRAND, y, ff('m', 20), GOLD)
    y += 45
    d.line([(W // 2 - 50, y), (W // 2 + 50, y)], fill=GOLD, width=2)
    y += 35
    y = wc(d, title, y, ff('s', 44), DT, mw=830, ls=1.25); y += 12
    gl(d, y, 80); y += 28

    fn, ft, fd = ff('s', 30), ff('m', 19), ff('l', 16)
    sep = (224, 221, 214)

    for sym, ttl, desc in items:
        d.text((75, y - 4), sym, font=fn, fill=GOLD)
        d.text((120, y), ttl, font=ft, fill=DT)
        d.text((120, y + 30), desc, font=fd, fill=MU)
        y += 62
        d.line([(75, y), (925, y)], fill=sep, width=1)
        y += 14

    if cta_line:
        y += 20
        d.rounded_rectangle([(60, y), (940, y + 90)], radius=10, fill=NAVY)
        ct(d, cta_line, y + 18, ff('m', 19), WHITE)
        ct(d, "Personalisiert \u00b7 Auf Deutsch \u00b7 In unter 10 Minuten", y + 52, ff('l', 15), WM)

    ct(d, "Entdecke dein Profil", H - 75, ff('m', 22), GOLD)
    ct(d, URL, H - 45, ff('l', 18), GOLD)
    return img


def make_quote(quote_text, sub_text, extra_text, variant='std'):
    bg = IVORY if variant != 'dark' else NAVY
    qtc = DT if variant != 'dark' else IVORY
    stc = MU if variant != 'dark' else WM
    gc = GOLD if variant != 'dark' else GOLD_L
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)

    if variant == 'dark':
        draw_stars_scattered(d)

    if variant == 'lines':
        d.line([(0, 40), (W, 40)], fill=GOLD, width=1)
        d.line([(0, H - 40), (W, H - 40)], fill=GOLD, width=1)

    y = 120
    ct(d, BRAND, y, ff('m', 22), gc)
    y += 50
    d.line([(W // 2 - 50, y), (W // 2 + 50, y)], fill=GOLD, width=2)
    y += 80

    y = wc(d, quote_text, y, ff('si', 52), qtc, mw=760, ls=1.35); y += 30
    gl(d, y, 50); y += 50
    y = wc(d, sub_text, y, ff('si', 24), stc, mw=680, ls=1.45); y += 20
    wc(d, extra_text, y, ff('l', 20), stc, mw=680, ls=1.5)

    if variant == 'dark':
        draw_star(d, W // 2 - 25, H - 140, 4)
        draw_star(d, W // 2, H - 133, 6)
        draw_star(d, W // 2 + 25, H - 140, 4)

    ct(d, "Entdecke dein Profil", H - 100, ff('m', 22), gc)
    bfill = BL if variant != 'dark' else BD
    ct(d, URL, H - 70, ff('l', 18), bfill)
    return img


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    template = data.get('template', 'A')
    variant = data.get('variant', 'std')

    try:
        if template == 'A':
            img = make_dark_statement(
                label=data['label'],
                hook=data['hook'],
                body=data.get('body', ''),
                insight=data.get('insight', ''),
                extra=data.get('extra', ''),
                variant=variant
            )
        elif template == 'B':
            img = make_split_card(
                lab1=data['lab1'], big1=data['big1'], desc1=data['desc1'],
                lab2=data['lab2'], big2=data['big2'], desc2=data['desc2'],
                connector=data['connector'],
                variant=variant
            )
        elif template == 'C':
            items = [(i['sym'], i['title'], i['desc']) for i in data['items']]
            img = make_infographic(
                title=data['title'],
                items=items,
                cta_line=data.get('cta_line')
            )
        elif template == 'E':
            img = make_quote(
                quote_text=data['quote'],
                sub_text=data['sub'],
                extra_text=data['extra'],
                variant=variant
            )
        else:
            return jsonify({"error": f"Unknown template: {template}"}), 400

        b64 = to_base64(img)
        return jsonify({"image_base64": b64, "width": W, "height": H})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
