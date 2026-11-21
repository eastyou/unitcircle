"""model 模块单元测试：角度解析、弧度文本与三角函数值。"""

from __future__ import annotations

import math
import unittest

from unitcircle.model import (
    DEFAULT_ANGLES_TEXT,
    Angle,
    UnitCircle,
    UnitCircleError,
    exact_value,
    format_decimal,
    format_radian,
    make_unit_circle,
    parse_angles,
)


class ParseAnglesTest(unittest.TestCase):
    def test_single_angle(self) -> None:
        self.assertEqual(parse_angles("30"), (30,))

    def test_ascii_commas(self) -> None:
        self.assertEqual(parse_angles("0,30,45,90"), (0, 30, 45, 90))

    def test_chinese_commas(self) -> None:
        self.assertEqual(parse_angles("0，30，45"), (0, 30, 45))

    def test_mixed_commas(self) -> None:
        self.assertEqual(parse_angles("0, 30，45"), (0, 30, 45))

    def test_whitespace_is_trimmed(self) -> None:
        self.assertEqual(parse_angles(" 0 , 30 ，45 "), (0, 30, 45))

    def test_dedupe(self) -> None:
        self.assertEqual(parse_angles("90,30,90,30"), (30, 90))

    def test_sort_ascending(self) -> None:
        self.assertEqual(parse_angles("330,0,180,30"), (0, 30, 180, 330))

    def test_bounds_zero_and_360(self) -> None:
        self.assertEqual(parse_angles("0"), (0,))
        self.assertEqual(parse_angles("360"), (360,))

    def test_twenty_four_angles_allowed(self) -> None:
        text = ",".join(str(value) for value in range(0, 360, 15))
        self.assertEqual(len(parse_angles(text)), 24)

    def test_twenty_five_angles_rejected(self) -> None:
        text = ",".join(str(value) for value in range(0, 361, 15))
        with self.assertRaises(UnitCircleError) as ctx:
            parse_angles(text)
        self.assertIn("1~24", str(ctx.exception))

    def test_negative_rejected(self) -> None:
        with self.assertRaises(UnitCircleError) as ctx:
            parse_angles("-30")
        self.assertIn("-30", str(ctx.exception))

    def test_over_360_rejected(self) -> None:
        with self.assertRaises(UnitCircleError) as ctx:
            parse_angles("361")
        self.assertIn("超出", str(ctx.exception))

    def test_decimal_rejected(self) -> None:
        with self.assertRaises(UnitCircleError) as ctx:
            parse_angles("30.5")
        self.assertIn("整数", str(ctx.exception))

    def test_non_numeric_rejected(self) -> None:
        with self.assertRaises(UnitCircleError) as ctx:
            parse_angles("abc")
        self.assertIn("abc", str(ctx.exception))

    def test_empty_rejected(self) -> None:
        for text in ("", "   "):
            with self.assertRaises(UnitCircleError) as ctx:
                parse_angles(text)
            self.assertIn("不能为空", str(ctx.exception))

    def test_only_commas_rejected(self) -> None:
        with self.assertRaises(UnitCircleError) as ctx:
            parse_angles(",")
        self.assertIn("为空", str(ctx.exception))

    def test_empty_token_rejected(self) -> None:
        with self.assertRaises(UnitCircleError) as ctx:
            parse_angles("0,,30")
        self.assertIn("第 2 个", str(ctx.exception))

    def test_trailing_comma_rejected(self) -> None:
        with self.assertRaises(UnitCircleError) as ctx:
            parse_angles("30,")
        self.assertIn("第 2 个", str(ctx.exception))

    def test_non_text_rejected(self) -> None:
        with self.assertRaises(UnitCircleError) as ctx:
            parse_angles(123)  # type: ignore[arg-type]
        self.assertIn("文本", str(ctx.exception))

    def test_default_angles_text(self) -> None:
        angles = parse_angles(DEFAULT_ANGLES_TEXT)
        self.assertEqual(len(angles), 16)
        self.assertEqual(angles[0], 0)
        self.assertEqual(angles[-1], 330)


