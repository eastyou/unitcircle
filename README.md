# unitcircle

[![CI](https://github.com/eastyou/unitcircle/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/unitcircle/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

面向数学课堂的单位圆三角函数转盘生成器：输入想讲的角度，一条命令生成 3 页 A4 可打印材料。**零第三方依赖，不联网，打印即用。**

第 1 页是可直接使用的单位圆盘，第 2 页是可剪下的指针与 0~360° 角度条，第 3 页是对应的三角函数值表和练习卡。特殊角同时给出精确值与 4 位小数近似值，正切不存在的位置明确标注。

## 特性

- **角度自由选**：1~24 个 0~360° 整数，支持中文逗号，自动去重并升序
- **三页成套**：单位圆转盘、可剪指针与角度条、三角函数值表 / 练习卡
- **刻度清晰**：外圈每 30° 主刻度、每 10° 次刻度，四个象限淡色区分
- **标注完整**：输入角度用不同颜色画半径，圆外标度数 + 弧度，圆内标坐标
- **精确值 + 近似值**：如 45° 的 cos 显示 `√2/2` 与 `0.7071`，30° 显示 `√3/2` 与 `0.866`
- **正切保护**：90°、270° 的 tan 显示「不存在」，不会输出无穷大
- **自包含 HTML**：CSS 与 SVG 全部内嵌，无网络资源，文本全部 HTML 转义
- **打印友好**：屏幕自适应不横向溢出；打印保持真实毫米尺寸，A4 纵向一页一版
- **132 个单元测试**：覆盖角度解析、特殊角弧度、坐标、象限、表格、转义、退出码

## 安装

```bash
pip install unitcircle
```

也可以直接下载源码，在项目目录中运行：

```bash
python -m unitcircle --help
```

## 用法

```bash
python -m unitcircle --angles 0,30,45,60,90,120,135,150,180,210,225,240,270,300,315,330 --title 单位圆转盘 -o examples/单位圆转盘.html
```

`--angles` 也可以用中文逗号：

```bash
python -m unitcircle --angles 0，30，45，60，90 -o 单位圆转盘.html
```

### 参数

| 参数 | 说明 | 默认 |
| --- | --- | --- |
| `--angles` | 逗号分隔的角度，1~24 个，每个为 0~360 的整数，支持 `，` | 16 个常用特殊角 |
| `--title` | 页面标题，1~40 个字符 | `单位圆转盘` |
| `-o, --output` | 输出 HTML 路径 | `单位圆转盘.html` |
| `--version` | 显示版本号 | — |

非法角度、空标题、超长标题等参数错误退出码为 `2`；文件写入失败退出码为 `1`；成功为 `0`。错误信息为中文，并指出第几个角度有问题。

## 打印与组装

用浏览器打开生成的 HTML，按 `Ctrl/Cmd + P`：

- 纸张：**A4 纵向**
- 边距：**无**（或默认）
- 缩放：**100%**，不要选「适应页面」
- 勾选「背景图形」，象限淡色才会打印出来

推荐使用 100% 缩放，这样 SVG 中的 `mm` 单位与纸张真实尺寸一致。

组装步骤：

1. 打印 3 页，第 1 页作为转盘底图。
2. 沿第 2 页虚线剪下指针和角度条。
3. 用图钉、回形针或按扣穿过指针中心孔与转盘轴孔。
4. 转动指针到目标角，外圈读度数与弧度，圆内读端点坐标。
5. 对照第 3 页核对 cos、sin、tan；练习时先用纸遮住右三列。

## 教学用法

- **特殊角记忆**：用 `0,30,45,60,90,120,135,150,180,210,225,240,270,300,315,330` 生成完整转盘，让学生观察弧度与角度的一一对应。
- **象限符号**：四个象限用不同淡色，配合第 3 页的 `+/-` 值，讲清「一全正、二正弦、三正切、四余弦」。
- **正切不存在**：把指针转到 90° 或 270°，表格中 tan 显示「不存在」，强化 `cos θ = 0` 的边界。
- **课堂小测**：第 3 页遮住 cos、sin、tan 三列，学生填写后对照精确值与近似值。
- **自定义角度**：只讲第一象限时用 `--angles 0,30,45,60,90`，转盘更疏朗。

## 项目结构

```text
unitcircle/
├── unitcircle/
│   ├── model.py       # 角度解析、弧度文本、三角函数值与校验
│   ├── render.py      # 三页 A4 排版、单位圆盘、指针与角度条 SVG
│   ├── cli.py         # 命令行入口与退出码
│   ├── __main__.py    # python -m unitcircle
│   └── __init__.py    # 公开 API
├── tests/             # 132 个单元测试（unittest）
├── examples/          # 示例：单位圆转盘.html
├── .github/workflows/ci.yml
├── pyproject.toml
├── LICENSE
└── README.md
```

## 开发

```bash
python -m unittest discover -s tests -v
```

生成示例：

```bash
python -m unitcircle --angles 0,30,45,60,90,120,135,150,180,210,225,240,270,300,315,330 --title 单位圆转盘 -o examples/单位圆转盘.html
```

CI 覆盖 Ubuntu / macOS / Windows × Python 3.10 / 3.13，并额外测试 Ubuntu 22.04 × Python 3.9。

## 许可证

[MIT](LICENSE) © 2026 eastyou
