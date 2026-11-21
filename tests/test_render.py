"""render 模块单元测试：三页排版、SVG 与 HTML 转义。"""

from __future__ import annotations

import unittest

from unitcircle.model import Angle, UnitCircle, UnitCircleError, make_unit_circle
from unitcircle.render import (
    angle_color,
    render_angle_strip_svg,
    render_disk_svg,
    render_html,
    render_pointer_svg,
)

ANGLES = [0, 30, 45, 60, 90, 180, 270, 360]


class RenderHtmlTest(unittest.TestCase):
    def setUp(self) -> None:
        self.circle = make_unit_circle(ANGLES, title="我的转盘")
        self.page = render_html(self.circle)

    def test_doctype_and_language(self) -> None:
        self.assertTrue(self.page.startswith("<!doctype html>"))
        self.assertIn('<html lang="zh-CN">', self.page)
        self.assertIn('<meta charset="utf-8">', self.page)

    def test_three_sheets(self) -> None:
        self.assertEqual(self.page.count("<section"), 3)
        self.assertEqual(self.page.count('class="sheet'), 3)

    def test_title(self) -> None:
        self.assertIn("<title>我的转盘</title>", self.page)
        self.assertIn("<h1>我的转盘</h1>", self.page)

    def test_title_escaped(self) -> None:
        page = render_html(
            make_unit_circle([0], title='<转盘 & "A">')
        )
        self.assertIn("&lt;转盘 &amp; &quot;A&quot;&gt;", page)
        self.assertNotIn("<转盘", page)

    def test_disk_svg(self) -> None:
        self.assertIn('class="disk"', self.page)
        self.assertIn('width="182mm" height="182mm"', self.page)
        self.assertIn('viewBox="0 0 182 182"', self.page)

    def test_major_ticks_every_thirty_degrees(self) -> None:
        self.assertEqual(self.page.count('class="tick major"'), 12)

    def test_minor_ticks(self) -> None:
        self.assertEqual(self.page.count('class="tick minor"'), 24)

    def test_quadrant_fills(self) -> None:
        self.assertEqual(self.page.count('class="quadrant"'), 4)
        self.assertIn("Ⅰ", self.page)
        self.assertIn("Ⅳ", self.page)

    def test_degree_and_radian_labels(self) -> None:
        self.assertIn("30°", self.page)
        self.assertIn("π/6", self.page)
        self.assertIn("360°", self.page)
        self.assertIn("2π", self.page)

    def test_coordinates_inside_disk(self) -> None:
        self.assertIn("(0.87, 0.5)", self.page)
        self.assertIn("(0.71, 0.71)", self.page)
        self.assertIn("(0, 1)", self.page)

    def test_center_hub(self) -> None:
        self.assertIn('class="hub"', self.page)

    def test_pointer_section(self) -> None:
        self.assertIn("可剪下指针", self.page)
        self.assertIn("带箭头与角度刻度", self.page)
        self.assertIn("沿虚线剪下", self.page)

    def test_angle_strip_section(self) -> None:
        self.assertIn("0~360° 角度条", self.page)
        self.assertIn("每 5° 一格", self.page)

    def test_table_rows(self) -> None:
        self.assertEqual(self.page.count("<tr>"), len(ANGLES) + 1)

    def test_table_headers(self) -> None:
        for header in ("度数", "弧度", "cos θ", "sin θ", "tan θ", "象限"):
            self.assertIn("<th>%s</th>" % header, self.page)

    def test_exact_and_decimal_values(self) -> None:
        self.assertIn("√2/2", self.page)
        self.assertIn("0.7071", self.page)
        self.assertIn("√3/2", self.page)
        self.assertIn("0.866", self.page)

    def test_half_values(self) -> None:
        self.assertIn('<span class="exact">1/2</span>', self.page)
        self.assertIn('<span class="approx">0.5</span>', self.page)

    def test_tangent_missing(self) -> None:
        self.assertIn('<span class="none">不存在</span>', self.page)
        self.assertIn("90° 与 270° 时 cos θ = 0", self.page)

    def test_quadrant_text_in_table(self) -> None:
        self.assertIn("第一象限", self.page)
        self.assertIn("x 轴正半轴", self.page)

    def test_page_numbers(self) -> None:
        for page_number in (1, 2, 3):
            self.assertIn("第 %d 页 / 共 3 页" % page_number, self.page)

    def test_print_css(self) -> None:
        self.assertIn("@page { size: A4 portrait; margin: 0; }", self.page)
        self.assertIn("@media print", self.page)
        self.assertIn("page-break-after: always", self.page)

    def test_real_millimetre_sizes(self) -> None:
        self.assertIn("width: 210mm", self.page)
        self.assertIn("height: 297mm", self.page)
        self.assertIn("width: 182mm", self.page)

    def test_responsive_css(self) -> None:
        self.assertIn("@media screen and (max-width: 720px)", self.page)
        self.assertIn("max-width: 100%", self.page)

    def test_no_network_resources(self) -> None:
        self.assertNotIn("https://", self.page)
        self.assertNotIn("<script", self.page)
        self.assertNotIn("@import", self.page)
        self.assertNotIn("url(", self.page)

    def test_non_circle_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            render_html("circle")  # type: ignore[arg-type]

    def test_twenty_four_rows(self) -> None:
        circle = make_unit_circle(list(range(0, 360, 15)))
        page = render_html(circle)
        self.assertEqual(page.count("<tr>"), 25)


