"""把单位圆转盘渲染成自包含、可打印的 A4 纵向 HTML。"""

from __future__ import annotations

import html
import math
from typing import Dict, List, Sequence, Tuple

from .model import Angle, UnitCircle, UnitCircleError, format_decimal

SVG_SIZE_MM = 182.0
CENTER_MM = SVG_SIZE_MM / 2.0
DISK_RADIUS_MM = 58.0
MAJOR_TICK_MM = 63.0
MINOR_TICK_MM = 60.5
SCALE_LABEL_MM = 51.5
POINT_RADIUS_MM = 1.8
COORD_RADII_MM = (42.0, 31.0)
ANGLE_RADII_MM = (71.0, 79.0)
QUADRANT_LABEL_MM = 19.0

QUADRANT_FILLS: Tuple[Tuple[int, int, str, str], ...] = (
    (0, 90, "#fef3c7", "Ⅰ"),
    (90, 180, "#e0f2fe", "Ⅱ"),
    (180, 270, "#dcfce7", "Ⅲ"),
    (270, 360, "#fae8ff", "Ⅳ"),
)

PAGE_COUNT = 3


def _num(value: float) -> str:
    """把毫米坐标格式化成紧凑文本，避免浮点尾数。"""
    text = "%.3f" % value
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text == "-0":
        return "0"
    return text


def _point(radius: float, degrees: float) -> Tuple[float, float]:
    """单位圆上按数学角度取屏幕坐标（y 轴向下）。"""
    radians = math.radians(degrees)
    return (
        CENTER_MM + radius * math.cos(radians),
        CENTER_MM - radius * math.sin(radians),
    )


def _anchor(x: float) -> str:
    """按横向位置选择文本锚点，避免标签越出画布。"""
    if x > CENTER_MM + 2.0:
        return "start"
    if x < CENTER_MM - 2.0:
        return "end"
    return "middle"


def angle_color(index: int, total: int) -> str:
    """按序号生成互不相同的颜色，最多 24 个角度也能区分。"""
    if isinstance(index, bool) or not isinstance(index, int):
        raise UnitCircleError("颜色索引必须是整数")
    if isinstance(total, bool) or not isinstance(total, int):
        raise UnitCircleError("角度总数必须是整数")
    if total < 1:
        raise UnitCircleError("角度总数必须大于 0")
    if not 0 <= index < total:
        raise UnitCircleError("颜色索引超出范围：%d" % index)
    hue = int(round(index * 360.0 / total)) % 360
    return "hsl(%d, 70%%, 42%%)" % hue


def _lanes(angles: Sequence[Angle], lane_count: int, threshold: int) -> List[int]:
    """给相邻角度分配不同半径，减少文字重叠。"""
    lanes: List[int] = []
    used: Dict[int, List[int]] = {}
    previous: int = -1
    lane = 0
    for angle in angles:
        position = angle.position
        if previous >= 0:
            gap = (angle.degrees - previous) % 360
            if gap < threshold or position in used:
                lane = (lane + 1) % lane_count
            else:
                lane = 0
        taken = used.setdefault(position, [])
        while lane in taken:
            lane = (lane + 1) % lane_count
        taken.append(lane)
        lanes.append(lane)
        previous = angle.degrees
    return lanes


def _quadrant_markup() -> List[str]:
    parts: List[str] = []
    for start, end, fill, label in QUADRANT_FILLS:
        x1, y1 = _point(DISK_RADIUS_MM, start)
        x2, y2 = _point(DISK_RADIUS_MM, end)
        path = "M %s %s L %s %s A %s %s 0 0 0 %s %s Z" % (
            _num(CENTER_MM),
            _num(CENTER_MM),
            _num(x1),
            _num(y1),
            _num(DISK_RADIUS_MM),
            _num(DISK_RADIUS_MM),
            _num(x2),
            _num(y2),
        )
        parts.append(
            '<path class="quadrant" d="%s" fill="%s" fill-opacity="0.65"/>'
            % (path, fill)
        )
        mx, my = _point(QUADRANT_LABEL_MM, (start + end) / 2.0)
        parts.append(
            '<text class="quadrant-label" x="%s" y="%s" text-anchor="middle"'
            ' font-size="6.5" fill="#64748b" fill-opacity="0.5">%s</text>'
            % (_num(mx), _num(my + 2.2), label)
        )
    return parts


