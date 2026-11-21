"""命令行入口：生成 A4 可打印的单位圆三角函数转盘。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .model import (
    DEFAULT_ANGLES_TEXT,
    DEFAULT_TITLE,
    UnitCircle,
    UnitCircleError,
    make_unit_circle,
    parse_angles,
)
from .render import PAGE_COUNT, render_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="unitcircle",
        description="单位圆转盘：输入角度，一键生成 A4 可打印三角函数转盘与练习卡",
    )
    parser.add_argument("--version", action="version", version="unitcircle 0.1.0")
    parser.add_argument(
        "--angles",
        default=DEFAULT_ANGLES_TEXT,
        help="逗号分隔的角度，1~24 个，取值 0~360，支持中文逗号",
    )
    parser.add_argument(
        "--title", default=DEFAULT_TITLE, help="页面标题，1~40 个字符"
    )
    parser.add_argument(
        "-o", "--output", default="单位圆转盘.html", help="输出 HTML 路径"
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        degrees = parse_angles(args.angles)
        circle: UnitCircle = make_unit_circle(degrees, title=args.title)
        page = render_html(circle)
    except UnitCircleError as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2

    try:
        Path(args.output).write_text(page, encoding="utf-8")
    except OSError as exc:
        print("错误: 写入文件失败: %s" % exc, file=sys.stderr)
        return 1

    print(
        "已生成 %s：%d 个角度，共 %d 页"
        % (args.output, circle.count, PAGE_COUNT)
    )
    print("用浏览器打开后按 Ctrl/Cmd + P，纸张选 A4 纵向、边距无即可打印")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
