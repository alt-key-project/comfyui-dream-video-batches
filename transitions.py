# -*- coding: utf-8 -*-

from .categories import *
from .core import *


class FadeProc:
    def __init__(self, fade_length, start_v, end_v):
        self._fade_len = fade_length
        self._start_v = start_v
        self._end_v = end_v
        self._delta = (self._end_v - self._start_v) / (abs(self._fade_len))

    def proc(self, n: int, total: int, im: DVB_Image, *a, **args):
        if self._start_v > self._end_v:
            # fade out (1.0, 0.75, 0.5, 0.25, 0) (len 4)
            end = total - 1
            start = max(total - 1 - abs(self._fade_len), 0)
            if start <= n <= end:
                i = n - start
                m = self._start_v + i * self._delta
                return (im.change_brightness(m),)
            else:
                return (im,)
        else:
            # fade in (0, 0.25, 0.5, 0.75, 1.0) (len 4)
            start = 0
            end = min(total - 1, abs(self._fade_len))
            if start <= n <= end:
                i = n - start
                m = self._start_v + i * self._delta
                return (im.change_brightness(m),)
            else:
                return (im,)


class DVB_FadeToBlack:
    NODE_NAME = "Fade To Black"
    ICON = "≻"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "fade_seconds": ("FLOAT", {"default": 1.0, "min": 0.1, "step": 0.1})
            },
        }

    CATEGORY = NodeCategories.BATCH_TRANSITIONS
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frames: FrameSet, fade_seconds: float):
        assert isinstance(frames, FrameSet)
        proc = DVB_ImageBatchProcessor(frames.tensor)
        fade_length = frames.framerate.seconds_to_frames(fade_seconds)
        fade = FadeProc(fade_length, 1.0, 0.0)
        return (FrameSet(tensor=proc.process(fade.proc), framerate=frames.framerate, indices= frames.indices),)


class DVB_FadeFromBlack:
    NODE_NAME = "Fade From Black"
    ICON = "≺"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "fade_seconds": ("FLOAT", {"default": 1.0, "min": 0.1, "step": 0.1})
            },
        }

    CATEGORY = NodeCategories.BATCH_TRANSITIONS
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frames: FrameSet, fade_seconds: float):
        assert isinstance(frames, FrameSet)
        proc = DVB_ImageBatchProcessor(frames.tensor)
        fade_length = frames.framerate.seconds_to_frames(fade_seconds)
        fade = FadeProc(fade_length, 0.0, 1.0)
        return (FrameSet(tensor=proc.process(fade.proc), framerate=frames.framerate, indices= frames.indices),)