def _axes_markup() -> List[str]:
    span = DISK_RADIUS_MM + 6.0
    low = _num(CENTER_MM - span)
    high = _num(CENTER_MM + span)
    center = _num(CENTER_MM)
    return [
        '<g class="axes">',
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#334155"'
        ' stroke-width="0.4"/>' % (low, center, high, center),
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#334155"'
        ' stroke-width="0.4"/>' % (center, low, center, high),
        '<polygon points="%s,%s %s,%s %s,%s" fill="#334155"/>'
        % (
            high,
            center,
            _num(CENTER_MM + span - 3.5),
            _num(CENTER_MM - 1.4),
            _num(CENTER_MM + span - 3.5),
            _num(CENTER_MM + 1.4),
        ),
        '<polygon points="%s,%s %s,%s %s,%s" fill="#334155"/>'
        % (
            low,
            center,
            _num(CENTER_MM - span + 3.5),
            _num(CENTER_MM - 1.4),
            _num(CENTER_MM - span + 3.5),
            _num(CENTER_MM + 1.4),
        ),
        '<polygon points="%s,%s %s,%s %s,%s" fill="#334155"/>'
        % (
            center,
            low,
            _num(CENTER_MM - 1.4),
            _num(CENTER_MM - span + 3.5),
            _num(CENTER_MM + 1.4),
            _num(CENTER_MM - span + 3.5),
        ),
        '<polygon points="%s,%s %s,%s %s,%s" fill="#334155"/>'
        % (
            center,
            high,
            _num(CENTER_MM - 1.4),
            _num(CENTER_MM + span - 3.5),
            _num(CENTER_MM + 1.4),
            _num(CENTER_MM + span - 3.5),
        ),
        '<text x="%s" y="%s" font-size="3.2" font-style="italic"'
        ' fill="#334155">x</text>'
        % (_num(CENTER_MM + span + 2.5), _num(CENTER_MM + 1.2)),
        '<text x="%s" y="%s" font-size="3.2" font-style="italic"'
        ' fill="#334155">y</text>'
        % (_num(CENTER_MM + 2.2), _num(CENTER_MM - span - 2.5)),
        "</g>",
    ]


def _ticks_markup() -> List[str]:
    parts: List[str] = ['<g class="ticks">']
    for degree in range(0, 360, 10):
        major = degree % 30 == 0
        outer = MAJOR_TICK_MM if major else MINOR_TICK_MM
        x1, y1 = _point(DISK_RADIUS_MM, degree)
        x2, y2 = _point(outer, degree)
        parts.append(
            '<line class="tick %s" x1="%s" y1="%s" x2="%s" y2="%s"'
            ' stroke="%s" stroke-width="%s"/>'
            % (
                "major" if major else "minor",
                _num(x1),
                _num(y1),
                _num(x2),
                _num(y2),
                "#475569" if major else "#94a3b8",
                "0.45" if major else "0.25",
            )
        )
    parts.append("</g>")
    parts.append('<g class="scale">')
    for degree in range(0, 360, 30):
        x, y = _point(SCALE_LABEL_MM, degree)
        parts.append(
            '<text class="scale-label" x="%s" y="%s" text-anchor="%s"'
            ' font-size="2.2" fill="#64748b" paint-order="stroke"'
            ' stroke="#ffffff" stroke-width="0.7">%d°</text>'
            % (_num(x), _num(y + 0.8), _anchor(x), degree)
        )
    parts.append("</g>")
    return parts


def _rays_markup(circle: UnitCircle) -> List[str]:
    parts: List[str] = ['<g class="rays">']
    seen: Dict[int, None] = {}
    for index, angle in enumerate(circle.angles):
        if angle.position in seen:
            continue
        seen[angle.position] = None
        color = angle_color(index, circle.count)
        x, y = _point(DISK_RADIUS_MM * 0.98, angle.degrees)
        parts.append(
            '<line class="ray" x1="%s" y1="%s" x2="%s" y2="%s"'
            ' stroke="%s" stroke-width="0.7" stroke-linecap="round"/>'
            % (
                _num(CENTER_MM),
                _num(CENTER_MM),
                _num(x),
                _num(y),
                color,
            )
        )
        parts.append(
            '<circle class="point" cx="%s" cy="%s" r="%s" fill="%s"'
            ' stroke="#ffffff" stroke-width="0.35"/>'
            % (_num(x), _num(y), _num(POINT_RADIUS_MM), color)
        )
    parts.append("</g>")
    return parts


