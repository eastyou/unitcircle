"""命令行入口单元测试：参数校验、退出码与生成结果。"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from typing import List, Tuple

from unitcircle.cli import main

ARGS = "0,30,45,60,90,120,135,150,180,210,225,240,270,300,315,330"


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.target = self.root / "unitcircle.html"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cli(self, argv: List[str]) -> Tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_generate_default(self) -> None:
        code, out, _ = self.run_cli(["-o", str(self.target)])
        self.assertEqual(code, 0)
        self.assertTrue(self.target.exists())
        page = self.target.read_text(encoding="utf-8")
        self.assertEqual(page.count("<section"), 3)
        self.assertIn("3 页", out)

    def test_generate_custom_angles(self) -> None:
        code, _, _ = self.run_cli(
            ["--angles", ARGS, "--title", "单位圆转盘", "-o", str(self.target)]
        )
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertEqual(page.count("<tr>"), 17)
        self.assertIn("单位圆转盘", page)

    def test_chinese_comma(self) -> None:
        code, _, _ = self.run_cli(
            ["--angles", "0，30，45", "-o", str(self.target)]
        )
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertEqual(page.count("<tr>"), 4)

    def test_dedupe_and_sort(self) -> None:
        code, _, _ = self.run_cli(
            ["--angles", "90,0,90,30,0", "-o", str(self.target)]
        )
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertEqual(page.count("<tr>"), 4)

    def test_invalid_angle_exit_code(self) -> None:
        code, _, err = self.run_cli(
            ["--angles", "0,abc", "-o", str(self.target)]
        )
        self.assertEqual(code, 2)
        self.assertIn("错误", err)
        self.assertIn("abc", err)
        self.assertFalse(self.target.exists())

    def test_too_many_angles_exit_code(self) -> None:
        angles = ",".join(str(value) for value in range(0, 361, 15))
        code, _, err = self.run_cli(["--angles", angles, "-o", str(self.target)])
        self.assertEqual(code, 2)
        self.assertIn("1~24", err)

    def test_long_title_exit_code(self) -> None:
        code, _, err = self.run_cli(
            ["--title", "字" * 41, "-o", str(self.target)]
        )
        self.assertEqual(code, 2)
        self.assertIn("40", err)

    def test_missing_output_directory(self) -> None:
        target = self.root / "missing" / "unitcircle.html"
        code, _, err = self.run_cli(["-o", str(target)])
        self.assertEqual(code, 1)
        self.assertIn("写入文件失败", err)

    def test_output_is_directory(self) -> None:
        directory = self.root / "folder"
        directory.mkdir()
        code, _, err = self.run_cli(["-o", str(directory)])
        self.assertEqual(code, 1)
        self.assertIn("写入文件失败", err)

    def test_help_exit_code(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stdout(io.StringIO()):
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_version_exit_code(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stdout(io.StringIO()):
                main(["--version"])
        self.assertEqual(ctx.exception.code, 0)

    def test_missing_option_value(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(io.StringIO()):
                main(["--angles"])
        self.assertEqual(ctx.exception.code, 2)

    def test_title_is_escaped(self) -> None:
        code, _, _ = self.run_cli(
            ["--angles", "0,45", "--title", "<转盘>", "-o", str(self.target)]
        )
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertIn("&lt;转盘&gt;", page)
        self.assertNotIn("<h1><转盘>", page)

    def test_success_message(self) -> None:
        code, out, _ = self.run_cli(
            ["--angles", "0,45,90", "-o", str(self.target)]
        )
        self.assertEqual(code, 0)
        self.assertIn("3 个角度", out)
        self.assertIn("A4 纵向", out)

    def test_three_page_html(self) -> None:
        code, _, _ = self.run_cli(["-o", str(self.target)])
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        for text in ("三角函数值表", "指针", "角度条", "A4 portrait"):
            self.assertIn(text, page)


if __name__ == "__main__":
    unittest.main()
