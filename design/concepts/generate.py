"""Generate discussion drawings, never production CAD. Python standard library only."""

import argparse
import json
import math
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PITCH = 19.05
WIDTH, DEPTH, ANGLE = 320.8, 117.25, 7.0
# Pad dimensions are visual placeholders, not selected production parts.
FOOT_RADIUS, FOOT_HEIGHT = 5.5, 2.0
FOOT_CENTERS = ((22.0, 13.0), (WIDTH - 22, 13.0), (22.0, DEPTH - 13), (WIDTH - 22, DEPTH - 13))
ROWS = [
    ["Esc", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", ("Back", 2)],
    [("Tab", 1.5), "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", ("\\", 1.5), "PgUp"],
    [("Caps", 1.75), "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", ("Enter", 2.25), "PgDn"],
    [("Shift", 2.25), "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", ("Shift", 1.75), "↑", "End"],
    [("Ctrl", 1.25), ("Win", 1.25), ("Alt", 1.25), ("Space", 6.25), "Alt", "Fn", "Ctrl", "←", "↓", "→"],
]


def text(x, y, value, size: float = 18, fill="#48373f", anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{escape(value)}</text>'


def rect(x, y, width, height, fill, radius: float = 0, extra=""):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" {extra}/>'


def line(x1, y1, x2, y2, color="#8b8e85", extra=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" {extra}/>'


def layout():
    keys = []
    for row, entries in enumerate(ROWS):
        position = 0.0
        for entry in entries:
            label, width = entry if isinstance(entry, tuple) else (entry, 1)
            keys.append({"row": row, "label": label, "width": width, "x": 8 + position * PITCH, "y": 11 + row * PITCH})
            position += width
        assert position == (15 if row == 0 else 16)
    assert len(keys) == 67
    assert [sum(key["row"] == row for key in keys) for row in range(5)] == [14, 15, 14, 14, 10]
    for key in keys:
        assert 0 <= key["x"] < key["x"] + key["width"] * PITCH <= WIDTH
        assert 0 <= key["y"] < key["y"] + PITCH <= DEPTH
    return keys


def sheet(title, subtitle, body, height=720):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="{height}" viewBox="0 0 1280 {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}。外观概念图，不可用于加工，尺寸与结构尚未验证。</desc>
<defs>
  <linearGradient id="ivory" x2="0.3" y2="1"><stop stop-color="#fffdfd"/><stop offset="1" stop-color="#ddd8dc"/></linearGradient>
  <linearGradient id="silver" x2="0.9" y2="0.8"><stop stop-color="#b6bbc4"/><stop offset="0.32" stop-color="#f3f4f6"/><stop offset="0.55" stop-color="#d4d8df"/><stop offset="1" stop-color="#969da8"/></linearGradient>
  <linearGradient id="red" x2="0.9" y2="1"><stop stop-color="#ef555c"/><stop offset="1" stop-color="#8e202b"/></linearGradient>
  <radialGradient id="clear-foot" cx=".3" cy=".25" r=".8"><stop stop-color="#ffffff" stop-opacity=".72"/><stop offset=".5" stop-color="#e9eff5" stop-opacity=".10"/><stop offset=".8" stop-color="#c9d2df" stop-opacity=".08"/><stop offset="1" stop-color="#9daabd" stop-opacity=".28"/></radialGradient>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#c0afb8" stroke-opacity="0.12"/></pattern>
  <pattern id="brush" width="3" height="1" patternUnits="userSpaceOnUse"><path d="M0 .5H3" stroke="#ffffff" stroke-opacity="0.12" stroke-width=".12"/></pattern>
  <filter id="shadow" x="-20%" y="-30%" width="140%" height="170%"><feDropShadow dx="0" dy="7" stdDeviation="7" flood-color="#69434e" flood-opacity=".17"/></filter>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation=".9"/></filter>
  <marker id="arrow" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto-start-reverse"><path d="M7 0L0 3.5L7 7" fill="none" stroke="#929588" stroke-width="1"/></marker>
</defs>
<style>text{{font-family:'Avenir Next','PingFang SC','Microsoft YaHei',sans-serif}} .mono{{font-family:'Menlo',monospace}} .leader{{fill:none;stroke:#929588;stroke-width:1.3}} .dim{{stroke:#929588;stroke-width:1;marker-start:url(#arrow);marker-end:url(#arrow)}}</style>
{rect(0, 0, 1280, height, '#f5f2f3')}{rect(0, 0, 1280, height, 'url(#grid)')}
{rect(56, 42, 4, 40, '#be3446', 2)}
{text(76, 58, title, 24)}{text(76, 88, subtitle, 15, '#7d6a74')}
{body}
{line(76, height - 57, 1204, height - 57, '#d9cbd2')}
{text(76, height - 31, 'DARLING65 / CONCEPT 01', 12, '#7d6a74', extra='class="mono"')}
{text(1204, height - 31, '仅用于外观讨论 · 非加工图 · 非性能验证', 13, '#7d6a74', 'end')}
</svg>\n'''


KANA = {
    'Q': 'た', 'W': 'て', 'E': 'い', 'R': 'す', 'T': 'か', 'Y': 'ん', 'U': 'な', 'I': 'に', 'O': 'ら', 'P': 'せ',
    'A': 'ち', 'S': 'と', 'D': 'し', 'F': 'は', 'G': 'き', 'H': 'く', 'J': 'ま', 'K': 'の', 'L': 'り',
    'Z': 'つ', 'X': 'さ', 'C': 'そ', 'V': 'ひ', 'B': 'こ', 'N': 'み', 'M': 'も',
    '1': 'ぬ', '2': 'ふ', '3': 'あ', '4': 'う', '5': 'え', '6': 'お', '7': 'や', '8': 'ゆ', '9': 'よ', '0': 'わ',
}
SHIFTED = {'1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')', '-': '_', '=': '+', '[': '{', ']': '}', ';': ':', "'": '"', ',': '<', '.': '>', '/': '?', '\\': '|'}
ARROWS = {'↑': 0, '←': -90, '↓': 180, '→': 90}


def keycap_headpiece(mark, paths, center_x, center_y, width, color):
    x0, y0, x1, y1 = mark['bounds']
    scale = width / (x1 - x0)
    tx, ty = center_x - scale * (x0 + x1) / 2, center_y - scale * (y0 + y1) / 2
    return f'<g class="keycap-headpiece" transform="matrix({scale} 0 0 {scale} {tx} {ty})" fill="none" stroke="{color}" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round">{paths}</g>'


def keycap_art(key, mark, paths, identifier):
    label = key['label']
    w = key['width'] * PITCH - 1.6
    accent = label in ('Esc', 'Enter', 'Fn') or label in ARROWS

    modifier = label in ('Tab', 'Caps', 'Shift', 'Back', 'PgUp', 'PgDn', 'End', '\\')
    color = 'url(#red)' if accent else ('#e8cbd3' if modifier or label == 'Space' else '#f5f1ef')
    ink = '#fff7ef' if accent else '#862e46'
    novelty = {'Esc': 'code-002', 'Enter': 'dwg-headpiece', 'Space': 'partner-code', 'Fn': 'partner-link'}.get(label, '')
    art = []
    if label == 'Esc':
        art.extend([text(2.2, 3.2, 'CODE', 1.4, ink, extra='class="mono"'), text(w / 2, 10.7, '002', 6.6, ink, 'middle', 'class="mono"'), text(w / 2, 14, 'ESC', 1.4, ink, 'middle')])
    elif label == 'Enter':
        art.extend(['<path d="M10.5 5.7V9H4M4 9L6.2 6.8M4 9L6.2 11.2" fill="none" stroke="'+ink+'" stroke-width=".55" stroke-linejoin="round"/>', text(2.7, 13.4, 'ENTER', 1.35, ink), keycap_headpiece(mark, paths, w * .65, 8.1, 23.5, ink)])
    elif label == 'Space':
        art.extend([rect(3, 2.8, 19, 10, '#ac3047', 1.2), text(12.5, 10.1, '002', 5.2, '#fff7ef', 'middle', 'class="mono"'), rect(w - 22, 2.8, 19, 10, 'none', 1.2, 'stroke="#9d405b" stroke-width=".4"'), text(w - 12.5, 10.1, '016', 5.2, '#9d405b', 'middle', 'class="mono"'), line(25, 7.8, w / 2 - 16, 7.8, '#b86d7e', 'stroke-width=".4"'), line(w / 2 + 16, 7.8, w - 25, 7.8, '#87b9af', 'stroke-width=".4"'), text(w / 2, 8.2, 'ダーリン', 4.5, ink, 'middle', 'font-family="Hiragino Sans,PingFang SC,sans-serif"'), text(w / 2, 12.5, 'DARLING IN THE FRANXX', 1.7, '#9d405b', 'middle', 'letter-spacing=".16"')])
    elif label == 'Fn':
        for cx in (w / 2 - 2, w / 2 + 2):
            art.append(f'<circle cx="{cx}" cy="6.8" r="3.1" fill="none" stroke="{ink}" stroke-width=".55"/>')
        art.append(text(w / 2, 13.5, 'FN', 1.8, ink, 'middle'))
    elif label in ARROWS:
        cx, cy = w / 2, 7.1
        art.append(f'<g transform="rotate({ARROWS[label]} {cx} {cy})"><path d="M{cx - 3.5} {cy + .6}L{cx} {cy - 3}L{cx + 3.5} {cy + .6}M{cx} {cy - 2.6}V{cy + 3.8}" fill="none" stroke="{ink}" stroke-width=".7" stroke-linejoin="miter"/>' + line(cx - 2.4, cy + 5.2, cx + 2.4, cy + 5.2, '#8dbab0', 'stroke-width=".5"') + '</g>')
    elif label == 'Shift':
        pilot = '016 / STAMEN' if key['x'] < PITCH else '002 / PISTIL'
        art.extend([text(3, 7.1, 'SHIFT', 3, ink), text(3, 12.6, pilot, 1.35, ink, extra='class="mono"')])
        for offset in (0, 2.7):
            art.append(line(w - 11 + offset, 5, w - 7 + offset, 11, ink, 'stroke-width=".8"'))
    elif label == 'Caps':
        art.extend([text(3, 6.7, 'CAPS', 2.8, ink), text(3, 12.2, 'LOCK', 1.5, ink), f'<circle cx="{w - 5}" cy="7.3" r="1.4" fill="none" stroke="{ink}" stroke-width=".45"/>'])
    elif label == 'Back':
        art.extend([text(3, 8.5, 'BACKSPACE', 2.2, ink), '<path d="M'+str(w-5)+' 5L'+str(w-9)+' 8.5L'+str(w-5)+' 12" fill="none" stroke="'+ink+'" stroke-width=".6"/>'])
    elif label in KANA:
        art.append(text(2.8, 8.8 if label.isdigit() else 6.8, label, 4.1 if label.isdigit() else 3.9, ink, extra='font-weight="500"'))
        art.append(text(w - 2.5, 12.9, KANA[label], 2.8, '#9a5a70', 'end', 'font-family="Hiragino Sans,PingFang SC,sans-serif"'))
        if label in SHIFTED:
            art.append(text(w - 2.6, 4.5, SHIFTED[label], 2, ink, 'end'))
        if label in ('F', 'J'):
            art.append(line(3, 12.9, 6.6, 12.9, '#6a9c91', 'stroke-width=".65" stroke-linecap="round"'))
    elif label in SHIFTED:
        art.extend([text(3, 10.5, label, 3.8, ink), text(w - 3, 5.7, SHIFTED[label], 2.6, ink, 'end')])
    else:
        art.append(text(w / 2, 9.4, label, 2.7, ink, 'middle'))
        if label in ('PgUp', 'PgDn', 'End'):
            art.append(line(w / 2 - 3, 12, w / 2 + 3, 12, '#a1556b', 'stroke-width=".4"'))
    return f'<g class="key" id="{escape(identifier, quote=True)}" data-row="{key["row"]}" data-width-u="{key["width"]}" data-label="{escape(label, quote=True)}" data-novelty="{novelty}">' + rect(.55, .55, w + .5, 17.9, '#fff4f7', 1.5, 'opacity=".5" filter="url(#glow)"') + rect(.8, .8, w, 17.45, '#c4b7be', 1.35) + rect(.8, .8, w, 15.7, color, 1.35, 'stroke="#fff5e5" stroke-opacity=".2" stroke-width=".2"') + '<g class="key-art" transform="translate(.8 .8)">' + ''.join(art) + '</g></g>'


def keycaps_view(keys, mark, paths):
    by_label = {key['label']: key for key in keys}
    cards = [('Esc', 76, '编号键 / CODE 002', '大编号与功能微字分层'), ('Enter', 300, '头饰图案键 / ENTER', '沿用用户 DWG 的真实轮廓'), ('F', 730, '字母区 / LATIN + KANA', '主字清楚，假名作为视觉副标'), ('Fn', 1035, '配对符号 / FN', '双环图案与空格配对编号呼应')]
    body = []
    for label, x, title, caption in cards:
        body.extend([f'<g transform="translate({x} 144) scale(7)">' + keycap_art(by_label[label], mark, paths, f'detail-{label}') + '</g>', text(x, 315, title, 15), text(x, 341, caption, 13, '#7d6a74')])
    body.extend(['<g transform="translate(160 403) scale(8)">' + keycap_art(by_label['Space'], mark, paths, 'detail-Space') + '</g>', text(160, 587, '主题空格 / 002 × 016', 19, '#a82d43'), text(160, 615, '浅粉底、深红字、搭档编号与少量青绿连接线；不改变空格功能。', 14, '#7d6a74')])
    palette = [(76, '#f5f1ef', '珍珠白 / 字母区'), (300, '#e8cbd3', '浅粉 / 修饰区'), (524, '#ac3047', '深红 / 图案键'), (748, '#c5cad2', '雾银 / 配重'), (972, '#87b9af', '青绿 / 少量点缀')]
    for x, color, label in palette:
        body.extend([rect(x, 662, 20, 20, color, 3, 'stroke="#303a2c22"'), text(x + 31, 677, label, 13, '#7d6a74')])
    body.extend([text(76, 735, '键帽高度、材质与印刷/透字工艺待定；假名仅为视觉副标，不改变 ANSI 输入映射。', 14, '#7d6a74'), text(76, 758, '参考 Hatoworks Ramune 的分区与图案键方法；不使用其瓶子图标、图片或品牌标识。', 14, '#7d6a74')])
    return sheet('01B / 主题键帽细节', '独立图案键 / 拉丁字母与假名副标 / 002 与 016 搭档编号 / 非联名设计', ''.join(body), 840)


def top_view(keys, mark, paths):
    body = [rect(0, 0, WIDTH, DEPTH, 'url(#ivory)', 5.5, 'stroke="#c7cabc" stroke-width=".55" filter="url(#shadow)"'),
            rect(1.4, 1.4, WIDTH - 2.8, DEPTH - 2.8, 'none', 4.2, 'stroke="#fffdfd" stroke-width=".7"'),
            rect(6.3, 9.2, 308.2, 98.85, '#d9cfd3', 2.2)]
    for index, key in enumerate(keys, 1):
        body.append(f'<g transform="translate({key["x"]} {key["y"]})">' + keycap_art(key, mark, paths, f"key-{index}") + "</g>")
    cx, cy = 8 + 15.5 * PITCH, 11 + .5 * PITCH
    body.extend(['<g id="encoder" data-control="rotary-encoder">', f'<circle cx="{cx}" cy="{cy}" r="8.2" fill="#c1a0ac"/>', f'<circle cx="{cx}" cy="{cy}" r="7.6" fill="url(#red)" stroke="#f28080" stroke-width=".25"/>'])
    for step in range(32):
        angle = step * math.tau / 32
        body.append(line(cx + math.cos(angle) * 6.7, cy + math.sin(angle) * 6.7, cx + math.cos(angle) * 7.25, cy + math.sin(angle) * 7.25, '#ffb0a0', 'stroke-width=".18" opacity=".75"'))
    body.extend([f'<circle cx="{cx}" cy="{cy}" r="5.8" fill="#b32c3e"/>', line(cx, cy - 4.8, cx, cy - 2.7, '#ffdec6', 'stroke-width=".7" stroke-linecap="round"'), '</g>', rect(8, 109.8, 304.8, .7, '#b13040', .35), text(10, 114.7, 'DARLING65', 2.5, '#7b8175'), text(310, 114.7, '002', 2.5, '#ac3444', 'end')])
    illustration = '<g transform="translate(159 174) scale(3)">' + ''.join(body) + '</g>'
    annotations = line(159, 150, 1121.4, 150, extra='class="dim"') + text(640, 136, '概念外廓约 321 mm', 15, '#737b6e', 'middle')
    annotations += line(1154, 174, 1154, 525.75, extra='class="dim"') + text(1176, 350, '约 117 mm', 14, '#737b6e', extra='transform="rotate(90 1176 350)"')
    annotations += '<path d="M1068 226L1034 116H899" class="leader"/>' + text(890, 118, '01 / 金属滚花旋钮', 16, '#ab2c3d', 'end')
    annotations += '<path d="M435 458L398 566H180" class="leader"/>' + text(76, 595, '02 / 逐键背光 · 柔白效果示意', 17) + text(76, 622, '灯色可调；实际透光需核对轴体与键帽。', 14, '#7d6a74')
    annotations += text(1204, 584, '67 键 + 1 个旋钮', 19, '#ab2c3d', 'end') + text(1204, 611, '旋转调音量，按压静音；Del 暂放 Fn + Backspace。', 14, '#7d6a74', 'end')
    return sheet('01 / 俯视与背光', '珍珠白字母区 / 浅粉修饰区 / 002 编号与双角图案键 / 右上角旋钮', illustration + annotations)


def reference_mark():
    try:
        mark = json.loads((ROOT / 'zero-two-reference.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise ValueError(f'Cannot load zero-two-reference.json: {error}') from error
    x0, y0, x1, y1 = mark['bounds']
    assert all(math.isfinite(value) for value in mark['bounds']) and x1 > x0 and y1 > y0
    assert len(mark['shapes']) == 38
    allowed = {'path': {'d'}, 'circle': {'cx', 'cy', 'r'}, 'polygon': {'points'}, 'line': {'x1', 'y1', 'x2', 'y2'}}
    paths = []
    for shape in mark['shapes']:
        tag, attributes = shape['tag'], shape['attributes']
        assert tag in allowed and set(attributes) <= allowed[tag]
        geometry = ' '.join(f'{name}="{escape(str(value), quote=True)}"' for name, value in attributes.items())
        paths.append(f'<{tag} class="cad-outline" data-source-entity="{int(shape["source_entity"])}" {geometry}/>')
    return mark, ''.join(paths)


def reference_svg(mark, paths):
    x0, y0, x1, y1 = mark['bounds']
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="600" viewBox="{x0 - 5} {y0 - 5} {x1 - x0 + 10} {y1 - y0 + 10}" role="img" aria-labelledby="title desc">
<title id="title">用户 DWG 提取的 002 双角头饰线稿</title>
<desc id="desc">来源：{escape(mark['source_file'])}。保留原始矢量比例，仅提取图案，非加工图。</desc>
<rect x="{x0 - 5}" y="{y0 - 5}" width="{x1 - x0 + 10}" height="{y1 - y0 + 10}" fill="#f7f7f0"/>
<g fill="none" stroke="#9e2c3d" stroke-width=".35" stroke-linejoin="round" stroke-linecap="round">{paths}</g>
</svg>\n'''


def bottom_view(mark, paths):
    body = [rect(0, 0, WIDTH, DEPTH, 'url(#ivory)', 5.5, 'stroke="#c7cabc" stroke-width=".55" filter="url(#shadow)"')]
    for x, y in FOOT_CENTERS:
        body.append(f'<g class="clear-foot" data-center-x="{x}" data-center-y="{y}" data-radius="{FOOT_RADIUS}"><circle class="footprint" cx="{x}" cy="{y}" r="{FOOT_RADIUS}" fill="url(#clear-foot)" stroke="#9daabd" stroke-opacity=".6" stroke-width=".3"/><circle cx="{x}" cy="{y}" r="{FOOT_RADIUS - .8}" fill="none" stroke="#ffffff" stroke-opacity=".65" stroke-width=".18"/><path d="M{x - 3.7} {y - 1.6}A4.2 4.2 0 0 1 {x + .6} {y - 4.2}" fill="none" stroke="#ffffff" stroke-opacity=".92" stroke-width=".5" stroke-linecap="round"/></g>')
    body.extend([rect(50, 28, WIDTH - 100, DEPTH - 56, '#b6b3ba', 3.2), rect(51, 29, WIDTH - 102, DEPTH - 58, 'url(#silver)', 2.4, 'id="weight-plate" data-material="stainless-steel-concept"'), rect(51, 29, WIDTH - 102, DEPTH - 58, 'url(#brush)', 2.4)])
    for x in (58, WIDTH - 58):
        for y in (36, DEPTH - 36):
            body.extend([f'<g class="weight-fastener"><circle cx="{x}" cy="{y}" r="1.65" fill="#8d8790"/>', line(x - .8, y, x + .8, y, '#f7f2f5', 'stroke-width=".3"'), '</g>'])
    center_x, center_y = WIDTH / 2, DEPTH / 2
    x0, y0, x1, y1 = mark['bounds']
    mark_scale = 75 / (x1 - x0)
    mark_transform = f'matrix({mark_scale} 0 0 {mark_scale} {-mark_scale * (x0 + x1) / 2} {-mark_scale * (y0 + y1) / 2})'
    body.extend([
        text(69, 57, 'DARLING65', 4.4, '#785e6a'),
        text(69, 65, 'PERSONAL EDITION', 2.3, '#856e7b'),
        text(WIDTH - 69, 57, 'STEEL WEIGHT', 2.8, '#856e7b', 'end'),
        text(WIDTH - 69, 65, 'CONCEPT 01', 2.3, '#856e7b', 'end'),
        f'<g id="zero-two-emblem" transform="translate({center_x} {center_y})" aria-label="配重正中央的 DWG 原图 002 双角头饰">',
        f'<g id="zero-two-horns" transform="{mark_transform}" fill="none" stroke="#9e2c3d" stroke-width=".6" stroke-linejoin="round" stroke-linecap="round">{paths}</g>',
        text(0, 24, '002', 4.5, '#785e6a', 'middle', 'letter-spacing="1.2"'),
        '</g>',
        rect(10, DEPTH / 2 - 5, 2.4, 10, '#a62b3b', 1),
    ])
    drawing = '<g transform="translate(159 155) scale(3)">' + ''.join(body) + '</g>'
    drawing += '<path d="M918 367L971 536H1204" class="leader"/>' + text(1204, 565, '独立可拆配重 / 雾银不锈钢效果暂定', 18, '#856e7b', 'end') + text(1204, 593, '厚度、质量和固定位置待结构校核，不承诺整机重量。', 14, '#7d6a74', 'end')
    drawing += '<path d="M225 194L181 536H76" class="leader"/>' + text(76, 565, '四颗透明圆形防滑脚垫', 18) + text(76, 593, '保留透明边缘与高光；直径、厚度及粘贴位置待定。', 14, '#7d6a74')
    return sheet('02 / 底部与配重', '雾银独立配重 / 中央 002 原图线稿 / 四角透明圆垫', drawing, 690)


def side_view():
    scale, left, floor = 8, 170, 445
    bottom = floor - FOOT_HEIGHT * scale
    front_top = bottom - 20 * scale
    rear_top = front_top - DEPTH * math.tan(math.radians(ANGLE)) * scale
    right = left + DEPTH * scale
    assert abs(math.degrees(math.atan2(front_top - rear_top, right - left)) - ANGLE) < 1e-9
    drawing = line(76, floor, 1204, floor, '#a1a79a', 'stroke-width="1.5"')
    drawing += f'<path id="case-profile" data-angle-degrees="{ANGLE}" data-front-x="{left}" data-front-y="{front_top}" data-rear-x="{right}" data-rear-y="{rear_top}" d="M{left} {front_top}L{right} {rear_top}V{bottom}H{left}Z" fill="url(#ivory)" stroke="#b7beaf" stroke-width="1.5"/>'
    drawing += line(left + 3, front_top + 25, right - 3, rear_top + 25, '#be3446', 'stroke-width="3"')
    for position in sorted({center[1] for center in FOOT_CENTERS}):
        cx, radius = left + position * scale, FOOT_RADIUS * scale
        drawing += f'<g class="clear-foot-profile" data-foot-center-y="{position}" data-height="{FOOT_HEIGHT}"><path d="M{cx - radius} {bottom}H{cx + radius}Q{cx + radius} {floor} {cx + radius / 2} {floor}H{cx - radius / 2}Q{cx - radius} {floor} {cx - radius} {bottom}Z" fill="url(#clear-foot)" stroke="#9daabd" stroke-opacity=".6" stroke-width=".9"/>' + line(cx - radius * .6, bottom + scale * .2, cx + radius * .6, bottom + scale * .2, '#ffffff', 'stroke-width="1.2" stroke-opacity=".8"') + '</g>'
    for row in range(5):
        cx = left + (11 + (row + .5) * PITCH) * scale
        cy = front_top - (cx - left) * math.tan(math.radians(ANGLE))
        drawing += f'<g class="profile-key" transform="rotate(-7 {cx} {cy})">' + rect(cx - 17, cy - 14, 34, 19, '#c4b7be', 3) + rect(cx - 65, cy - 49, 130, 37, '#f5f1ef', 7, 'stroke="#c1c7b9"') + line(cx - 49, cy - 15, cx + 49, cy - 15, '#fff4f7', 'stroke-width="2"') + '</g>'
    drawing += rect(right - 24, rear_top + 27, 24, 23, '#3b4439', 5) + rect(right - 21, rear_top + 32, 16, 11, '#a6ae9d', 3)
    drawing += text(left, 487, '前侧', 15, '#7d6a74') + text(right, 487, '后侧 / USB-C', 15, '#7d6a74', 'end')
    ox, oy, radius = 170, 550, 165
    ex, ey = ox + radius * math.cos(math.radians(ANGLE)), oy - radius * math.sin(math.radians(ANGLE))
    drawing += line(ox, oy, ox + 280, oy, '#8b9385') + line(ox, oy, ox + 280, oy - 280 * math.tan(math.radians(ANGLE)), '#ab2c3d', 'stroke-width="1.8"')
    drawing += f'<path d="M{ox + radius} {oy}A{radius} {radius} 0 0 0 {ex} {ey}" fill="none" stroke="#ab2c3d" stroke-width="2"/>'
    drawing += text(475, 539, '7° 固定倾角', 24, '#ab2c3d') + text(76, 602, '角度以定位板安装面相对桌面定义；透明圆垫等厚示意，直径、高度与键帽轮廓待定。', 15, '#7d6a74')
    return sheet('03 / 7° 侧面轮廓', '前低后高 / 透明圆垫侧视投影 / 固定 7° / USB-C 位置暂定', drawing, 690)


def outputs():
    keys = layout()
    mark, paths = reference_mark()
    drawings = {'top.svg': top_view(keys, mark, paths), 'keycaps.svg': keycaps_view(keys, mark, paths), 'bottom.svg': bottom_view(mark, paths), 'side.svg': side_view(), 'zero-two-reference.svg': reference_svg(mark, paths)}
    assert len(re.findall(r'class="key"', drawings['top.svg'])) == 67
    assert drawings['top.svg'].count('id="encoder"') == 1
    assert drawings['top.svg'].count('data-novelty="code-002"') == 1
    assert drawings['top.svg'].count('data-novelty="dwg-headpiece"') == 1
    assert drawings['top.svg'].count('data-novelty="partner-code"') == 1
    assert drawings['top.svg'].count('data-novelty="partner-link"') == 1
    assert drawings['keycaps.svg'].count('class="key"') == 5
    assert drawings['bottom.svg'].count('class="weight-fastener"') == 4
    assert drawings['bottom.svg'].count('class="clear-foot"') == 4
    assert drawings['side.svg'].count('class="clear-foot-profile"') == 2
    assert FOOT_RADIUS > 0 and FOOT_HEIGHT > 0
    assert all(FOOT_RADIUS < x < WIDTH - FOOT_RADIUS and FOOT_RADIUS < y < DEPTH - FOOT_RADIUS for x, y in FOOT_CENTERS)
    assert drawings['bottom.svg'].count('class="cad-outline"') == len(mark['shapes'])
    assert drawings['zero-two-reference.svg'].count('class="cad-outline"') == len(mark['shapes'])
    assert f'id="zero-two-emblem" transform="translate({WIDTH / 2} {DEPTH / 2})"' in drawings['bottom.svg']
    assert drawings['side.svg'].count('class="profile-key"') == 5
    for svg in drawings.values():
        assert '非加工图' in svg and '<title' in svg and '<desc' in svg
        assert '<script' not in svg and 'href=' not in svg
    return drawings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate geometry and detect stale drawings without writing.')
    args = parser.parse_args()
    try:
        drawings = outputs()
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as error:
        parser.error(f'Invalid concept drawing data: {error}')
    if args.check:
        stale = [name for name, content in drawings.items() if not (ROOT / name).exists() or (ROOT / name).read_text(encoding='utf-8') != content]
        if stale:
            parser.exit(1, 'Stale or missing: ' + ', '.join(stale) + '\n')
        print('PASS: 67 keys + encoder; 7-degree geometry; weight; all SVG files current.')
    else:
        for name, content in drawings.items():
            (ROOT / name).write_text(content, encoding='utf-8')
        print('Generated top.svg, keycaps.svg, bottom.svg, side.svg, zero-two-reference.svg. Concept drawings only.')


if __name__ == '__main__':
    main()
