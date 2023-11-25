# -*- coding: utf-8 -*-
import random


class PartialPrompt:
    ID = "PARTIAL_PROMPT"

    def __init__(self):
        self._data = {}

    def merge(self, other):
        p = PartialPrompt()
        for item in self._data.items():
            p._data[item[0]] = item[1]
        for item in other._data.items():
            p._data[item[0]] = item[1]
        return p

    def add(self, text: str, weight: float):
        output = PartialPrompt()
        output._data = dict(self._data)
        for parts in text.split(","):
            parts = parts.strip()
            if " " in parts and not (parts.startswith("(") and parts.endswith(")")):
                output._data["(" + parts + ")"] = weight
            else:
                output._data[parts] = weight
        return output

    def random_subset(self, num_positive, num_negative, seed):
        rnd = random.Random()
        rnd.seed(seed)
        positives = list(filter(lambda item: item[1] > 0, self._data.items()))
        negatives = list(filter(lambda item: item[1] < 0, self._data.items()))
        rnd.shuffle(positives)
        rnd.shuffle(negatives)
        num_negative = min(len(negatives), num_negative)
        num_positive = min(len(positives), num_positive)
        new_prompt = PartialPrompt()
        for i in range(num_positive):
            item = positives.pop()
            new_prompt = new_prompt.add(item[0], item[1])
        for i in range(num_negative):
            item = negatives.pop()
            new_prompt = new_prompt.add(item[0], item[1])
        return new_prompt

    def is_empty(self):
        return not self._data

    def abs_sum(self):
        if not self._data:
            return 0.0
        return sum(map(abs, self._data.values()))

    def abs_max(self):
        if not self._data:
            return 0.0
        return max(map(abs, self._data.values()))

    def scaled_by(self, f: float):
        new_data = PartialPrompt()
        new_data._data = dict(self._data)
        for text, weight in new_data._data.items():
            new_data._data[text] = weight * f
        return new_data

    def finalize_signed(self, clamp: float):
        items = self._data.items()
        items = sorted(items, key=lambda pair: (pair[1], pair[0]))
        pos = list()
        neg = list()
        for text, w in sorted(items, key=lambda pair: (-pair[1], pair[0])):
            if w >= 0.0001:
                pos.append("({}:{:.3f})".format(text, min(clamp, w)))
        for text, w in sorted(items, key=lambda pair: (pair[1], pair[0])):
            if w <= -0.0001:
                neg.append("({}:-{:.3f})".format(text, min(clamp, -w)))
        return ", ".join(pos + neg)

    def finalize(self, clamp: float):
        items = self._data.items()
        items = sorted(items, key=lambda pair: (pair[1], pair[0]))
        pos = list()
        neg = list()
        for text, w in sorted(items, key=lambda pair: (-pair[1], pair[0])):
            if w >= 0.0001:
                pos.append("({}:{:.3f})".format(text, min(clamp, w)))
        for text, w in sorted(items, key=lambda pair: (pair[1], pair[0])):
            if w <= -0.0001:
                neg.append("({}:{:.3f})".format(text, min(clamp, -w)))
        return ", ".join(pos), ", ".join(neg)
