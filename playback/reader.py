import os
import re
import av
import glob
import numpy as np
import OpenImageIO as oiio


class VideoReader(object):

    def __init__(self, path):

        self.typed = "video"
        self.path = path
        self.container = av.open(path)
        self.stream = self.container.streams.video[0]

        self.frames = list(self.container.decode(self.stream))

    def frame_count(self):
        return len(self.frames)

    def get_fps(self, rounded=0):
        fps = float(self.stream.average_rate)

        if rounded == 0:
            return fps

        result = round(fps, rounded)

        return result

    def get_frame(self, frame_number):
        frame = self.frames[frame_number]
        image = frame.to_ndarray(format="rgb24")

        return image


class SequenceReader(object):

    def __init__(self, path):
        self.typed = "sequence"

        self.fps = 24.0

        self.path = path
        self.files = self.find_sequence(path)

    def find_sequence(self, path):

        pattern = re.sub(r"#+", "*", path)
        found_files = sorted(glob.glob(pattern))
        files = sorted(glob.glob(pattern))

        # directory = os.path.dirname(path)
        # extension = os.path.splitext(path)[1]
        # pattern = os.path.join(directory, f"*{extension}")
        # files = sorted(glob.glob(pattern))

        return files

    def frame_count(self):
        return len(self.files)

    def get_fps(self):
        return self.fps

    def set_fps(self, fps):
        self.fps = fps or self.fps

    def get_frame(self, frame_number):
        path = self.files[frame_number]
        input_file = oiio.ImageInput.open(path)

        if not input_file:
            raise RuntimeError(f"Failed to open image: {path}")

        spec = input_file.spec()
        channels = spec.channelnames

        # print(channels)

        # --------------------------------------------------
        # Find RGB
        # --------------------------------------------------

        rgb = None

        candidates = [
            ("R", "G", "B"),
            ("beauty.R", "beauty.G", "beauty.B"),
            ("rgba.R", "rgba.G", "rgba.B"),
            ("Ci.R", "Ci.G", "Ci.B"),
        ]

        for candidate in candidates:
            if all(ch in channels for ch in candidate):
                rgb = candidate
                break

        if not rgb:
            raise RuntimeError(f"No RGB channels found in: {path}")

        channel_indices = [channels.index(ch) for ch in rgb]

        image = input_file.read_image(chbegin=channel_indices[0], chend=channel_indices[-1] + 1)
        input_file.close()

        image = np.array(image)

        # return image
        # image = image.astype(np.float32)

        # return image

        # float -> preview
        image = np.clip(image, 0.0, 1.0)

        image = (image * 255.0).astype(np.uint8)

        return image
