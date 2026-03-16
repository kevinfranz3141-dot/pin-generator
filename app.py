# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import base64, io, os

app = Flask(__name__)

W, H = 1000, 1500
URL = "spirituellersteckbrief.netlify.app"

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

def gl(d, y, w=60):
    d.line([((W - w) // 2, y), ((W + w) // 2, y)], fill=GOLD, width=1)

def star(d, y):
    ct(d, "\u2726", y, ff('s', 18), GOLD)

def to_base64(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG', quality=95)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def make_dark_statement(label, hook, body, insight, extra, variant='std'):
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

    y = 80
    star(d, y); y += 50
    ct(d, label, y, ff('b', 16), GOLD); y += 55
    y = wc(d, hook, y, ff('s', 58), WHITE, mw=830, ls=1.3); y += 30
    gl(d, y); y += 35
    y = wc(d, body, y, ff('l', 23), WM, mw=780, ls=1.55); y += 35
    gl(d, y, 40); y += 30
    y = wc(d, insight, y, ff('si', 24), GOLD_L, mw=750, ls=1.5); y += 40
    gl(d, y, 30); y += 28
    wc(d, extra, y, ff('l', 21), DIM, mw=720, ls=1.5)
    ct(d, URL, H - 65, ff('l', 14), BD)
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

    y = 80
    star(d, y); y += 45
    ct(d, lab1, y, ff('b', 16), t1c); y += 50
    ct(d, big1, y, ff('s', 58), t1b); y += 80
    wc(d, desc1, y, ff('l', 21), t1d, mw=750, ls=1.5)
    gl(d, 680, 100)

    y = split + 45
    ct(d, lab2, y, ff('b', 16), t2c); y += 50
    ct(d, big2, y, ff('s', 58), t2b); y += 80
    wc(d, desc2, y, ff('l', 21), t2d, mw=750, ls=1.5)

    cy = H - 160
    d.line([(350, cy), (650, cy)], fill=GOLD, width=1)
    fill_conn = DT if variant == 'std' else (WHITE if variant == 'dark' else DT)
    wc(d, connector, cy + 18, ff('si', 22), fill_conn, mw=600, ls=1.4)

    bfill = BD if variant in ['std', 'dark'] else BL
    ct(d, URL, H - 55, ff('l', 14), bfill)
    return img


def make_infographic(title, items, cta_line=None):
    img = Image.new('RGB', (W, H), IVORY)
    d = ImageDraw.Draw(img)

    y = 60
    y = wc(d, title, y, ff('s', 46), DT, mw=830, ls=1.25); y += 12
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

    ct(d, URL, H - 50, ff('l', 14), GOLD)
    return img


def make_quote(quote_text, sub_text, extra_text, variant='std'):
    bg = IVORY if variant != 'dark' else NAVY
    qtc = DT if variant != 'dark' else IVORY
    stc = MU if variant != 'dark' else WM
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)

    if variant == 'lines':
        d.line([(0, 40), (W, 40)], fill=GOLD, width=1)
        d.line([(0, H - 40), (W, H - 40)], fill=GOLD, width=1)

    star(d, 200)
    y = wc(d, quote_text, 350, ff('si', 54), qtc, mw=760, ls=1.35); y += 30
    gl(d, y, 50); y += 40
    ct(d, "Spiritueller Steckbrief", y, ff('l', 20), stc); y += 50
    gl(d, y, 30); y += 30
    y = wc(d, sub_text, y, ff('si', 24), stc, mw=680, ls=1.45); y += 20
    wc(d, extra_text, y, ff('l', 20), stc, mw=680, ls=1.5)
    star(d, H - 130)
    bfill = BL if variant != 'dark' else BD
    ct(d, URL, H - 75, ff('l', 13), bfill)
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
                body=data['body'],
                insight=data['insight'],
                extra=data['extra'],
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
