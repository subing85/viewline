class FrameCache:

    def __init__(self, max_size=100):

        self.max_size = max_size

        self.cache = {}

    def get(self, frame):

        return self.cache.get(frame)

    def add(self, frame, image):

        if len(self.cache) >= self.max_size:

            first_key = next(iter(self.cache))

            # del self.cache[first_key]

        self.cache[frame] = image

    def clear(self):

        self.cache.clear()
