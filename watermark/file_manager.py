# watermark/file_manager.py
import os
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image


class FileManager:
    SUPPORTED_INPUT_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
    SUPPORTED_OUTPUT_FORMATS = ["JPEG", "PNG"]

    def __init__(self):
        self.imported_files: List[Path] = []

    # ------------------------------
    # 导入功能
    # ------------------------------
    def import_files(self, file_paths: List[str]) -> List[Path]:
        """导入单张或多张图片，返回有效文件路径列表"""
        valid_files = []
        for f in file_paths:
            p = Path(f)
            if p.suffix.lower() in self.SUPPORTED_INPUT_FORMATS and p.exists():
                valid_files.append(p)
        self.imported_files.extend(valid_files)
        return valid_files

    def import_folder(self, folder_path: str) -> List[Path]:
        """导入整个文件夹中的图片"""
        folder = Path(folder_path)
        if not folder.is_dir():
            return []
        valid_files = [f for f in folder.iterdir() if f.suffix.lower() in self.SUPPORTED_INPUT_FORMATS]
        self.imported_files.extend(valid_files)
        return valid_files

    def get_imported_files(self) -> List[Path]:
        """返回当前已导入的文件列表"""
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
        scale_percent: float = 1.0
    ) -> Path:
        """
        导出单张图片
        :param img: PIL.Image
        :param original_path: 原图路径
        :param output_dir: 导出目录
        :param output_format: "JPEG" 或 "PNG"
        :param name_rule: "original"/"prefix"/"suffix"
        :param custom_str: 前/后缀字符串
        :param jpeg_quality: JPEG质量
        :param scale_percent: 缩放比例（0.1 ~ 5.0）
        """
        if output_format not in self.SUPPORTED_OUTPUT_FORMATS:
            raise ValueError(f"不支持的导出格式: {output_format}")

        # 缩放图片
        if scale_percent != 1.0:
            new_size = (int(img.width * scale_percent), int(img.height * scale_percent))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # 处理输出目录
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 文件名处理
        stem = original_path.stem
        if name_rule == "prefix":
            new_name = f"{custom_str}{stem}"
        elif name_rule == "suffix":
            new_name = f"{stem}{custom_str}"
        else:
            new_name = stem

        ext = ".jpg" if output_format == "JPEG" else ".png"
        output_path = output_dir / f"{new_name}{ext}"

        # 防止覆盖原文件
        if output_path.resolve().parent == original_path.parent:
            raise ValueError("禁止导出到原文件夹！")

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
        scale_percent: float = 1.0
    ) -> List[Path]:
        """
        批量导出
        :param images: [(PIL.Image, Path), ...]
        :return: 导出路径列表
        """
        exported_files = []
        for img, original_path in images:
            try:
                out_path = self.export_image(
                    img,
                    original_path,
                    output_dir,
                    output_format,
                    name_rule,
                    custom_str,
                    jpeg_quality,
                    scale_percent
                )
                exported_files.append(out_path)
            except Exception as e:
                print(f"[WARN] 导出失败 {original_path}: {e}")
        return exported_files
