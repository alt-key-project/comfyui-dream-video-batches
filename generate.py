from .core import *
from .categories import *


class DVB_InbetweenFrames:
    NODE_NAME = "Generate Inbetween Frames"
    ICON = "🧱"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "fill_mode": (["BLEND", "CLOSEST FRAME", "PREVIOUS FRAME"],)
            },
        }

    CATEGORY = NodeCategories.BASE
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frames: FrameSet, fill_mode):
        assert isinstance(frames, FrameSet)
        gc_comfyui()
        if fill_mode == "BLEND":
            return (frames.generate_inbetween_blended(),)
        elif fill_mode == "CLOSEST FRAME":
            return (frames.generate_inbetween_closest(),)
        else:
            return (frames.generate_inbetween_previous(),)
