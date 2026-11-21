"""单位圆转盘的数据模型：角度校验、弧度文本与三角函数值。"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

MIN_ANGLES = 1
MAX_ANGLES = 24
MIN_DEGREE = 0
MAX_DEGREE = 360
FULL_TURN = 360
RIGHT_ANGLE = 90
MAX_TITLE = 40
DEFAULT_TITLE = "单位圆转盘"
DEFAULT_ANGLES = (
    0,
    30,
    45,
    60,
    90,
    120,
    135,
    150,
    180,
    210,
    225,
    240,
    270,
    300,
    315,
    330,
)
DEFAULT_ANGLES_TEXT = ",".join(str(value) for value in DEFAULT_ANGLES)

QUADRANT_NAMES: Dict[int, str] = {
    1: "第一象限",
    2: "第二象限",
    3: "第三象限",
    4: "第四象限",
}

SPECIAL_RADIANS: Dict[int, str] = {
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

_EXACT_VALUES: Dict[str, Dict[int, str]] = {
    "cos": {
        0: "1",
        30: "√3/2",
        45: "√2/2",
        60: "1/2",
        90: "0",
        120: "-1/2",
        135: "-√2/2",
        150: "-√3/2",
        180: "-1",
        210: "-√3/2",
        225: "-√2/2",
        240: "-1/2",
        270: "0",
        300: "1/2",
        315: "√2/2",
        330: "√3/2",
        360: "1",
    },
    "sin": {
        0: "0",
        30: "1/2",
        45: "√2/2",
        60: "√3/2",
        90: "1",
        120: "√3/2",
        135: "√2/2",
        150: "1/2",
        180: "0",
        210: "-1/2",
        225: "-√2/2",
        240: "-√3/2",
        270: "-1",
        300: "-√3/2",
        315: "-√2/2",
        330: "-1/2",
        360: "0",
    },
    "tan": {
        0: "0",
        30: "√3/3",
        45: "1",
        60: "√3",
        120: "-√3",
        135: "-1",
        150: "-√3/3",
        180: "0",
        210: "√3/3",
        225: "1",
        240: "√3",
        300: "-√3",
        315: "-1",
        330: "-√3/3",
        360: "0",
    },
}


class UnitCircleError(ValueError):
    """角度、标题或渲染参数不合法。"""


def _require_degree(value: object, name: str = "角度") -> int:
    """校验角度是否为 0~360 的整数，拒绝布尔值。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise UnitCircleError("%s必须是整数" % name)
    if not MIN_DEGREE <= value <= MAX_DEGREE:
        raise UnitCircleError(
            "%s必须在 %d~%d 之间，当前是 %d"
            % (name, MIN_DEGREE, MAX_DEGREE, value)
        )
    return value