def _coords_markup(circle: UnitCircle) -> List[str]:
    parts: List[str] = ['<g class="coords">']
    lanes = _lanes(circle.angles, len(COORD_RADII_MM), 20)
    seen: Dict[int, None] = {}
    for index, angle in enumerate(circle.angles):
        if angle.position in seen:
            continue
        seen[angle.position] = None
        radius = COORD_RADII_MM[lanes[index]]
        x, y = _point(radius, angle.degrees)
        label = "(%s, %s)" % (
            format_decimal(angle.cos_value, 2),
            format_decimal(angle.sin_value, 2),
        )
        anchor = _anchor(x)
        width = len(label) * 1.7 * 0.58
        if anchor == "start":
            rect_x = x
        elif anchor == "end":
            rect_x = x - width
        else:
            rect_x = x - width / 2.0
        parts.append(
            '<rect class="coord-bg" x="%s" y="%s" width="%s" height="2.9"'
            ' rx="0.4" fill="#ffffff" fill-opacity="0.82"/>'
            % (_num(rect_x), _num(y + 0.7 - 2.1), _num(width))
        )
        parts.append(
            '<text class="coord" x="%s" y="%s" text-anchor="%s"'
            ' font-size="1.7" font-weight="600" fill="%s" paint-order="stroke"'
            ' stroke="#ffffff" stroke-width="0.55">%s</text>'
            % (
                _num(x),
                _num(y + 0.7),
                anchor,
                angle_color(index, circle.count),
                html.escape(label),
            )
        )
    parts.append("</g>")
    return parts


def _labels_markup(circle: UnitCircle) -> List[str]:
    parts: List[str] = ['<g class="angle-labels">']
    lanes = _lanes(circle.angles, len(ANGLE_RADII_MM), 20)
    for index, angle in enumerate(circle.angles):
        radius = ANGLE_RADII_MM[lanes[index]]
        x, y = _point(radius, angle.degrees)
        x_text = _num(x)
        parts.append(
            '<text class="angle-label" x="%s" y="%s" text-anchor="%s"'
            ' font-size="2.5" fill="%s" paint-order="stroke" stroke="#ffffff"'
            ' stroke-width="0.8"><tspan x="%s" font-weight="700">%d°</tspan>'
            '<tspan x="%s" dy="3.1" font-weight="400">%s</tspan></text>'
            % (
                x_text,
                _num(y + 0.9),
                _anchor(x),
                angle_color(index, circle.count),
                x_text,
                angle.degrees,
                x_text,
                html.escape(angle.radian_text),
            )
        )
    parts.append("</g>")
    return parts


def _hub_markup() -> List[str]:
    center = _num(CENTER_MM)
    return [
        '<g class="hub">',
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#0f172a"'
        ' stroke-width="0.35"/>'
        % (
            _num(CENTER_MM - 9.0),
            center,
            _num(CENTER_MM + 9.0),
            center,
        ),
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#0f172a"'
        ' stroke-width="0.35"/>'
        % (
            center,
            _num(CENTER_MM - 9.0),
            center,
            _num(CENTER_MM + 9.0),
        ),
        '<circle cx="%s" cy="%s" r="4.2" fill="#ffffff" stroke="#0f172a"'
        ' stroke-width="0.4"/>' % (center, center),
        "</g>",
    ]


