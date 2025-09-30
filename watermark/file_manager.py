# watermark/file_manager.py
import os
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image


class FileManager:
    SUPPORTED_INPUT_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
    SUPPORTED_OUTPUT_FORMATS = ["JPEG", "PNG"]

    def __init__(self):
        # 已导入的图片路径列表
        self.imported_files: List[Path] = []

    # ------------------------------
    # 导入功能
    # ------------------------------
    def import_files(self, file_paths: List[str]) -> List[Path]:
        """
        导入单张或多张图片，返回有效文件路径列表
        """
        valid_files = []
        for f in file_paths:
            p = Path(f)
            if p.suffix.lower() in self.SUPPORTED_INPUT_FORMATS and p.exists():
                valid_files.append(p)
        self.imported_files.extend(valid_files)
        return valid_files

    def import_folder(self, folder_path: str) -> List[Path]:
        """
        导入整个文件夹中的图片
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            return []
        valid_files = [
            f for f in folder.iterdir()
            if f.suffix.lower() in self.SUPPORTED_INPUT_FORMATS
        ]
        self.imported_files.extend(valid_files)
        return valid_files

    def get_imported_files(self) -> List[Path]:
        """
        返回当前已导入的文件列表
        """
        return self.imported_files

    # ------------------------------
    # 导出功能
    # ------------------------------
    def export_image(
        self,
        img: Image.Image,
        original_path: Path,
        output_dir: str,
        output_format: str = "PNG",
        name_rule: str = "suffix",
        custom_str: str = "_watermarked",
        jpeg_quality: int = 90,
        resize: Optional[Tuple[int, int]] = None,
    ) -> Path:
        """
        导出单张图片
        :param img: 需要保存的 PIL.Image
        :param original_path: 原图路径
        :param output_dir: 导出文件夹
        :param output_format: "JPEG" 或 "PNG"
        :param name_rule: 命名规则 ("original", "prefix", "suffix")
        :param custom_str: 前缀或后缀字符串
        :param jpeg_quality: JPEG 质量（0-100）
        :param resize: 可选尺寸 (width, height)
        :return: 导出文件路径
        """
        if output_format not in self.SUPPORTED_OUTPUT_FORMATS:
            raise ValueError(f"不支持的导出格式: {output_format}")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 文件名处理
        stem = original_path.stem
        if name_rule == "prefix":
            new_name = f"{custom_str}{stem}"
        elif name_rule == "suffix":
            new_name = f"{stem}{custom_str}"
        else:  # 保留原名
            new_name = stem

        ext = ".jpg" if output_format == "JPEG" else ".png"
        output_path = output_dir / f"{new_name}{ext}"

        # 防止覆盖原图（如果导出目录和原图目录相同）
        if output_path.resolve().parent == original_path.parent:
            raise ValueError("禁止导出到原文件夹！")

        # 调整尺寸
        if resize:
            img = img.resize(resize, Image.Resampling.LANCZOS)

        # 保存
        save_params = {}
        if output_format == "JPEG":
            save_params["quality"] = jpeg_quality

        img.save(output_path, output_format, **save_params)
        return output_path

    def batch_export(
        self,
        images: List[Tuple[Image.Image, Path]],
        output_dir: str,
        output_format: str = "PNG",
        name_rule: str = "suffix",
        custom_str: str = "_watermarked",
        jpeg_quality: int = 90,
        resize: Optional[Tuple[int, int]] = None,
    ) -> List[Path]:
        """
        批量导出
        :param images: [(PIL.Image, 原图Path), ...]
        :return: 导出的文件路径列表
        """
        exported_paths = []
        for img, path in images:
            try:
                out = self.export_image(
                    img,
                    original_path=path,
                    output_dir=output_dir,
                    output_format=output_format,
                    name_rule=name_rule,
                    custom_str=custom_str,
                    jpeg_quality=jpeg_quality,
                    resize=resize,
                )
                exported_paths.append(out)
            except Exception as e:
                print(f"导出失败 {path}: {e}")
        return exported_paths