class FormatDecimalTest(unittest.TestCase):
    def test_whole_number(self) -> None:
        self.assertEqual(format_decimal(1.0), "1")

    def test_half(self) -> None:
        self.assertEqual(format_decimal(0.5), "0.5")

    def test_trailing_zeros_removed(self) -> None:
        self.assertEqual(format_decimal(0.8660254, 4), "0.866")

    def test_four_digits_kept(self) -> None:
        self.assertEqual(format_decimal(0.70710678, 4), "0.7071")

    def test_zero(self) -> None:
        self.assertEqual(format_decimal(0.0), "0")

    def test_negative_zero(self) -> None:
        self.assertEqual(format_decimal(-0.0), "0")

    def test_negative_value(self) -> None:
        self.assertEqual(format_decimal(-0.5), "-0.5")

    def test_two_digits(self) -> None:
        self.assertEqual(format_decimal(0.8660254, 2), "0.87")

    def test_non_number_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            format_decimal("0.5")  # type: ignore[arg-type]

    def test_bool_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            format_decimal(True)  # type: ignore[arg-type]

    def test_digits_type_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            format_decimal(0.5, "4")  # type: ignore[arg-type]

    def test_digits_range_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            format_decimal(0.5, -1)

    def test_infinite_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            format_decimal(float("inf"))


class FormatRadianTest(unittest.TestCase):
    def test_special_angles(self) -> None:
        expected = {
            0: "0",
            30: "π/6",
            45: "π/4",
            60: "π/3",
            90: "π/2",
            120: "2π/3",
            135: "3π/4",
            150: "5π/6",
            180: "π",
            210: "7π/6",
            225: "5π/4",
            240: "4π/3",
            270: "3π/2",
            300: "5π/3",
            315: "7π/4",
            330: "11π/6",
            360: "2π",
        }
        for degree, text in expected.items():
            self.assertEqual(format_radian(degree), text, degree)

    def test_non_special_angle_uses_decimals(self) -> None:
        self.assertEqual(format_radian(20), "0.349")

    def test_one_degree(self) -> None:
        self.assertEqual(format_radian(1), "0.017")

    def test_near_full_turn(self) -> None:
        self.assertEqual(format_radian(359), "6.266")

    def test_negative_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            format_radian(-1)

    def test_float_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            format_radian(30.0)  # type: ignore[arg-type]

    def test_bool_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            format_radian(True)  # type: ignore[arg-type]


class ExactValueTest(unittest.TestCase):
    def test_thirty_degrees(self) -> None:
        self.assertEqual(exact_value(30, "cos"), "√3/2")
        self.assertEqual(exact_value(30, "sin"), "1/2")
        self.assertEqual(exact_value(30, "tan"), "√3/3")

    def test_forty_five_degrees(self) -> None:
        self.assertEqual(exact_value(45, "cos"), "√2/2")
        self.assertEqual(exact_value(45, "tan"), "1")

    def test_non_special_angle(self) -> None:
        self.assertIsNone(exact_value(20, "cos"))

    def test_tangent_missing_at_90(self) -> None:
        self.assertIsNone(exact_value(90, "tan"))
        self.assertIsNone(exact_value(270, "tan"))

    def test_function_is_case_insensitive(self) -> None:
        self.assertEqual(exact_value(45, " COS "), "√2/2")

    def test_unknown_function_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            exact_value(30, "sec")

    def test_non_text_function_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            exact_value(30, 1)  # type: ignore[arg-type]

    def test_bad_degree_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            exact_value(400, "cos")


