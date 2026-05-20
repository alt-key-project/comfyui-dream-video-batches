# -*- coding: utf-8 -*-
import os
import hashlib

from .categories import NodeCategories
from .core import on_node_error


class DVB_LoadTextFromPath:
    NODE_NAME = "Load Text From Path"
    ICON = "📄"
    CATEGORY = NodeCategories.IO
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "result"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_path": ("STRING", {"default": '', "multiline": False}),
                "encoding": (["utf-8", "utf-16", "ascii", "utf-8-sig", "latin-1"], {"default": "utf-8"})
            }
        }

    @classmethod
    def IS_CHANGED(cls, text_path, encoding, **kwargs):
        if not text_path or not os.path.exists(text_path) or os.path.isdir(text_path):
            return ""
        m = hashlib.sha256()
        with open(text_path, "rb") as f:
            m.update(f.read())
        return m.digest().hex()

    def result(self, text_path, encoding, **other):
        if not text_path:
            return ("",)
        if not os.path.exists(text_path):
            on_node_error(DVB_LoadTextFromPath, "Path does not exist: " + text_path)
        if os.path.isdir(text_path):
            on_node_error(DVB_LoadTextFromPath, "Path is a directory, not a file: " + text_path)
        with open(text_path, "r", encoding=encoding) as f:
            return (f.read(),)