def render_disk_svg(circle: UnitCircle) -> str:
    """绘制第 1 页的单位圆盘。"""
    if not isinstance(circle, UnitCircle):
        raise UnitCircleError("circle 必须是 UnitCircle 对象")
    summary = "、".join("%d°" % angle.degrees for angle in circle.angles)
    label = "单位圆转盘，标出 %d 个角度：%s" % (circle.count, summary)
    parts: List[str] = [
        '<svg class="disk" xmlns="http://www.w3.org/2000/svg"'
        ' width="%smm" height="%smm" viewBox="0 0 %s %s" role="img"'
        ' aria-label="%s">'
        % (
            _num(SVG_SIZE_MM),
            _num(SVG_SIZE_MM),
            _num(SVG_SIZE_MM),
            _num(SVG_SIZE_MM),
            html.escape(label),
        )
    ]
    parts.extend(_quadrant_markup())
    parts.append(
        '<circle class="rim" cx="%s" cy="%s" r="%s" fill="none"'
        ' stroke="#334155" stroke-width="0.45"/>'
        % (_num(CENTER_MM), _num(CENTER_MM), _num(DISK_RADIUS_MM))
    )
    parts.extend(_axes_markup())
    parts.extend(_ticks_markup())
    parts.extend(_rays_markup(circle))
    parts.extend(_coords_markup(circle))
    parts.extend(_labels_markup(circle))
    parts.extend(_hub_markup())
    parts.append("</svg>")
    return "".join(parts)


def render_pointer_svg() -> str:
    """绘制可剪下的指针：箭头、轴孔与刻度环。"""
    parts: List[str] = [
        '<svg class="pointer-svg" xmlns="http://www.w3.org/2000/svg"'
        ' width="180mm" height="60mm" viewBox="0 0 180 60" role="img"'
        ' aria-label="可剪下的指针，带箭头和 0~360 度刻度环">',
        '<rect x="4" y="5" width="172" height="42" rx="4" fill="none"'
        ' stroke="#94a3b8" stroke-width="0.35" stroke-dasharray="2 1.6"/>',
        '<text x="7" y="12.5" font-size="2.6" fill="#64748b">'
        "沿虚线剪下</text>",
        '<g class="pointer-body">',
        '<polygon points="30,23.5 134,25.4 134,30.6 30,32.5"'
        ' fill="#fcd34d" stroke="#b45309" stroke-width="0.35"/>',
        '<polygon points="134,21 162,28 134,35" fill="#f59e0b"'
        ' stroke="#b45309" stroke-width="0.35"/>',
        '<circle cx="30" cy="28" r="10.5" fill="#fffbeb" stroke="#b45309"'
        ' stroke-width="0.4"/>',
        "</g>",
        '<g class="pointer-scale">',
    ]
    for degree in range(0, 360, 15):
        outer = 14.0 if degree % 30 == 0 else 13.0
        x1, y1 = 30.0 + 10.5 * math.cos(math.radians(degree)), 28.0 - 10.5 * math.sin(
            math.radians(degree)
        )
        x2, y2 = 30.0 + outer * math.cos(math.radians(degree)), 28.0 - outer * math.sin(
            math.radians(degree)
        )
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#b45309"'
            ' stroke-width="0.28"/>'
            % (_num(x1), _num(y1), _num(x2), _num(y2))
        )
    for degree in (90, 180, 270):
        x, y = 30.0 + 17.5 * math.cos(math.radians(degree)), 28.0 - 17.5 * math.sin(
            math.radians(degree)
        )
        parts.append(
            '<text x="%s" y="%s" text-anchor="middle" font-size="1.8"'
            ' fill="#92400e">%d°</text>'
            % (_num(x), _num(y + 0.7), degree)
        )
    parts.append("</g>")
    parts.append(
        '<circle cx="30" cy="28" r="2.4" fill="#ffffff" stroke="#92400e"'
        ' stroke-width="0.35"/>'
    )
    parts.append(
        '<text x="7" y="56" font-size="2.6" fill="#475569">'
        "中心孔对准转盘轴孔，用图钉固定后即可旋转</text>"
    )
    parts.append("</svg>")
    return "".join(parts)


