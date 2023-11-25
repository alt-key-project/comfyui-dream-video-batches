

class LogEntry:
    ID = "LOG_ENTRY"

    @classmethod
    def new(cls, text):
        return LogEntry([(time.time(), text)])

    def __init__(self, data: List[Tuple[float, str]] = None):
        if data is None:
            self._data = list()
        else:
            self._data = list(data)

    def add(self, text: str):
        new_data = list(self._data)
        new_data.append((time.time(), text))
        return LogEntry(new_data)

    def merge(self, log_entry):
        new_data = list(self._data)
        new_data.extend(log_entry._data)
        return LogEntry(new_data)

    def get_filtered_entries(self, t: float):
        for d in sorted(self._data):
            if d[0] > t:
                yield d


class FrameCounter:
    ID = "FRAME_COUNTER"

    def __init__(self, current_frame=0, total_frames=1, frames_per_second=25.0):
        self.current_frame = max(0, current_frame)
        self.total_frames = max(total_frames, 1)
        self.frames_per_second = float(max(1.0, frames_per_second))

    def incremented(self, amount: int):
        return FrameCounter(self.current_frame + amount, self.total_frames, self.frames_per_second)

    @property
    def is_first_frame(self):
        return self.current_frame == 0

    @property
    def is_final_frame(self):
        return (self.current_frame + 1) == self.total_frames

    @property
    def is_after_last_frame(self):
        return self.current_frame >= self.total_frames

    @property
    def current_time_in_seconds(self):
        return float(self.current_frame) / self.frames_per_second

    @property
    def total_time_in_seconds(self):
        return float(self.total_frames) / self.frames_per_second

    @property
    def remaining_time_in_seconds(self):
        return self.total_time_in_seconds - self.current_time_in_seconds

    @property
    def progress(self):
        return float(self.current_frame) / (max(2, self.total_frames) - 1)


class AnimationSequence:
    ID = "ANIMATION_SEQUENCE"

    def __init__(self, frame_counter: FrameCounter, frames: Dict[int, List[str]] = None):
        self.frames = frames
        self.fps = frame_counter.frames_per_second
        self.frame_counter = frame_counter
        if self.is_defined:
            self.keys_in_order = sorted(frames.keys())
            self.num_batches = min(map(len, self.frames.values()))
        else:
            self.keys_in_order = []
            self.num_batches = 0

    @property
    def batches(self):
        return range(self.num_batches)

    def get_image_files_of_batch(self, batch_num):
        for key in self.keys_in_order:
            yield self.frames[key][batch_num]

    @property
    def is_defined(self):
        if self.frames:
            return True
        else:
            return False


class SharedTypes:
    frame_counter = {"frame_counter": (FrameCounter.ID,)}
    sequence = {"sequence": (AnimationSequence.ID,)}
    palette = {"palette": (RGBPalette.ID,)}
