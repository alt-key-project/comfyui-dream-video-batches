# -*- coding: utf-8 -*-

from .categories import *
from .core import *


class DVB_MergeFrames:
    NODE_NAME = "Frame Set Merger"
    ICON = "🗍"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "a": (FrameSet.TYPE_NAME,),
                "b": (FrameSet.TYPE_NAME,),
                "priority": (["use_a_when_possible", "use_b_when_possible"],)
            },
        }

    CATEGORY = NodeCategories.BATCH
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, a: FrameSet, b: FrameSet, priority: str):
        if priority == "use_b_when_possible":
            t = a
            a = b
            b = t
        if a.framerate != b.framerate:
            on_node_error(DVB_MergeFrames,
                          "Frame sets have different framerate {} and {} - cannot merge!".format(a.framerate,
                                                                                                 b.framerate))
        return (a.merge(b),)


class DVB_Splitter:
    NODE_NAME = "Frame Set Splitter"
    ICON = "✂"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "overlap": ("INT", {"default": 0, "min": 0})
            },
        }

    CATEGORY = NodeCategories.BATCH
    RETURN_TYPES = (FrameSet.TYPE_NAME, FrameSet.TYPE_NAME)
    RETURN_NAMES = ("first_half", "second_half")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frames: FrameSet, overlap: int):
        images = frames.indexed_images
        n = len(images) // 2
        first_half = images[0:n]
        second_half = images[n:]
        first_half_overlap = min(len(second_half), overlap // 2)
        second_half_overlap = min(len(first_half), overlap - first_half_overlap)
        first_half_extra = list()
        second_half_extra = list()
        for i in range(first_half_overlap):
            first_half_extra.append(second_half[i])
        for i in range(second_half_overlap):
            second_half_extra.insert(0, first_half[-(n + 1)])
        first_half = first_half + first_half_extra
        second_half = second_half_extra + second_half
        print("Split {} into {} + {} (overlap {})".format(len(images), len(first_half), len(second_half), overlap))
        return (FrameSet.from_indexed_images(first_half, frames.framerate),
                FrameSet.from_indexed_images(second_half, frames.framerate))
