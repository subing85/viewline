from pprint import pprint
cached_frames1 = [
    {0},
    {0, 1},
    {0, 1, 2},
    {0, 1, 2, 3},
    {0, 1, 2, 3, 4},
    {0, 1, 2, 3, 4, 5},
    {0, 1, 2, 3, 4, 5, 6},
    {0, 1, 2, 3, 4, 5, 6, 7},
    {0, 1, 2, 3, 4, 5, 6, 7, 8},
    {0, 1, 2, 3, 4, 5, 6, 7, 8, 9},
    {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
]

for cached_frames in cached_frames1:

    frames = sorted(cached_frames)

    ranges = []
    start = frames[0]
    end = frames[0]

    for frame in frames:
        end = frame+1

    ranges.append((start, end))

    pprint(ranges)