class AngleTest(unittest.TestCase):
    def test_coordinates(self) -> None:
        expected = {
            0: (1.0, 0.0),
            30: (math.sqrt(3) / 2.0, 0.5),
            45: (math.sqrt(2) / 2.0, math.sqrt(2) / 2.0),
            60: (0.5, math.sqrt(3) / 2.0),
            90: (0.0, 1.0),
            180: (-1.0, 0.0),
            270: (0.0, -1.0),
            360: (1.0, 0.0),
        }
        for degree, (cos_value, sin_value) in expected.items():
            angle = Angle(degree)
            self.assertAlmostEqual(angle.cos_value, cos_value, places=12)
            self.assertAlmostEqual(angle.sin_value, sin_value, places=12)

    def test_coordinate_text(self) -> None:
        self.assertEqual(Angle(45).coordinate_text, "(0.7071, 0.7071)")

    def test_coordinate_text_on_axis(self) -> None:
        self.assertEqual(Angle(90).coordinate_text, "(0, 1)")
        self.assertEqual(Angle(270).coordinate_text, "(0, -1)")

    def test_quadrant_numbers(self) -> None:
        expected = {
            0: 0,
            30: 1,
            90: 0,
            120: 2,
            180: 0,
            210: 3,
            270: 0,
            300: 4,
            360: 0,
        }
        for degree, quadrant in expected.items():
            self.assertEqual(Angle(degree).quadrant, quadrant, degree)

    def test_quadrant_text(self) -> None:
        self.assertEqual(Angle(30).quadrant_text, "第一象限")
        self.assertEqual(Angle(120).quadrant_text, "第二象限")
        self.assertEqual(Angle(210).quadrant_text, "第三象限")
        self.assertEqual(Angle(300).quadrant_text, "第四象限")

    def test_axis_text(self) -> None:
        self.assertEqual(Angle(0).quadrant_text, "x 轴正半轴")
        self.assertEqual(Angle(90).quadrant_text, "y 轴正半轴")
        self.assertEqual(Angle(180).quadrant_text, "x 轴负半轴")
        self.assertEqual(Angle(270).quadrant_text, "y 轴负半轴")
        self.assertEqual(Angle(360).quadrant_text, "x 轴正半轴")

    def test_tangent_missing(self) -> None:
        self.assertIsNone(Angle(90).tan_value)
        self.assertIsNone(Angle(270).tan_value)

    def test_tangent_values(self) -> None:
        self.assertAlmostEqual(Angle(45).tan_value or 0.0, 1.0, places=12)
        self.assertAlmostEqual(Angle(135).tan_value or 0.0, -1.0, places=12)
        self.assertEqual(Angle(180).tan_text, "0")

    def test_tangent_text(self) -> None:
        self.assertEqual(Angle(90).tan_text, "不存在")
        self.assertEqual(Angle(270).tan_text, "不存在")
        self.assertEqual(Angle(30).tan_text, "0.5774")
        self.assertEqual(Angle(45).tan_text, "1")

    def test_cos_text(self) -> None:
        self.assertEqual(Angle(60).cos_text, "0.5")
        self.assertEqual(Angle(120).cos_text, "-0.5")
        self.assertEqual(Angle(90).cos_text, "0")

    def test_sin_text(self) -> None:
        self.assertEqual(Angle(30).sin_text, "0.5")
        self.assertEqual(Angle(270).sin_text, "-1")

    def test_radian_text(self) -> None:
        self.assertEqual(Angle(30).radian_text, "π/6")
        self.assertEqual(Angle(360).radian_text, "2π")
        self.assertEqual(Angle(20).radian_text, "0.349")

    def test_exact_properties(self) -> None:
        self.assertEqual(Angle(45).cos_exact, "√2/2")
        self.assertEqual(Angle(45).sin_exact, "√2/2")
        self.assertEqual(Angle(45).tan_exact, "1")
        self.assertIsNone(Angle(20).cos_exact)
        self.assertIsNone(Angle(90).tan_exact)

    def test_position(self) -> None:
        self.assertEqual(Angle(360).position, 0)
        self.assertEqual(Angle(450 % 360).position, 90)

    def test_invalid_degrees(self) -> None:
        for value in (-1, 361, 30.0, "30", True, None):
            with self.assertRaises(UnitCircleError):
                Angle(value)  # type: ignore[arg-type]


class UnitCircleTest(unittest.TestCase):
    def test_make_sorts_and_dedupes(self) -> None:
        circle = make_unit_circle([90, 0, 30, 30])
        self.assertEqual(
            [angle.degrees for angle in circle.angles], [0, 30, 90]
        )

    def test_direct_constructor_sorts_and_dedupes(self) -> None:
        circle = UnitCircle(angles=(Angle(180), Angle(0), Angle(180)))
        self.assertEqual([angle.degrees for angle in circle.angles], [0, 180])

    def test_count(self) -> None:
        self.assertEqual(make_unit_circle([0, 30, 60]).count, 3)

    def test_empty_angles_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            make_unit_circle([])

    def test_too_many_angles_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            make_unit_circle(list(range(0, 361, 15)))

    def test_title_is_trimmed(self) -> None:
        circle = make_unit_circle([0], title="  我的转盘  ")
        self.assertEqual(circle.title, "我的转盘")

    def test_empty_title_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            make_unit_circle([0], title="   ")

    def test_long_title_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            make_unit_circle([0], title="字" * 41)

    def test_non_text_title_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            make_unit_circle([0], title=1)  # type: ignore[arg-type]

    def test_non_sequence_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            make_unit_circle(30)  # type: ignore[arg-type]

    def test_string_sequence_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            make_unit_circle("0,30")  # type: ignore[arg-type]

    def test_float_angle_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            make_unit_circle([0, 30.0])  # type: ignore[list-item]

    def test_bool_angle_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            make_unit_circle([True])  # type: ignore[list-item]

    def test_non_angle_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            UnitCircle(angles=(30,))  # type: ignore[arg-type]

    def test_non_sequence_angles_rejected(self) -> None:
        with self.assertRaises(UnitCircleError):
            UnitCircle(angles=30)  # type: ignore[arg-type]

    def test_max_angles_allowed(self) -> None:
        circle = make_unit_circle(list(range(0, 360, 15)))
        self.assertEqual(circle.count, 24)


if __name__ == "__main__":
    unittest.main()
