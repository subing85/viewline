import os

from PySide6 import QtCore

from playback.reader import VideoReader
from playback.reader import SequenceReader
from playback.frame_cache import FrameCache

class MediaPlayer(QtCore.QObject):

    frame_ready = QtCore.Signal(object)
    frame_changed = QtCore.Signal(int)

    def __init__(self):

        super().__init__()

        self.ocio_processor = None
        self.input_space = None
        self.display = None
        self.view = None

        self.reader = None

        self.current_frame = 0

        self.frame_count = 0
        self.cache = FrameCache(max_size=200)

        self.timer = QtCore.QTimer()

        self.timer.timeout.connect(self.next_frame)

    def load(self, path):
        extension = os.path.splitext(path)[1].lower()

        if extension in [".mp4", ".mov", ".avi"]:
            self.reader = VideoReader(path)
        else:
            self.reader = SequenceReader(path)

        self.frame_count = self.reader.frame_count()

        self.current_frame = 0

        self.update_frame()

    def play(self):

        print("\nself.reader", self.reader)
        if not self.reader:
            return

        fps = self.reader.fps()
        interval = int(1000 / fps)

        print("fps", fps, "interval", interval)
        self.timer.start(interval)

    def stop(self):
        self.timer.stop()

    def seek(self, frame):
        self.current_frame = frame
        self.update_frame()

    def next_frame(self):
        self.current_frame += 1

        if self.current_frame >= self.frame_count:
            self.current_frame = 0

        self.update_frame()

    def update_frame(self):
        frame = self.reader.get_frame(self.current_frame)
        self.cache.add(self.current_frame, frame)

        self.frame_ready.emit(frame)
        self.frame_changed.emit(self.current_frame)


    def _update_frame(self):
        frame = self.reader.get_frame(
            self.current_frame
        )

        # --------------------------------------------------
        # Apply OCIO
        # --------------------------------------------------

        if self.ocio_processor:
            frame = frame.astype("float32") / 255.0

            frame = self.ocio_processor.process_image(
                frame,
                self.input_space,
                self.display,
                self.view
            )

            frame = frame * 255.0
            frame = frame.clip(0, 255)
            frame = frame.astype("uint8")

            self.cache.add(self.current_frame, frame)

        self.frame_ready.emit(frame)
        self.frame_changed.emit(self.current_frame)


    def previous_frame(self):
        if not self.reader:
            return

        self.current_frame -= 1

        if self.current_frame < 0:
            self.current_frame = self.frame_count - 1

        self.update_frame()


    def next_frame_manual(self):

        if not self.reader:
            return

        self.current_frame += 1

        if self.current_frame >= self.frame_count:
            self.current_frame = 0

        self.update_frame()

    def set_ocio(self, processor, input_space, display, view):

        self.ocio_processor = processor
        self.input_space = input_space
        self.display = display
        self.view = view
        self.update_frame()