def format_decimal(value: float, digits: int = 4) -> str:
    """保留指定小数位并去掉末尾的零，-0 统一写成 0。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise UnitCircleError("数值必须是数字")
    if isinstance(digits, bool) or not isinstance(digits, int):
        raise UnitCircleError("小数位数必须是整数")
    if not 0 <= digits <= 8:
        raise UnitCircleError("小数位数必须在 0~8 之间")
    number = float(value)
    if not math.isfinite(number):
        raise UnitCircleError("数值必须是有限数")
    text = ("%." + str(digits) + "f") % number
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in ("-0", ""):
        text = "0"
    return text


def format_radian(degrees: int) -> str:
    """把角度转成弧度文本：特殊角用 π 形式，其余保留 3 位小数。"""
    degree = _require_degree(degrees)
    special = SPECIAL_RADIANS.get(degree)
    if special is not None:
        return special
    return format_decimal(math.radians(degree), 3)


def exact_value(degrees: int, function: str) -> Optional[str]:
    """返回特殊角的精确三角值文本；非特殊角返回 None。"""
    degree = _require_degree(degrees)
    if not isinstance(function, str):
        raise UnitCircleError("函数名必须是文本")
    key = function.strip().lower()
    if key not in _EXACT_VALUES:
        raise UnitCircleError("函数名必须是 cos、sin 或 tan")
    return _EXACT_VALUES[key].get(degree)


@dataclass(frozen=True)
class Angle:
    """单位圆上的一个角度及其三角函数值。"""

    degrees: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "degrees", _require_degree(self.degrees))

    @property
    def radians(self) -> float:
        """角度对应的弧度数值。"""
        return math.radians(self.degrees)

    @property
    def position(self) -> int:
        """等效的 0~359 度位置，360° 与 0° 重合。"""
        return self.degrees % FULL_TURN

    @property
    def cos_value(self) -> float:
        """余弦值。"""
        return math.cos(self.radians)

    @property
    def sin_value(self) -> float:
        """正弦值。"""
        return math.sin(self.radians)

    @property
    def tan_value(self) -> Optional[float]:
        """正切值；90°、270° 等处不存在，返回 None。"""
        if self.degrees % 180 == RIGHT_ANGLE:
            return None
        return math.tan(self.radians)

    @property
    def radian_text(self) -> str:
        """弧度展示文本，例如 30° 显示 π/6。"""
        return format_radian(self.degrees)

    @property
    def cos_text(self) -> str:
        """余弦数值文本，保留 4 位小数并去尾零。"""
        return format_decimal(self.cos_value, 4)

    @property
    def sin_text(self) -> str:
        """正弦数值文本，保留 4 位小数并去尾零。"""
        return format_decimal(self.sin_value, 4)

    @property
    def tan_text(self) -> str:
        """正切数值文本；不存在时返回中文提示。"""
        value = self.tan_value
        if value is None:
            return "不存在"
        return format_decimal(value, 4)

    @property
    def cos_exact(self) -> Optional[str]:
        """余弦的精确值文本，非特殊角为 None。"""
        return exact_value(self.degrees, "cos")

    @property
    def sin_exact(self) -> Optional[str]:
        """正弦的精确值文本，非特殊角为 None。"""
        return exact_value(self.degrees, "sin")

    @property
    def tan_exact(self) -> Optional[str]:
        """正切的精确值文本，非特殊角或不存在时为 None。"""
        return exact_value(self.degrees, "tan")

    @property
    def quadrant(self) -> int:
        """象限编号 1~4；落在坐标轴上时返回 0。"""
        position = self.position
        if position % RIGHT_ANGLE == 0:
            return 0
        if position < RIGHT_ANGLE:
            return 1
        if position < 180:
            return 2
        if position < 270:
            return 3
        return 4

    @property
    def quadrant_text(self) -> str:
        """象限或坐标轴的中文说明。"""
        quadrant = self.quadrant
        if quadrant:
            return QUADRANT_NAMES[quadrant]
        position = self.position
        if position == 0:
            return "x 轴正半轴"
        if position == 90:
            return "y 轴正半轴"
        if position == 180:
            return "x 轴负半轴"
        return "y 轴负半轴"

    @property
    def coordinate_text(self) -> str:
        """单位圆端点坐标，保留 4 位小数。"""
        return "(%s, %s)" % (
            format_decimal(self.cos_value, 4),
            format_decimal(self.sin_value, 4),
        )


def parse_angles(text: str) -> Tuple[int, ...]:
    """解析逗号分隔的角度，支持中文逗号，自动去重并升序。"""
    if not isinstance(text, str):
        raise UnitCircleError("角度列表必须是文本")
    cleaned = text.strip().replace("，", ",")
    if not cleaned:
        raise UnitCircleError("角度列表不能为空，例如：0,30,45,90")
    values: List[int] = []
    for index, token in enumerate(cleaned.split(","), start=1):
        item = token.strip()
        if not item:
            raise UnitCircleError("第 %d 个角度为空，请检查逗号" % index)
        if not item.isascii() or not item.isdigit():
            raise UnitCircleError(
                "第 %d 个角度「%s」不是 0~360 的整数" % (index, item)
            )
        degree = int(item)
        if not MIN_DEGREE <= degree <= MAX_DEGREE:
            raise UnitCircleError(
                "第 %d 个角度「%s」超出 0~360 的范围" % (index, item)
            )
        values.append(degree)
    unique = sorted(set(values))
    if not MIN_ANGLES <= len(unique) <= MAX_ANGLES:
        raise UnitCircleError(
            "角度数量必须在 %d~%d 个之间，当前有 %d 个"
            % (MIN_ANGLES, MAX_ANGLES, len(unique))
        )
    return tuple(unique)


def make_unit_circle(
    degrees: Sequence[int], title: str = DEFAULT_TITLE
) -> UnitCircle:
    """由角度整数序列构造单位圆，自动去重并升序。"""
    if isinstance(degrees, (str, bytes)) or not isinstance(
        degrees, (list, tuple)
    ):
        raise UnitCircleError("角度必须是整数序列，例如 [0, 30, 45]")
    angles: List[Angle] = []
    for value in degrees:
        if isinstance(value, bool) or not isinstance(value, int):
            raise UnitCircleError("角度必须是 0~360 的整数")
        angles.append(Angle(value))
    return UnitCircle(angles=tuple(angles), title=title)


@dataclass(frozen=True)
class UnitCircle:
    """一张单位圆转盘：角度集合与页面标题。"""

    angles: Tuple[Angle, ...]
    title: str = DEFAULT_TITLE

    def __post_init__(self) -> None:
        try:
            angles = tuple(self.angles)
        except TypeError as exc:
            raise UnitCircleError("angles 必须是 Angle 序列") from exc
        cleaned: List[Angle] = []
        seen: Dict[int, None] = {}
        for angle in angles:
            if not isinstance(angle, Angle):
                raise UnitCircleError("angles 中只能放 Angle 对象")
            if angle.degrees in seen:
                continue
            seen[angle.degrees] = None
            cleaned.append(angle)
        cleaned.sort(key=lambda item: item.degrees)
        if not MIN_ANGLES <= len(cleaned) <= MAX_ANGLES:
            raise UnitCircleError(
                "角度数量必须在 %d~%d 个之间，当前有 %d 个"
                % (MIN_ANGLES, MAX_ANGLES, len(cleaned))
            )
        if not isinstance(self.title, str):
            raise UnitCircleError("标题必须是文本")
        title = self.title.strip()
        if not title:
            raise UnitCircleError("标题不能为空")
        if len(title) > MAX_TITLE:
            raise UnitCircleError("标题最多 %d 个字符" % MAX_TITLE)
        object.__setattr__(self, "angles", tuple(cleaned))
        object.__setattr__(self, "title", title)

    @property
    def count(self) -> int:
        """角度数量。"""
        return len(self.angles)
