# -*- coding: utf-8 -*-
import json
import os


import folder_paths as comfy_paths

_EMBEDDED_CONFIGURATION = {
    "debug": False,
    "paths": {
        "default_input": comfy_paths.input_directory,
        "default_output": comfy_paths.output_directory
    },
    "ui": {
        "top_category": "DVB",
        "prepend_icon_to_category": True,
        "append_icon_to_category": False,
        "prepend_icon_to_node": True,
        "append_icon_to_node": False,
        "category_icons": {
            "animation": "🎥",
            "postprocessing": "⚙",
            "transforms": "🔀",
            "curves": "📈",
            "color": "🎨",
            "generate": "⚡",
            "camera": "🎥",
            "base": "🎭",
            "utils": "🛠",
            "edit": "✂",
            "image": "🌄",
            "switches": "⭆",
            "conditioning": "☯",
            "batch": "🎞",
            "DVB": "🎭"
        }
    },

}

_config_data = None


class DVB_Config:
    FILEPATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    DEFAULT_CONFIG = _EMBEDDED_CONFIGURATION

    def __init__(self):
        global _config_data
        if not os.path.isfile(DVB_Config.FILEPATH):
            self._data = DVB_Config.DEFAULT_CONFIG
            self._save()
        if _config_data is None:
            with open(DVB_Config.FILEPATH, encoding="utf-8") as f:
                self._data = json.load(f)
                if self._merge_with_defaults(self._data, DVB_Config.DEFAULT_CONFIG):
                    self._save()
                _config_data = self._data
        else:
            self._data = _config_data

    def _save(self):
        with open(DVB_Config.FILEPATH, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def _merge_with_defaults(self, config: dict, default_config: dict) -> bool:
        changed = False
        for key in default_config.keys():
            if key not in config:
                changed = True
                config[key] = default_config[key]
            elif isinstance(default_config[key], dict):
                changed = changed or self._merge_with_defaults(config[key], default_config[key])
        return changed

    def get(self, key: str, default=None):
        key = key.split(".")
        d = self._data
        for part in key:
            d = d.get(part, {})
        if isinstance(d, dict) and not d:
            return default
        else:
            return d
