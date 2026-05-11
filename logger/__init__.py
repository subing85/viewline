# Copyright (c) 2026, Motion-Craft Technology All rights reserved.
# Author: Subin. Gopi (subing85@gmail.com).
# Description: Logger module.
# WARNING! All changes made in this file will be lost when recompiling source file!


from __future__ import absolute_import

import os
import sys
import logging
import tempfile


def Logger(**kwargs):
    tempdirname = os.path.join(tempfile.gettempdir(), "studio-pipe")
    if not os.path.isdir(tempdirname):
        os.makedirs(tempdirname)
    filename = kwargs.get("filename") or "pipe"
    filepath = os.path.join(tempdirname, "%s.log" % filename)
    format = "# %(asctime)s %(levelname)6s: %(module)s-line: %(lineno)d | %(message)s"
    date = "%Y/%m/%d %I:%M:%S:%p"
    formatter = logging.Formatter(fmt=format, datefmt=date)
    logging.basicConfig(
        filename=filepath,
        format=format,
        datefmt=date,
        filemode="a",
        level=logging.DEBUG,
    )
    logget = logging.getLogger()
    logget.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    return logget


def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:  # Prevent adding multiple handlers
        format = "# %(asctime)s%(levelname)8s: %(name)s-line: %(lineno)d | %(message)s"
        date = "%Y/%m/%d %I:%M:%S:%p"
        formatter = logging.Formatter(fmt=format, datefmt=date)

        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.propagate = False

    return logger


def logTypes():
    types = [
        "info",
        "critical",
        "error",
        "warning",
        "warn",
        "debug",
    ]
    print(types)
    return types


def nextLine():
    print("\n")


def verbose(value):
    print(value)


def separator(nextline=False):
    value = f"\n{'#'*60}" if nextline else "#" * 60
    print(value)


if __name__ == "__main__":
    pass
