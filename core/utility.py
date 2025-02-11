import hashlib
import json
import os


def hashed_as_strings(*items, **kwargs):
    tokens = "|".join(list(map(str, items)))
    m = hashlib.sha256()
    m.update(tokens.encode(encoding="utf-8"))
    for pair in kwargs.items():
        m.update(str(pair).encode(encoding="utf-8"))
    return m.digest().hex()



class ForEachState:
    def __init__(self, filepath):
        self._filepath = os.path.abspath(filepath)
        self._dir = os.path.normpath(os.path.dirname(self._filepath))
        try:
            with open(self._filepath, "r", encoding="utf8") as f:
                self._data = json.load(f)
        except:
            self._data = dict()

    def add_files_to_process(self, files):
        files = list(map(lambda f: os.path.basename(f), files))
        all_files = set(self._data.keys())
        all_files.update(files)
        for filename in all_files:
            if filename not in self._data:
                self._data[filename] = False
        with open(self._filepath, "w", encoding="utf8") as f:
            txt = json.dumps(self._data, indent=2)
            f.write(txt)

    def mark_done(self, filename):
        filename = os.path.basename(filename)
        self._data[filename] = True
        with open(self._filepath, "w", encoding="utf8") as f:
            txt = json.dumps(self._data, indent=2)
            f.write(txt)

    def pop(self):
        for filename in sorted(self._data.keys()):
            if not self._data.get(filename, False):
                print("pop {}".format(filename))
                return os.path.join(self._dir, filename)
        return None
