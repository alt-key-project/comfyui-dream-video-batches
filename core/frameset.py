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

    def __init__(self, tensor: Tensor, framerate: FrameRate, indices: List[int] = None):
        assert isinstance(tensor, Tensor)
        self._tensor = tensor
        self.framerate = framerate
        if indices is None:
            self.indices = list(range(len(self._tensor)))
        else:
            self.indices = list(sorted(indices))

        if not len(tensor) == len(indices):
            raise Exception(
                "Tensor length {}, indices {} - tensor shape {}".format(len(tensor), len(self.indices), tensor.shape))

    @property
    def image_dimensions(self):
        if self.is_empty:
            return (0, 0)
        s = self._tensor[0].shape
        print("Shape is {}".format(s))
        return s[1], s[0]

    def reindexed(self, first_index=0, step=1):
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

    def _generate_between_list(self):
        prev_image = None
        prev_index = None
        images = self.images
        work = list()
        for i in range(len(self)):
            img = images[i]
            idx = self.indices[i]
            if prev_index is not None:
                for new_index in range(prev_index + 1, idx):
                    work.append((new_index, prev_index, prev_image, idx, img))
            prev_index = idx
            prev_image = img
        return work

    def generate_inbetween_blended(self):
        new_frames = list()
        for (idx, prev_img_idx, prev_img, next_img_idx, next_img) in self._generate_between_list():
            w = (idx - prev_img_idx) / (next_img_idx - prev_img_idx)
            new_frames.append(IndexedImage(prev_img.blend(next_img, 1.0 - w, w), idx))
        return self.merge(FrameSet.from_indexed_images(new_frames, self.framerate))

    def generate_inbetween_previous(self):
        new_frames = list()
        for (idx, prev_img_idx, prev_img, next_img_idx, next_img) in self._generate_between_list():
            new_frames.append(IndexedImage(prev_img, idx))
        return self.merge(FrameSet.from_indexed_images(new_frames, self.framerate))

    def generate_inbetween_closest(self):
        new_frames = list()
        for (idx, prev_img_idx, prev_img, next_img_idx, next_img) in self._generate_between_list():
            if abs(idx - prev_img_idx) < abs(next_img_idx - idx):
                new_frames.append(IndexedImage(prev_img, idx))
            else:
                new_frames.append(IndexedImage(next_img, idx))
        return self.merge(FrameSet.from_indexed_images(new_frames, self.framerate))

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

    def fade_to(self, frames_after, fade_length):
        images_first = self.indexed_images
        images_after = frames_after.indexed_images
        if fade_length < 1:
            FrameSet.from_indexed_images(images_first + images_after, self.framerate)
        a = images_first[0:len(images_first) - fade_length]
        b = images_first[len(images_first) - fade_length:]
        c = images_after[0:fade_length]
        d = images_after[fade_length:]

        print("first : {}".format(len(images_first)))
        print("after : {}".format(len(images_after)))
        print("a : {}".format(len(a)))
        print("b : {}".format(len(b)))
        print("c : {}".format(len(c)))
        print("d : {}".format(len(d)))

        assert (len(a) + len(b)) == len(images_first)
        assert len(b) == len(c)
        assert (len(c) + len(d)) == len(images_after)

        bandc = list()
        for i in range(fade_length):
            f = float(i + 1) / (fade_length + 1)
            img = b[i].image.blend(c[i].image, 1.0 - f, f)
            bandc.append(IndexedImage(img, b[i].index))

        d = FrameSet.from_indexed_images(d, self.framerate).reindexed(bandc[-1].index + 1).indexed_images
        return FrameSet.from_indexed_images(a + bandc + d, self.framerate)
