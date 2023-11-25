# -*- coding: utf-8 -*-

import numpy
import torch
from .err import raise_error
from PIL import Image, ImageFilter, ImageEnhance
from PIL.Image import Resampling
from PIL.ImageDraw import ImageDraw
from torch import Tensor


def _convert_tensor_image_to_pil(tensor_image) -> Image:
    return Image.fromarray(numpy.clip(255. * tensor_image.cpu().numpy().squeeze(), 0, 255).astype(numpy.uint8))


def _convert_from_pil_to_tensor(pil_image):
    return torch.from_numpy(numpy.array(pil_image).astype(numpy.float32) / 255.0)


class DVB_Image:
    def __init__(self, tensor_image=None, pil_image=None, file_path=None, with_alpha=False):
        if tensor_image is None and pil_image is None and file_path is None:
            raise Exception("No Image provided!")

        self._tensor_image = tensor_image
        self._pil_image = pil_image
        if pil_image is None and file_path is not None:
            self._pil_image = Image.open(file_path)
        self._with_alpha = with_alpha
        self._image_draw = None
        self._numpy = None

    @classmethod
    def join_to_tensor_data(cls, images):
        def _to_tensor(img):
            t = img
            if t is None:
                return None
            if isinstance(img, cls):
                t = img.tensor_image
            return t
        image_tensors = [_to_tensor(image) for image in images]
        dims = 0
        for t in image_tensors:
            print("Image tensor is shape {}".format(t.shape))

        tensor = torch.from_numpy(numpy.array(image_tensors))
        assert len(tensor) == len(images)
        return tensor

    @classmethod
    def images_from_tensor_data(cls, tensor: Tensor):
        return [DVB_Image(tensor_image=data) for data in tensor]

    @property
    def pil_image(self):
        if self._pil_image is not None:
            return self._pil_image
        pil_img = _convert_tensor_image_to_pil(self._tensor_image)
        if self._with_alpha and pil_img.mode != "RGBA":
            pil_img = pil_img.convert("RGBA")
        else:
            if pil_img.mode not in ("RGB", "RGBA"):
                pil_img = pil_img.convert("RGB")
        self._pil_image = pil_img
        return self._pil_image

    @property
    def tensor_image(self):
        if self._tensor_image is not None:
            return self._tensor_image
        self._tensor_image = _convert_from_pil_to_tensor(self._pil_image)
        return self._tensor_image

    @property
    def numpy_array(self):
        if self._numpy is not None:
            return self._numpy
        self._numpy = numpy.array(self.pil_image)
        return self._numpy

    @property
    def width(self):
        return self.pil_image.width

    @property
    def height(self):
        return self.pil_image.height

    @property
    def size(self):
        return self.pil_image.size

    @property
    def _draw(self):
        if self._image_draw is not None:
            return self._image_draw
        self._image_draw = ImageDraw(self.pil_image)
        return self._image_draw

    def change_brightness(self, factor):
        enhancer = ImageEnhance.Brightness(self.pil_image)
        return DVB_Image(pil_image=enhancer.enhance(factor))

    def change_contrast(self, factor):
        enhancer = ImageEnhance.Contrast(self.pil_image)
        return DVB_Image(pil_image=enhancer.enhance(factor))

    def numpy_array(self):
        return numpy.array(self.pil_image)

    def convert(self, mode="RGB"):
        if mode in ("GRAY", "GREY"):
            mode = "L"
        if self.pil_image.mode == mode:
            return self
        return DVB_Image(pil_image=self.pil_image.convert(mode))

    def blend(self, other, weight_self: float = 0.5, weight_other: float = 0.5):
        alpha = 1.0 - weight_self / (weight_other + weight_self)
        return DVB_Image(pil_image=Image.blend(self.pil_image, other.pil_image, alpha))

    def blur(self, amount):
        return DVB_Image(pil_image=self.pil_image.filter(ImageFilter.GaussianBlur(amount)))

    def adjust_colors(self, red_factor=1.0, green_factor=1.0, blue_factor=1.0):
        # newRed   = 1.1*oldRed  +  0*oldGreen    +  0*oldBlue  + constant
        # newGreen = 0*oldRed    +  0.9*OldGreen  +  0*OldBlue  + constant
        # newBlue  = 0*oldRed    +  0*OldGreen    +  1*OldBlue  + constant
        matrix = (red_factor, 0, 0, 0,
                  0, green_factor, 0, 0,
                  0, 0, blue_factor, 0)
        return DVB_Image(pil_image=self.pil_image.convert("RGB", matrix))

    @classmethod
    def empty(cls, width, height, mode):
        return DVB_Image(pil_image=Image.new(mode, (width, height), 0))

    @classmethod
    def from_file(cls, file_path):
        return DVB_Image(pil_image=Image.open(file_path))

    def resize(self, resize_width=0, resize_height=0, resampling=Resampling.NEAREST):
        if resize_width > 0 or resize_height > 0:
            ratio = self.width / self.height
            if resize_height <= 0:
                resize_height = round(resize_width / ratio)
            elif resize_width <= 0:
                resize_width = round(resize_height * ratio)
            return DVB_Image(pil_image=self.pil_image.resize((resize_width, resize_height), resampling))
        else:
            return self