def render_angle_strip_svg() -> str:
    """绘制 0~360° 角度条，每 5° 一格、每 30° 标数字。"""
    x0 = 12.0
    x1 = 168.0
    width = x1 - x0
    parts: List[str] = [
        '<svg class="strip-svg" xmlns="http://www.w3.org/2000/svg"'
        ' width="180mm" height="64mm" viewBox="0 0 180 64" role="img"'
        ' aria-label="0 到 360 度角度条，每 5 度一格，四段颜色对应四个象限">',
        '<rect x="4" y="5" width="172" height="38" rx="2" fill="none"'
        ' stroke="#94a3b8" stroke-width="0.35" stroke-dasharray="2 1.6"/>',
        '<g class="strip-bands">',
    ]
    for start, end, fill, label in QUADRANT_FILLS:
        left = x0 + width * start / 360.0
        right = x0 + width * end / 360.0
        parts.append(
            '<rect x="%s" y="9" width="%s" height="20" fill="%s"'
            ' fill-opacity="0.65"/>'
            % (_num(left), _num(right - left), fill)
        )
        parts.append(
            '<text x="%s" y="19.5" text-anchor="middle" font-size="5"'
            ' fill="#64748b" fill-opacity="0.55">%s</text>'
            % (_num((left + right) / 2.0), label)
        )
    parts.append(
        '<rect x="%s" y="9" width="%s" height="20" fill="none"'
        ' stroke="#94a3b8" stroke-width="0.35"/>' % (_num(x0), _num(width))
    )
    parts.append("</g>")
    parts.append('<g class="strip-ticks">')
    for degree in range(0, 361, 5):
        x = x0 + width * degree / 360.0
        if degree % 30 == 0:
            bottom = 37.0
            stroke = "#475569"
            stroke_width = "0.4"
        elif degree % 10 == 0:
            bottom = 34.0
            stroke = "#64748b"
            stroke_width = "0.3"
        else:
            bottom = 31.5
            stroke = "#94a3b8"
            stroke_width = "0.2"
        parts.append(
            '<line x1="%s" y1="29" x2="%s" y2="%s" stroke="%s"'
            ' stroke-width="%s"/>'
            % (_num(x), _num(x), _num(bottom), stroke, stroke_width)
        )
    parts.append("</g>")
    parts.append('<g class="strip-labels">')
    for degree in range(0, 361, 30):
        x = x0 + width * degree / 360.0
        if degree == 0:
            anchor = "start"
        elif degree == 360:
            anchor = "end"
        else:
            anchor = "middle"
        parts.append(
            '<text x="%s" y="42" text-anchor="%s" font-size="2.3"'
            ' fill="#334155">%d°</text>'
            % (_num(x), anchor, degree)
        )
    parts.append("</g>")
    parts.append(
        '<text x="7" y="53" font-size="2.6" fill="#475569">'
        "剪下角度条，把 0° 端对齐圆盘右侧，配合指针读出任意角度</text>"
    )
    parts.append("</svg>")
    return "".join(parts)


def _value_cell(exact: str, approx: str) -> str:
    if exact == approx:
        return '<span class="exact">%s</span>' % html.escape(exact)
    return (
        '<span class="exact">%s</span><span class="approx">%s</span>'
        % (html.escape(exact), html.escape(approx))
    )


def _table_markup(circle: UnitCircle) -> str:
    rows: List[str] = []
    for index, angle in enumerate(circle.angles):
        color = angle_color(index, circle.count)
        if angle.tan_exact is None and angle.tan_value is None:
            tan_cell = '<span class="none">不存在</span>'
        elif angle.tan_exact is None:
            tan_cell = '<span class="approx-only">%s</span>' % html.escape(
                angle.tan_text
            )
        else:
            tan_cell = _value_cell(angle.tan_exact, angle.tan_text)
        if angle.cos_exact is None:
            cos_cell = '<span class="approx-only">%s</span>' % html.escape(
                angle.cos_text
            )
        else:
            cos_cell = _value_cell(angle.cos_exact, angle.cos_text)
        if angle.sin_exact is None:
            sin_cell = '<span class="approx-only">%s</span>' % html.escape(
                angle.sin_text
            )
        else:
            sin_cell = _value_cell(angle.sin_exact, angle.sin_text)
        rows.append(
            '<tr><td class="deg"><span class="swatch" style="background:%s">'
            "</span>%d°</td><td class=\"rad\">%s</td><td>%s</td><td>%s</td>"
            '<td>%s</td><td class="quad">%s</td></tr>'
            % (
                color,
                angle.degrees,
                html.escape(angle.radian_text),
                cos_cell,
                sin_cell,
                tan_cell,
                html.escape(angle.quadrant_text),
            )
        )
    return (
        '<table class="values"><thead><tr><th>度数</th><th>弧度</th>'
        "<th>cos θ</th><th>sin θ</th><th>tan θ</th><th>象限</th></tr></thead>"
        "<tbody>%s</tbody></table>" % "".join(rows)
    )


