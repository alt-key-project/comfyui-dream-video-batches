import os, json
import folder_paths as comfy_paths


TEMP_PATH = os.path.join(os.path.abspath(comfy_paths.temp_directory), "DreamVideoBatches")


class DRV_StateStore:
    def __init__(self, name, read_fun, write_fun):
        self._read = read_fun
        self._write = write_fun
        self._name = name

    def _as_key(self, k):
        return self._name + "_" + k

    def get(self, key, default):
        v = self[key]
        if v is None:
            return default
        else:
            return v

    def update(self, key, default, f):
        prev = self.get(key, default)
        v = f(prev)
        self[key] = v
        return v

    def __getitem__(self, item):
        return self._read(self._as_key(item))

    def __setitem__(self, key, value):
        return self._write(self._as_key(key), value)


class DRV_StateFile:
    def __init__(self, state_collection_name="state"):
        self._filepath = os.path.join(TEMP_PATH, state_collection_name + ".json")
        self._dirname = os.path.dirname(self._filepath)
        if not os.path.isdir(self._dirname):
            os.makedirs(self._dirname)
        if not os.path.isfile(self._filepath):
            self._data = {}
        else:
            with open(self._filepath, encoding="utf-8") as f:
                self._data = json.load(f)

    def get_section(self, name: str) -> DRV_StateStore:
        return DRV_StateStore(name, self._read, self._write)

    def _read(self, key):
        return self._data.get(key, None)

    def _write(self, key, value):
        previous = self._data.get(key, None)
        if value is None:
            if key in self._data:
                del self._data[key]
        else:
            self._data[key] = value
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f)
        return previous

