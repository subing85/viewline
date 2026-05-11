import os


def hasPathExists(filepath):
    if not filepath:
        return None

    absfilepath = os.path.expandvars(filepath)

    return os.path.exists(absfilepath)
