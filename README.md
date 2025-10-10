# 图片加水印工具 (Photo Watermark Tool)

这是一个基于本地桌面的 Windows 图形化应用，用于批量给图片添加水印（文本或图片）。项目以简洁高效为目标，支持模板保存、实时预览、位置拖拽与批量导出。

## 主要功能概览

- 批量导入图片（单张/多张/文件夹）并在左侧列表显示缩略图与文件名。
- 文本水印：可输入文字、选择字号（按图片尺寸相对设置）、颜色、透明度、加粗/斜体。
- 图片水印：支持带透明通道的 PNG，支持缩放与透明度调节。
- 水印位置：提供 9 宫格常用位置预设（四角/四边中点/中心），并支持在预览区域拖拽微调偏移量。
- 模板管理：可保存/加载/删除水印设置模板，程序启动可载入上次会话设置。
- 导出：支持 PNG/JPEG 输出，支持命名规则（保留原名/前缀/后缀）、JPEG 质量调整、导出尺寸缩放和批量导出。

这些需求来自 `PRD.md`，并在代码层由 `ui/`、`watermark/` 与 `file_manager`/`config_manager` 等模块实现。

## 快速开始

先决条件：Windows（建议 Windows 10 及以上），Python 3.8+。

1. 创建并激活虚拟环境（可选但推荐）：

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. 安装依赖（项目根 `requirements.txt` 当前为空；至少需要安装 Pillow 与 PyQt6）：

```powershell
pip install pillow pyqt6
```

3. 运行主程序（在项目根目录）：

```powershell
python -m ui.main_window
```

说明：主窗口入口为 `ui/main_window.py`，程序使用 PyQt6 实现界面，`watermark` 包实现水印生成逻辑，`file_manager` 负责文件导入/导出，`config_manager` 负责模板持久化。

## 代码结构

- `ui/`
  - `main_window.py` — 主窗口与交互逻辑（应用入口）
  - `controls.py` — 控件集合（文本输入、滑块、按钮、模板下拉等）
  - `image_list.py` — 左侧图片列表组件
  - `preview_widget.py` — 预览组件（显示 PIL -> Qt 的图片，并响应拖拽）

- `watermark/`
  - `watermark_text.py` — 文本水印实现（字号按图片尺寸比例、字体加载/回退、粗体/斜体/描边/阴影处理）
  - `watermark_image.py` — 图片水印实现（可缩放、调整透明度、按中心点粘贴）
  - `file_manager.py` — 文件导入/导出逻辑（支持批量导出、命名规则、JPEG 质量、缩放）
  - `config_manager.py` — 模板的保存/加载/列举/删除（JSON 存储在 `templates/`）
  - `preview.py` — 预览管理（将文本/图片水印组合到预览图片上）

- `assets/` — 放置默认 logo、图标等资源（例如 `assets/logo.png`）
- `templates/` — 模板存放目录（JSON）
- `test/` — 简单的功能测试脚本
- `test_inputs/`, `test_outputs/` — 测试输入/输出目录

## 已打包发行版（dist）

项目根目录下包含一个 `dist/` 目录，包含已打包的 Windows 可执行文件（exe）以及必要的运行时资源，双击运行即可。