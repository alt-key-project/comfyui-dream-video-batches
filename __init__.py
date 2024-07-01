# -*- coding: utf-8 -*-

from .calculate import *
from .cutandjoin import *
from .inputfields import *
from .transitions import *
from .utility import *
from .generate import *
from .camera import *
from .loaders import *
from .wrapping import *
from .core import DVB_Config
import json, os

_NODE_CLASSES = [
    #DVB_TraceMalloc,
    DVB_FrameSetReindex,
    DVB_FrameSetOffset,
    DVB_Calculation,
    DVB_Multiply,
    DVB_Divide,
    DVB_Splitter,
    DVB_InputFloat,
    DVB_InputInt,
    DVB_InputText,
    DVB_InputString,
    DVB_ImagesToFrameSet,
    DVB_BlendedTransition,
    DVB_UnwrapFrameSet,
    DVB_ConcatFrameSets,
    DVB_MergeFrames,
    DVB_FadeFromBlack,
    DVB_FadeToBlack,
    DVB_LinearCameraPan,
    DVB_SineCameraPan,
    DVB_Zoom,
    DVB_ZoomSine,
    DVB_LinearCameraRoll,
    DVB_SineCameraRoll,
    DVB_InbetweenFrames,
    DVB_ForEachFilename,
    DVB_ForEachCheckpoint,
    DVB_LoadImageFromPath,
    DVB_Reverse,
    DVB_FrameSetRepeat,
    DVB_FrameSetDimensionsScaled,
    DVB_FrameSetSplitBeginning,
    DVB_FrameSetSplitEnd
]


_SIGNATURE_SUFFIX = " [DVB]"

MANIFEST = {
    "name": "Dream Video Batches",
    "version": (1, 0, 1),
    "author": "Dream Project",
    "project": "https://github.com/alt-key-project/comfyui-dream-video-batches",
    "description": "Various utility nodes for working with video batches in ComfyUI",
}

NODE_CLASS_MAPPINGS = {}

NODE_DISPLAY_NAME_MAPPINGS = {}

config = DVB_Config()


def update_category(cls):
    top = config.get("ui.top_category", "").strip().strip("/")
    leaf_icon = ""
    if top and "CATEGORY" in cls.__dict__:
        cls.CATEGORY = top + "/" + cls.CATEGORY.lstrip("/")
    if "CATEGORY" in cls.__dict__:
        joined = []
        for partial in cls.CATEGORY.split("/"):
            icon = config.get("ui.category_icons." + partial, "")
            if icon:
                leaf_icon = icon
            if config.get("ui.prepend_icon_to_category", False):
                partial = icon.lstrip() + " " + partial
            if config.get("ui.append_icon_to_category", False):
                partial = partial + " " + icon.rstrip()
            joined.append(partial)
        cls.CATEGORY = "/".join(joined)
    return leaf_icon


def update_display_name(cls, category_icon, display_name):
    icon = cls.__dict__.get("ICON", category_icon)
    if config.get("ui.prepend_icon_to_node", False):
        display_name = icon.lstrip() + " " + display_name
    if config.get("ui.append_icon_to_node", False):
        display_name = display_name + " " + icon.rstrip()
    return display_name


for cls in _NODE_CLASSES:
    category_icon = update_category(cls)
    clsname = cls.__name__
    if "NODE_NAME" in cls.__dict__:
        node_name = cls.__dict__["NODE_NAME"] + _SIGNATURE_SUFFIX
        NODE_CLASS_MAPPINGS[node_name] = cls
        NODE_DISPLAY_NAME_MAPPINGS[node_name] = update_display_name(cls, category_icon,
                                                                    cls.__dict__.get("DISPLAY_NAME",
                                                                                     cls.__dict__["NODE_NAME"]))
    else:
        raise Exception("Class {} is missing NODE_NAME!".format(str(cls)))


def update_node_index():
    node_list_path = os.path.join(os.path.dirname(__file__), "node_list.json")
    with open(node_list_path) as f:
        node_list = json.loads(f.read())
    updated = False
    for nodename in NODE_CLASS_MAPPINGS.keys():
        if nodename not in node_list:
            node_list[nodename] = ""
            updated = True
    if updated or True:
        with open(node_list_path, "w") as f:
            f.write(json.dumps(node_list, indent=2, sort_keys=True))


update_node_index()