def _header(title: str, subtitle: str) -> str:
    return (
        '<header class="head"><h1>%s</h1><p class="sub">%s</p></header>'
        % (html.escape(title), html.escape(subtitle))
    )


def _footer(page: int) -> str:
    return (
        '<footer class="foot"><span>unitcircle · A4 纵向 · 打印后沿虚线剪下</span>'
        '<span class="page">第 %d 页 / 共 %d 页</span></footer>' % (page, PAGE_COUNT)
    )


def _page_disk(circle: UnitCircle) -> str:
    subtitle = "共 %d 个角度 · 外圈标角度与弧度 · 圆内标坐标" % circle.count
    note = (
        "四个象限用淡色区分；外圈每 30° 一条主刻度、每 10° 一条次刻度。"
        "圆内坐标保留 2 位小数，cos / sin 的 4 位小数见第 3 页。"
    )
    return (
        '<section class="sheet sheet-disk">%s'
        '<div class="disk-body"><div class="chart">%s</div>'
        '<p class="note">%s</p></div>%s</section>'
        % (
            _header(circle.title, subtitle),
            render_disk_svg(circle),
            html.escape(note),
            _footer(1),
        )
    )


def _page_tools(circle: UnitCircle) -> str:
    subtitle = "第 2 页 · 指针与 0~360° 角度条"
    note = (
        "组装：沿虚线剪下指针和角度条，用图钉穿过指针中心孔与转盘轴孔；"
        "转动指针即可读取角度，再对照第 3 页的三角函数值。"
    )
    return (
        '<section class="sheet sheet-tools">%s'
        '<div class="tools-body">'
        '<div class="tool"><h2>可剪下指针</h2>'
        '<p class="hint">带箭头与角度刻度，中心孔对准转盘轴孔。</p>'
        '<div class="pointer">%s</div></div>'
        '<div class="tool"><h2>0~360° 角度条</h2>'
        '<p class="hint">每 5° 一格，每 30° 标数字，四段淡色对应四个象限。</p>'
        '<div class="strip">%s</div></div>'
        '<p class="note">%s</p></div>%s</section>'
        % (
            _header(circle.title, subtitle),
            render_pointer_svg(),
            render_angle_strip_svg(),
            html.escape(note),
            _footer(2),
        )
    )


def _page_table(circle: UnitCircle) -> str:
    subtitle = "第 3 页 · 三角函数值表 · %d 个角度" % circle.count
    practice = (
        "练习卡：用纸遮住 cos、sin、tan 三列，自己写出数值，再对照检查。"
        "tan θ = sin θ / cos θ；90° 与 270° 时 cos θ = 0，tan θ 不存在。"
    )
    return (
        '<section class="sheet sheet-table">%s%s'
        '<div class="practice">%s</div>%s</section>'
        % (
            _header(circle.title, subtitle),
            _table_markup(circle),
            html.escape(practice),
            _footer(3),
        )
    )


def render_html(circle: UnitCircle) -> str:
    """生成完整 HTML：3 页 A4 纵向，自包含且不联网。"""
    if not isinstance(circle, UnitCircle):
        raise UnitCircleError("circle 必须是 UnitCircle 对象")
    title = html.escape(circle.title)
    toolbar = (
        '<div class="toolbar"><strong>%s</strong>'
        "<span>%d 个角度 · 3 页 · A4 纵向</span></div>"
        % (title, circle.count)
    )
    return (
        "<!doctype html>\n"
        '<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n"
        "%s\n<main>%s%s%s</main>\n</body>\n</html>\n"
        % (
            title,
            _style(),
            toolbar,
            _page_disk(circle),
            _page_tools(circle),
            _page_table(circle),
        )
    )


