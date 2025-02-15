# -*- coding: utf-8 -*-
import os
import hashlib

from .categories import NodeCategories
from .core import *


class DVB_LoadImageFromPath:
    NODE_NAME = "Load Image From Path"
    CATEGORY = NodeCategories.IO
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "result"
    ICON = "🖼"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_path": ("STRING", {"default": '', "multiline": False}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, *values, **kwargs):
        image_path = kwargs.get("image_path", "None")
        if (not image_path) or (not os.path.isfile(image_path)):
            return ""
        m = hashlib.sha256()
        with open(image_path, "rb") as f:
            m.update(f.read())
        return m.digest().hex()

    def result(self, image_path, **other):
        return (DVB_Image.join_to_tensor_data([DVB_Image(file_path=image_path, with_alpha=True)]),)

