"""unitcircle：A4 可打印的单位圆三角函数转盘。"""

from __future__ import annotations

from .model import (
    DEFAULT_ANGLES,
    DEFAULT_ANGLES_TEXT,
    DEFAULT_TITLE,
    FULL_TURN,
    MAX_ANGLES,
    MAX_DEGREE,
    MAX_TITLE,
    MIN_ANGLES,
    MIN_DEGREE,
    QUADRANT_NAMES,
    SPECIAL_RADIANS,
    Angle,
    UnitCircle,
    UnitCircleError,
    exact_value,
    format_decimal,
    format_radian,
    make_unit_circle,
    parse_angles,
)
from .render import (
    PAGE_COUNT,
    angle_color,
    render_angle_strip_svg,
    render_disk_svg,
    render_html,
    render_pointer_svg,
)

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_ANGLES",
    "DEFAULT_ANGLES_TEXT",
    "DEFAULT_TITLE",
    "FULL_TURN",
    "MAX_ANGLES",
    "MAX_DEGREE",
    "MAX_TITLE",
    "MIN_ANGLES",
    "MIN_DEGREE",
    "PAGE_COUNT",
    "QUADRANT_NAMES",
    "SPECIAL_RADIANS",
    "Angle",
    "UnitCircle",
    "UnitCircleError",
    "angle_color",
    "exact_value",
    "format_decimal",
    "format_radian",
    "make_unit_circle",
    "parse_angles",
    "render_angle_strip_svg",
    "render_disk_svg",
    "render_html",
    "render_pointer_svg",
    "__version__",
]
