# watermark/config_manager.py
import json
from pathlib import Path
from typing import Dict, Any, List


class ConfigManager:
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def save_template(self, name: str, config: Dict[str, Any]):
        """保存模板，config 是水印参数字典"""
        template_path = self.template_dir / f"{name}.json"
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"[OK] 模板已保存: {template_path}")

    def load_template(self, name: str) -> Dict[str, Any]:
        """加载模板，返回水印参数字典"""
        template_path = self.template_dir / f"{name}.json"
        if not template_path.exists():
            raise FileNotFoundError(f"模板不存在: {name}")
        with open(template_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config

    def list_templates(self) -> List[str]:
        """列出所有模板名称（不带 .json 后缀）"""
        return [f.stem for f in self.template_dir.glob("*.json")]

    def delete_template(self, name: str):
        """删除模板"""
        template_path = self.template_dir / f"{name}.json"
        if template_path.exists():
            template_path.unlink()
            print(f"[OK] 模板已删除: {name}")
        else:
            print(f"[WARN] 模板不存在: {name}")
