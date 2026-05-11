import os

CURRENT_PATH = os.path.dirname(__file__)


def getIconFilepath(name):
    filepath = os.path.abspath(os.path.join(CURRENT_PATH, "icons", f"{name}.png"))

    return filepath
