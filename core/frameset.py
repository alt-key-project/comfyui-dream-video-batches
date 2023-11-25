# -*- coding: utf-8 -*-
from functools import cache
from typing import List

from torch import Tensor

from .dvb_image import DVB_Image
from .framerate import FrameRate



class IndexedImage:
    def __init__(self, image: DVB_Image, index: int):
        assert isinstance(image, DVB_Image)
        self.image = image
        self.index = index

class FrameSet:
    TYPE_NAME = "FRAME_SET"

    def __init__(self, tensor : Tensor, framerate: FrameRate, indices: List[int] = None):
        assert isinstance(tensor, Tensor)
        self._tensor = tensor
        self.framerate = framerate
        if indices is None:
            self.indices = list(range(len(self._tensor)))
        else:
            self.indices = list(sorted(indices))
        if not len(tensor) == len(indices):
            raise Exception("Tensor length {}, indices {} - tensor shape {}".format(len(tensor), len(self.indices), tensor.shape))



    def reindexed(self, first_index = 0, step = 1):
        indices = list()
        for i in range(len(self)):
            indices.append(first_index + i * step)
        return FrameSet(self._tensor, self.framerate, indices)


    @classmethod
    def from_images(cls, images: List[DVB_Image], framerate: FrameRate, indices: List[int] = None):
        return FrameSet(DVB_Image.join_to_tensor_data(images), framerate, indices)

    @classmethod
    def from_indexed_images(cls, images: List[IndexedImage], framerate: FrameRate):
        unindexed = list(map(lambda item: item.image, images))
        indices = list(map(lambda item: item.index, images))
        return FrameSet(DVB_Image.join_to_tensor_data(unindexed), framerate, indices)

    @property
    def last_index(self):
        if self.is_empty:
            return -1
        return self.indices[-1]

    @property
    def first_index(self):
        if self.is_empty:
            return -1
        return self.indices[0]

    def __len__(self):
        return len(self.indices)

    def has_index_gaps(self):
        if len(self) < 2:
            return False
        for i in range(1, len(self)):
            if (self.indices[i] - self.indices[i - 1]) != 1:
                return True
        return False

    @property
    def is_empty(self):
        return len(self._tensor) == 0

    @property
    def tensor(self) -> Tensor:
        return self._tensor

    @property
    @cache
    def indexed_length(self):
        if self.is_empty:
            return 0
        return self.indices[-1] - self.indices[0] + 1

    @property
    @cache
    def indexed_images(self) -> List[IndexedImage]:
        return list(map(lambda tp: IndexedImage(tp[1], tp[0]), zip(self.indices, self.images)))

    @property
    @cache
    def images(self):
        return DVB_Image.images_from_tensor_data(self._tensor)

    def merge(self, other):
        final_indices = set(self.indices)
        final_indices.update(other.indices)
        index_lookup_self = dict()
        index_lookup_other = dict()
        final_indices = list(sorted(final_indices))
        final_images = list()
        for i in range(len(self)):
            index_lookup_self[self.indices[i]] = i
        for i in range(len(other)):
            index_lookup_other[other.indices[i]] = i

        for index in final_indices:
            from_self = index_lookup_self.get(index, None)
            from_other = index_lookup_other.get(index, None)
            assert (from_self is not None) or (from_other is not None)
            if from_self is not None:
                final_images.append(self.images[from_self])
            else:
                final_images.append(other.images[from_other])
        return FrameSet.from_images(final_images, self.framerate, final_indices)

    def get_blended_frame_images(self):
        if self.is_empty:
            return list()
        images = self.images
        output_images = [images[0]]
        last_index = self.indices[0]
        for i in range(1, len(self)):
            prev_img = output_images[-1]
            img = images[i]
            index = self.indices[i]
            extra_frames = index - last_index - 1
            delta = 1.0 / (extra_frames + 1)
            for n in range(extra_frames):
                extra_img = prev_img.blend(img, (n + 1) * delta, 1.0 - ((n + 1) * delta))
                output_images.append(extra_img)
            output_images.append(img)
            last_index = index
        return output_images