def _style() -> str:
    return """
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; }
  body {
    margin: 0;
    padding: 7mm 4mm 9mm;
    background: #e2e8f0;
    color: #0f172a;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC",
      "Source Han Sans SC", sans-serif;
  }
  .toolbar {
    width: 210mm;
    max-width: 100%;
    margin: 0 auto 4mm;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 10px;
    color: #334155;
    font-size: 13px;
  }
  .toolbar strong { font-size: 15px; letter-spacing: 1px; }
  .toolbar span { color: #64748b; font-size: 12px; }
  .sheet {
    width: 210mm;
    max-width: 100%;
    min-height: 297mm;
    margin: 0 auto 6mm;
    padding: 12mm 14mm 10mm;
    background: #fff;
    box-shadow: 0 6px 22px rgba(15, 23, 42, 0.14);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .head { text-align: center; margin-bottom: 2mm; }
  .head h1 {
    margin: 0;
    font-size: 20pt;
    font-weight: 600;
    letter-spacing: 4pt;
  }
  .head .sub {
    margin: 1.6mm 0 0;
    font-size: 9.5pt;
    color: #475569;
    letter-spacing: 0.3pt;
  }
  .chart {
    width: 182mm;
    max-width: 100%;
    margin: 1mm auto 0;
  }
  .disk-body, .tools-body { margin: auto 0; }
  .sheet-disk .foot, .sheet-tools .foot { margin-top: 0; }
  .chart svg {
    display: block;
    width: 182mm;
    max-width: 100%;
    height: auto;
    margin: 0 auto;
  }
  .note {
    margin: 2mm 0 0;
    font-size: 8.5pt;
    line-height: 1.6;
    color: #475569;
    text-align: center;
  }
  .foot {
    margin-top: auto;
    padding-top: 2mm;
    border-top: 0.2mm solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    gap: 10px;
    font-size: 8pt;
    color: #64748b;
  }
  .tool { margin: 1.5mm 0 0; }
  .tool h2 {
    margin: 0 0 1mm;
    font-size: 12pt;
    font-weight: 600;
    letter-spacing: 1pt;
    color: #1e293b;
  }
  .tool .hint {
    margin: 0 0 1mm;
    font-size: 8.5pt;
    color: #64748b;
  }
  .pointer, .strip { width: 182mm; max-width: 100%; margin: 0 auto; }
  .pointer svg, .strip svg { display: block; width: 100%; height: auto; }
  table.values {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    margin-top: 1mm;
  }
  table.values th,
  table.values td {
    border: 0.25mm solid #cbd5e1;
    padding: 1mm 1.5mm;
    text-align: center;
    vertical-align: middle;
    font-size: 9pt;
    line-height: 1.25;
    overflow-wrap: anywhere;
  }
  table.values th {
    background: #f1f5f9;
    font-size: 9.5pt;
    font-weight: 600;
  }
  table.values td.deg { font-weight: 600; white-space: nowrap; }
  table.values td.rad { white-space: nowrap; }
  table.values .exact { display: block; font-weight: 600; }
  table.values .approx { display: block; font-size: 7pt; color: #64748b; }
  table.values .none { color: #b91c1c; font-weight: 600; }
  .swatch {
    display: inline-block;
    width: 2.2mm;
    height: 2.2mm;
    border-radius: 50%;
    margin-right: 1.2mm;
    vertical-align: -0.1mm;
  }
  .practice {
    margin-top: 2.5mm;
    padding: 2mm 3mm;
    border: 0.3mm dashed #94a3b8;
    border-radius: 1.5mm;
    font-size: 8.5pt;
    line-height: 1.6;
    color: #334155;
  }
  @media screen and (max-width: 720px) {
    body { padding: 4mm 3mm 6mm; }
    .toolbar { flex-direction: column; gap: 2px; font-size: 12px; }
    .sheet { min-height: 0; padding: 8mm 5mm; overflow: visible; }
    .head h1 { font-size: 16pt; letter-spacing: 2pt; }
    .chart, .chart svg, .pointer, .strip { width: 100%; }
    table.values th, table.values td {
      padding: 0.8mm 0.6mm;
      font-size: 8pt;
    }
    table.values .approx { font-size: 6.5pt; }
  }
  @page { size: A4 portrait; margin: 0; }
  @media print {
    body { background: #fff; padding: 0; }
    .toolbar { display: none; }
    .sheet {
      width: 210mm;
      height: 297mm;
      min-height: 0;
      max-width: none;
      margin: 0;
      padding: 12mm 14mm 10mm;
      box-shadow: none;
      overflow: hidden;
      page-break-after: always;
      break-after: page;
    }
    .sheet:last-child { page-break-after: auto; break-after: auto; }
    .chart svg, .pointer svg, .strip svg {
      width: 182mm;
      max-width: none;
    }
    * {
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
  }
"""
