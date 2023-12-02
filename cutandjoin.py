# -*- coding: utf-8 -*-
from .core.frameset import IndexedImage

from .categories import *
from .core import *


class DVB_FrameSetReindex:
    NODE_NAME = "Frame Set Reindex"
    ICON = "🔢"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "start": ("INT", {"default": 0}),
                "step": ("INT", {"default": 1})
            },
        }

    CATEGORY = NodeCategories.BASE
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frames: FrameSet, start, step):
        return (frames.reindexed(start, step),)


class DVB_FrameSetOffset:
    NODE_NAME = "Frame Set Index Offset"
    ICON = "🔢"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "offset": ("INT", {"default": 0})
            },
        }

    CATEGORY = NodeCategories.BASE
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frames: FrameSet, offset):
        return (frames.reindexed(frames.first_index + offset),)


class DVB_ConcatFrameSets:
    NODE_NAME = "Frame Set Concatenation"
    ICON = "🔗"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "a": (FrameSet.TYPE_NAME,),
                "b": (FrameSet.TYPE_NAME,),
                "offset_from_end": ("INT", {"default": 0}),
                "step": ("INT", {"default": 1, "min": 1}),
            },
        }

    CATEGORY = NodeCategories.EDIT
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, a: FrameSet, b: FrameSet, offset_from_end, step):
        first_index = a.last_index + step + offset_from_end

        if a.framerate != b.framerate:
            on_node_error(DVB_MergeFrames,
                          "Frame sets have different framerate {} and {} - cannot concatenate!".format(a.framerate,
                                                                                                       b.framerate))

        return (a.merge(b.reindexed(first_index, step)),)


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

    CATEGORY = NodeCategories.EDIT
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

    CATEGORY = NodeCategories.EDIT
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
        return (FrameSet.from_indexed_images(first_half, frames.framerate),
                FrameSet.from_indexed_images(second_half, frames.framerate))


class DVB_Reverse:
    NODE_NAME = "Frame Set Reverse"
    ICON = "⮠"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
            },
        }

    CATEGORY = NodeCategories.EDIT
    RETURN_TYPES = (FrameSet.TYPE_NAME, )
    RETURN_NAMES = ("frames", )
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frames: FrameSet):
        return (FrameSet.from_images(list(reversed(frames.images)), frames.framerate, frames.indices),)

class DVB_FrameSetRepeat:
    NODE_NAME = "Frame Set Repeat"
    ICON = "𝄈"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "repetitions": ("INT", {"default": 2, "min": 1}),
                "step": ("INT", {"default": 1, "min": 1})
            },
        }

    CATEGORY = NodeCategories.EDIT
    RETURN_TYPES = (FrameSet.TYPE_NAME, )
    RETURN_NAMES = ("frames", )
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frames: FrameSet, repetitions, step):
        original_frames = frames.indexed_images
        result = list()
        last_frame_index = 0
        for i in range(repetitions):
            start_index = last_frame_index + step
            for f in original_frames:
                result.append(IndexedImage(f.image, start_index + f.index))
            last_frame_index = result[-1].index

        return (FrameSet.from_indexed_images(result, frames.framerate),)
