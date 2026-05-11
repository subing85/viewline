import os
import glob

import numpy as np

import OpenImageIO as oiio


class SequenceReader:

    def __init__(self, path):

        self.path = path

        self.files = self.find_sequence(path)

    def find_sequence(self, path):

        directory = os.path.dirname(path)

        extension = os.path.splitext(path)[1]

        pattern = os.path.join(directory, f"*{extension}")

        files = sorted(glob.glob(pattern))

        return files

    def frame_count(self):

        return len(self.files)

    def fps(self):

        return 24.0

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
