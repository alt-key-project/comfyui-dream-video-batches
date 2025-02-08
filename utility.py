# -*- coding: utf-8 -*-
import math
import os

import folder_paths as comfy_paths
import glob

from .categories import NodeCategories
from .core import *


class DVB_IntToString:
    NODE_NAME = "Int To String"
    ICON = "🔨"
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "convert"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("INT", {"default": 0}),
            }
        }

    def convert(self, value, **values):
        return (str(value),)


class DVB_FloatToString:
    NODE_NAME = "Float To String"
    ICON = "🔨"
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "convert"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {"default": 0.0, "step": "0.01"}),
            }
        }

    def convert(self, value, **values):
        return (str(value),)


class DVB_StringBuilder:
    NODE_NAME = "String Builder"
    ICON = "🖹"
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "build"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": ""}),
            },
            "optional": {
                "A": ("STRING", {"default": ""}),
                "B": ("STRING", {"default": ""})
            }
        }

    def build(self, text: str, **values):
        A = values.get("A", "")
        B = values.get("B", "")
        return (text.replace("$A", A).replace("$B", B),)


_ID_SELETIONS = list(
    sorted(["apple", "banana", "grape", "melon", "orange", "pear", "fish", "dog", "cat", "chicken", "book",
            "car", "tree", "moon", "sun", "cloud", "lemon", "cow", "horse", "duck", "eagle", "rock"]))


class DVB_ForEachFilename:
    NODE_NAME = "For Each Filename"
    ICON = "🗘"
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("STRING", "STRING", "FOREACH")
    RETURN_NAMES = ("filepath", "name", "foreach")
    FUNCTION = "exec"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "id": (_ID_SELETIONS,),
                "directory": ("STRING", {"default": comfy_paths.input_directory}),
                "pattern": ("STRING", {"default": "*.jpg"})
            },
        }

    def exec(self, id: str, directory: str, pattern: str):
        directory = directory.strip('"')
        if not os.path.isdir(directory):
            on_node_error(DVB_ForEachFilename, "Not a directory: {}".format(directory))

        foreach_filename = "foreach_" + id + ".json"

        statefile = os.path.normpath(os.path.abspath(os.path.join(directory, "foreach_" + id + ".json")))
        search_path = os.path.normpath(os.path.abspath(directory))
        state = ForEachState(statefile)

        files = list(filter(lambda f: f != foreach_filename, glob.glob(os.path.join(search_path, pattern), recursive=False)))
        state.add_files_to_process(files)

        next_path = state.pop()
        if next_path is None:
            os.unlink(statefile)
            on_node_error(DVB_ForEachFilename, "No more files to process.")
        name, _ = os.path.splitext(os.path.basename(next_path))
        return (next_path, name, statefile)


class DVB_FrameSetDimensionsScaled:
    NODE_NAME = "Frame Set Frame Dimensions Scaled"
    ICON = "⌗"
    OUTPUT_NODE = False
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "exec"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "factor": ("FLOAT", {"default": 1.0, "min": 0.01})
            }
        }

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def exec(self, frames :FrameSet, factor : float):
        d = frames.image_dimensions

        return (round(d[0] * factor),round(d[1] * factor))


class DVB_ForEachCheckpoint:
    NODE_NAME = "For Each Done"
    ICON = "🗘"
    OUTPUT_NODE = True
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = tuple()
    RETURN_NAMES = tuple()
    FUNCTION = "exec"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "foreach": ("FOREACH",),
            }
        }

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def exec(self, image, foreach):
        state = ForEachState(foreach)
        next_file = state.pop()
        state.mark_done(next_file)
        return tuple()


class DVB_StringTokenizer:
    NODE_NAME = "String Tokenizer"
    ICON = "🪙"
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("token",)
    FUNCTION = "exec"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "separator": ("STRING", {"default": ","}),
                "selected": ("INT", {"default": 0, "min": 0})
            },
        }

    def exec(self, text: str, separator: str, selected: int):
        if separator is None or separator == "":
            separator = " "
        parts = text.split(sep=separator)
        return (parts[abs(selected) % len(parts)].strip(),)


def _align_num(n: int, alignment: int, type: str):
    if alignment <= 1:
        return n
    if type == "ceil":
        return int(math.ceil(float(n) / alignment)) * alignment
    elif type == "floor":
        return int(math.floor(float(n) / alignment)) * alignment
    else:
        return int(round(float(n) / alignment)) * alignment


class DVB_FrameDimensions:
    NODE_NAME = "Common Frame Dimensions"
    ICON = "⌗"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "size": (["3840", "1920", "1440", "1280", "768", "720", "640", "512"],),
                "aspect_ratio": (["16:9", "16:10", "4:3", "1:1", "5:4", "3:2", "21:9", "14:9"],),
                "orientation": (["wide", "tall"],),
                "divisor": (["8", "4", "2", "1"],),
                "alignment": ("INT", {"default": 64, "min": 1, "max": 512}),
                "alignment_type": (["ceil", "floor", "nearest"],),
            },
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("INT", "INT", "INT", "INT")
    RETURN_NAMES = ("width", "height", "final_width", "final_height")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, size, aspect_ratio, orientation, divisor, alignment, alignment_type):
        ratio = tuple(map(int, aspect_ratio.split(":")))
        final_width = int(size)
        final_height = int(round((float(final_width) * ratio[1]) / ratio[0]))
        width = _align_num(int(round(final_width / float(divisor))), alignment, alignment_type)
        height = _align_num(int(round((float(width) * ratio[1]) / ratio[0])), alignment, alignment_type)
        if orientation == "wide":
            return (width, height, final_width, final_height)
        else:
            return (height, width, final_height, final_width)


class DVB_TraceMalloc:
    NODE_NAME = "Trace Memory Allocation"
    ICON = "⌗"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"default": ""}),
            }
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, string):
        import tracemalloc, gc

        print("!! Forcing GC")
        gc_comfyui()
        gc.collect()
        if not tracemalloc.is_tracing():
            print("!! TRACEMALLOC INIT")
            tracemalloc.start()
        else:
            print("!! TRACEMALLOC RUNNING")

        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        for stat in top_stats[:10]:
            print("!! TRACEMALLOC: " + str(stat))
        return (string,)