class RenderDiskTest(unittest.TestCase):
    def test_invalid_circle_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            render_disk_svg("circle")  # type: ignore[arg-type]

    def test_aria_label_contains_angles(self) -> None:
        svg = render_disk_svg(make_unit_circle([0, 90]))
        self.assertIn('aria-label="单位圆转盘', svg)
        self.assertIn("0°", svg)
        self.assertIn("90°", svg)

    def test_duplicate_position_drawn_once(self) -> None:
        svg = render_disk_svg(make_unit_circle([0, 360]))
        self.assertEqual(svg.count('class="ray"'), 1)
        self.assertEqual(svg.count('class="point"'), 1)


class RenderToolsTest(unittest.TestCase):
    def test_pointer_has_arrow_and_hole(self) -> None:
        svg = render_pointer_svg()
        self.assertIn("pointer-svg", svg)
        self.assertIn("<polygon", svg)
        self.assertIn('r="2.4"', svg)
        self.assertIn("90°", svg)

    def test_strip_endpoints(self) -> None:
        svg = render_angle_strip_svg()
        self.assertIn(">0°</text>", svg)
        self.assertIn(">360°</text>", svg)
        self.assertIn("strip-svg", svg)

    def test_strip_quadrant_labels(self) -> None:
        svg = render_angle_strip_svg()
        for label in ("Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ"):
            self.assertIn(label, svg)


class AngleColorTest(unittest.TestCase):
    def test_colors_are_distinct(self) -> None:
        colors = [angle_color(index, 16) for index in range(16)]
        self.assertEqual(len(set(colors)), 16)

    def test_color_format(self) -> None:
        self.assertEqual(angle_color(0, 4), "hsl(0, 70%, 42%)")
        self.assertEqual(angle_color(1, 4), "hsl(90, 70%, 42%)")

    def test_invalid_index(self) -> None:
        for index in (-1, 4, True, "0"):
            with self.assertRaises(UnitCircleError):
                angle_color(index, 4)  # type: ignore[arg-type]

    def test_invalid_total(self) -> None:
        with self.assertRaises(UnitCircleError):
            angle_color(0, 0)


class UnitCircleAngleTest(unittest.TestCase):
    def test_angle_list_is_sorted(self) -> None:
        circle = UnitCircle(angles=(Angle(90), Angle(0)))
        self.assertEqual([angle.degrees for angle in circle.angles], [0, 90])

    def test_count_property(self) -> None:
        self.assertEqual(make_unit_circle([0, 45, 90]).count, 3)


if __name__ == "__main__":
    unittest.main()
