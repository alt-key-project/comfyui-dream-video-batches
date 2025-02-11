from .categories import *
from .core import *

class DVB_InputText:
    NODE_NAME = "Text Input"
    ICON = "✍"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("STRING", {"default": "", "multiline": True}),
            },
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "noop"

    @classmethod
    def IS_CHANGED(cls, *values, **kwargs):
        return hashed_as_strings(*values, **kwargs)

    def noop(self, value):
        return (value,)


class DVB_InputString:
    NODE_NAME = "String Input"
    ICON = "✍"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("STRING", {"default": "", "multiline": False}),
            },
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "noop"

    @classmethod
    def IS_CHANGED(cls, *values, **kwargs):
        return hashed_as_strings(*values, **kwargs)

    def noop(self, value):
        return (value,)


class DVB_InputFloat:
    NODE_NAME = "Float Input"
    ICON = "✍"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {"default": 0.0}),
            },
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("FLOAT",)
    FUNCTION = "noop"

    @classmethod
    def IS_CHANGED(cls, *values, **kwargs):
        return hashed_as_strings(*values, **kwargs)

    def noop(self, value):
        return (value,)


class DVB_InputInt:
    NODE_NAME = "Int Input"
    ICON = "✍"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("INT", {"default": 0}),
            },
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("INT",)
    FUNCTION = "noop"

    @classmethod
    def IS_CHANGED(cls, *values, **kwargs):
        return hashed_as_strings(*values, **kwargs)

    def noop(self, value):
        return (value,)

