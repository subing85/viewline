# Copyright (c) 2026, Motion-Craft Technology All rights reserved.
# Author: Subin. Gopi (subing85@gmail.com).
# Description: Review Player sketch stroke module.
# WARNING! All changes made in this file will be lost when recompiling source file!

from __future__ import absolute_import

import math
import copy
import uuid

from PySide6 import QtGui
from PySide6 import QtCore
from PySide6 import QtWidgets


class Sketch(object):
    """
    Frame-based sketch stroke manager.

    This class stores freehand drawing strokes for each frame
    and provides methods for creating, editing, clearing, and
    rendering sketches.

    Notes:
        stroke points should be stored as normalized
        coordinates (0.0 - 1.0) relative to the displayed image.

    Example:
        {
            1001: [
                {
                    "color": (255, 0, 0),
                    "thickness": 3,
                    "points": [
                        (0.25, 0.50),
                        (0.30, 0.55)
                    ]
                }
            ]
        }
    """

    def __init__(self):
        """
        Initialize sketch manager.
        """

        # Current active stroke tool.
        self.tool = "pencil"

        # Current Active Frame
        self.current_frame = None

        # Drawing State
        self.enabled = False
        self.drawing = False

        # Active Brush Color
        self.color = (255, 0, 0)

        # Active Brush Thickness
        self.thickness = 3

        # Active eraser radius
        self.eraser_radius = 0.02

        # Current Stroke
        self.current_stroke = None

        # Frame Stroke Storage
        self.strokes = dict()

        self.image_width = 1920
        self.image_height = 1080

        self.txt_font = None

        self.drag_start = None
        self.drag_end = None

        self.preview_shape = None

        self.selected_stroke = None

        self.move_start = None
        self.original_stroke = None

        self.undo_history = list()

    def set_tool(self, tool):
        """
        Set active stroke tool.

        Args:
            tool (str):
                Tool name ("pencil", "eraser").
        """
        self.tool = tool

    def set_enabled(self, enabled):
        """
        Enable or disable stroke drawing.

        Args:
            enabled (bool): Pencil tool state.
        """

        self.enabled = enabled

    def set_frame(self, frame):
        """
        Set current active frame.

        Args:
            frame (int):
                Current frame number.
        """

        self.current_frame = frame

    def set_color(self, color):
        """
        Set active brush color.

        Args:
            color (tuple):
                RGB color tuple.
        """

        self.color = color or self.color

    def set_thickness(self, value):
        """
        Set active brush thickness.

        Args:
            value (int):
                Line thickness.
        """

        self.thickness = max(1, int(value))

    def set_eraser_radius(self, value):
        """
        Set eraser radius in image pixels.

        Args:
            value (int):
                Radius in pixels.

        5    # very small
        10   # small
        20   # medium
        40   # large
        80   # huge
        """

        self.eraser_radius = max(1, int(value))

    def set_image_size(self, width, height):
        """
        Store source image size.

        Args:
            width (int):
                Source image width.

            height (int):
                Source image height.
        """

        self.image_width = max(width, 1)
        self.image_height = max(height, 1)

    def set_txt_font(self, values):
        self.txt_font = values

    def get_strokes(self):
        """
        Return strokes for current frame.

        Returns:
            list:
                Frame stroke list.
        """

        if self.current_frame is None:
            return list()

        return self.strokes.get(self.current_frame, list())

    def has_strokes(self):
        """
        Check whether current frame contains sketches.

        Returns:
            bool
        """

        if self.current_frame is None:
            return False

        return bool(self.strokes.get(self.current_frame))

    def frame_count(self):
        """
        Return number of annotated frames.

        Returns:
            int
        """

        return len(self.strokes)

    def generate_id(self):
        return str(uuid.uuid4())

    def mousePressEvent(self, point):
        """
        Start drawing operation.
        """

        if self.current_frame is None:
            return

        # Enable drag operation
        self.drawing = True

        if self.tool == "move":
            self.selected_stroke = self.hit_stroke(point)

            if self.selected_stroke:
                self.move_start = point
                self.original_stroke = copy.deepcopy(self.selected_stroke)

            return

        # Eraser
        if self.tool == "eraser":
            # Save current frame state ONCE
            self.undo_history.append(
                {
                    "type": "erase",
                    "frame": self.current_frame,
                    "strokes": copy.deepcopy(self.strokes.get(self.current_frame, list())),
                }
            )

            self.drawing = True
            self.erase(point)

            return

        if self.tool == "txt":

            if self.txt_font.get("txt"):

                stroke = self.txt_font.copy()

                stroke["id"] = self.generate_id()
                stroke["type"] = "txt"
                stroke["position"] = point

                self.strokes.setdefault(self.current_frame, [])
                self.strokes[self.current_frame].append(stroke)

                self.undo_history.append(
                    {
                        "type": "create",
                        "frame": self.current_frame,
                        "stroke_id": stroke["id"],
                    }
                )

            return

        # Create stroke
        stroke = {
            "id": self.generate_id(),
            "type": self.tool,
            "color": self.color,
            "thickness": self.thickness,
        }

        # Pencil
        if self.tool == "pencil":
            stroke["points"] = [point]

        # Rectangle / Ellipse
        elif self.tool in ["rectangle", "ellipse"]:
            stroke["start"] = point
            stroke["end"] = point

        self.current_shape = stroke

        self.strokes.setdefault(self.current_frame, list())
        self.strokes[self.current_frame].append(stroke)

    def mouseMoveEvent(self, point):
        """
        Update current drawing operation.
        """

        if not self.drawing:
            return

        if self.tool == "move":

            if not self.selected_stroke:
                return

            dx = point[0] - self.move_start[0]
            dy = point[1] - self.move_start[1]

            self.move_stroke(self.selected_stroke, dx, dy)

            self.move_start = point

            return

        # Eraser
        if self.tool == "eraser":
            self.erase(point)
            return

        if self.tool == "txt":
            return

        if not self.current_shape:
            return

        typed = self.current_shape["type"]

        # Pencil
        if typed == "pencil":
            self.current_shape["points"].append(point)

        # Rectangle / Ellipse
        elif typed in ["rectangle", "ellipse"]:
            self.current_shape["end"] = point

    def mouseReleaseEvent(self, point):
        """
        Finish drawing operation.
        """

        if not self.drawing:
            return

        if self.tool == "move":

            if self.selected_stroke and self.original_stroke:
                self.undo_history.append(
                    {
                        "type": "move",
                        "stroke_id": self.selected_stroke["id"],
                        "old_data": self.original_stroke,
                    }
                )

            self.selected_stroke = None
            self.original_stroke = None

            self.drawing = False

            return

        # Eraser
        if self.tool == "eraser":
            self.drawing = False
            return

        if self.tool == "txt":
            return

        # Final Shape Update
        if self.current_shape:
            typed = self.current_shape["type"]

            if typed in ["rectangle", "ellipse"]:
                self.current_shape["end"] = point

            self.undo_history.append(
                {
                    "type": "create",
                    "frame": self.current_frame,
                    "stroke_id": self.current_shape["id"],
                }
            )

        self.drawing = False
        self.current_shape = None

    def draw(self, painter, point_converter=None):
        """
        Draw all strokes for current frame.
        """

        if self.current_frame is None:
            return

        strokes = self.get_strokes()

        for stroke in strokes:
            typed = stroke["type"]

            if typed == "pencil":
                pen = QtGui.QPen(QtGui.QColor(*stroke["color"]))
                pen.setWidth(stroke["thickness"])
                painter.setPen(pen)

                self.draw_pencil(painter, stroke, point_converter)

            elif typed == "rectangle":
                pen = QtGui.QPen(QtGui.QColor(*stroke["color"]))
                pen.setWidth(stroke["thickness"])
                painter.setPen(pen)

                self.draw_rectangle(painter, stroke, point_converter)

            elif typed == "ellipse":
                pen = QtGui.QPen(QtGui.QColor(*stroke["color"]))
                pen.setWidth(stroke["thickness"])
                painter.setPen(pen)

                self.draw_ellipse(painter, stroke, point_converter)

            elif typed == "txt":
                self.draw_text(painter, stroke, point_converter)

            # Draw selection box for selected stroke
            if stroke is self.selected_stroke:
                self.draw_selection(painter, stroke, point_converter)

    def draw_pencil(self, painter, stroke, point_converter=None):
        points = stroke["points"]

        if len(points) < 2:
            return

        for index in range(len(points) - 1):
            point1 = points[index]
            point2 = points[index + 1]

            if point_converter:
                point1 = point_converter(point1)
                point2 = point_converter(point2)

            painter.drawLine(point1, point2)

    def draw_ellipse(self, painter, stroke, point_converter=None):

        point1 = stroke["start"]
        point2 = stroke["end"]

        if point_converter:
            point1 = point_converter(point1)
            point2 = point_converter(point2)

        rect = QtCore.QRectF(point1, point2).normalized()

        painter.drawEllipse(rect)

    def draw_rectangle(self, painter, stroke, point_converter=None):

        point1 = stroke["start"]
        point2 = stroke["end"]

        if point_converter:
            point1 = point_converter(point1)
            point2 = point_converter(point2)

        rect = QtCore.QRectF(point1, point2).normalized()

        painter.drawRect(rect)

    def draw_text(self, painter, stroke, point_converter=None):

        point = stroke["position"]

        if point_converter:
            draw_point = point_converter(point)
        else:
            draw_point = point

        font = QtGui.QFont()

        font.setFamily(stroke.get("family", None))
        font.setPointSize(stroke.get("font_size", 24))
        font.setBold(stroke.get("bold", False))

        font.setItalic(stroke.get("italic", False))
        font.setUnderline(stroke.get("underline", False))
        font.setStrikeOut(stroke.get("strike_out", False))

        painter.setFont(font)

        metrics = QtGui.QFontMetrics(font)

        text = stroke["txt"]

        width = metrics.horizontalAdvance(text)
        height = metrics.height()

        ascent = metrics.ascent()

        stroke["bounds"] = {
            "x": point[0],
            "y": point[1],
            "width": width,
            "height": height,
            "ascent": ascent,
        }

        painter.setPen(QtGui.QColor(*stroke["color"]))
        painter.drawText(draw_point, text)

    def erase(self, point):

        strokes = self.get_strokes()

        if not strokes:
            return

        new_strokes = list()

        for stroke in strokes:
            typed = stroke.get("type", "pencil")

            # Pencil
            if typed == "pencil":
                new_strokes.extend(self.hit_pencil(stroke, point))

            # Rectangle
            elif typed == "rectangle":
                if not self.hit_rectangle(stroke, point):
                    new_strokes.append(stroke)

            # Ellipse
            elif typed == "ellipse":
                if not self.hit_ellipse(stroke, point):
                    new_strokes.append(stroke)

            # txt
            elif typed == "txt":
                if not self.hit_txt(stroke, point):
                    new_strokes.append(stroke)

        self.strokes[self.current_frame] = new_strokes

    def move_stroke(self, stroke, dx, dy):

        typed = stroke["type"]

        if typed == "pencil":
            stroke["points"] = [(x + dx, y + dy) for x, y in stroke["points"]]

        elif typed in ["rectangle", "ellipse"]:
            x1, y1 = stroke["start"]
            x2, y2 = stroke["end"]

            stroke["start"] = (x1 + dx, y1 + dy)
            stroke["end"] = (x2 + dx, y2 + dy)

        elif typed == "txt":
            x, y = stroke["position"]
            stroke["position"] = (x + dx, y + dy)

    def get_stroke_rect(self, stroke, point_converter=None):
        if stroke["type"] == "pencil":
            points = stroke["points"]

            converted = [point_converter(p) if point_converter else p for p in points]

            xs = [p.x() for p in converted]
            ys = [p.y() for p in converted]

            rect = QtCore.QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))

            return rect

        elif stroke["type"] in ["rectangle", "ellipse"]:
            p1 = stroke["start"]
            p2 = stroke["end"]

            if point_converter:
                p1 = point_converter(p1)
                p2 = point_converter(p2)

            rect = QtCore.QRectF(p1, p2).normalized()

            return rect

        elif stroke["type"] == "txt":
            point = stroke["position"]

            if point_converter:
                point = point_converter(point)

            font = QtGui.QFont()
            font.setPointSize(stroke.get("font_size", 24))

            metrics = QtGui.QFontMetrics(font)

            rect = metrics.boundingRect(stroke["txt"])

            rect.moveTo(point.x(), point.y() - rect.height())

            return QtCore.QRectF(rect)

    def draw_selection(self, painter, stroke, point_converter=None):
        rect = self.get_stroke_rect(stroke, point_converter)

        if rect is None:
            return

        pen = QtGui.QPen(QtGui.QColor(0, 170, 255))

        pen.setWidth(2)
        pen.setStyle(QtCore.Qt.DashLine)

        painter.setPen(pen)

        painter.drawRect(rect)

    def undo(self):
        if not self.undo_history:
            return

        action = self.undo_history.pop()

        # CREATE
        if action["type"] == "create":
            frame = action["frame"]
            stroke_id = action["stroke_id"]

            if frame in self.strokes:
                self.strokes[frame] = [
                    stroke for stroke in self.strokes[frame] if stroke["id"] != stroke_id
                ]
                if not self.strokes[frame]:
                    del self.strokes[frame]

            return

        # MOVE
        if action["type"] == "move":
            stroke = self.find_stroke(action["stroke_id"])

            if stroke:
                stroke.clear()
                stroke.update(copy.deepcopy(action["old_data"]))

            return

        # ERASE
        if action["type"] == "erase":
            self.strokes[action["frame"]] = copy.deepcopy(action["strokes"])

            return

    def find_stroke(self, stroke_id):
        """
        Find stroke by UUID.
        """

        for frame_strokes in self.strokes.values():

            for stroke in frame_strokes:

                if stroke.get("id") == stroke_id:
                    return stroke

        return None

    def hit_pencil(self, stroke, point):
        radius_x = self.eraser_radius / float(self.image_width)
        radius_y = self.eraser_radius / float(self.image_height)

        segments = list()
        current_segment = list()

        for p in stroke["points"]:
            dx = (p[0] - point[0]) / radius_x
            dy = (p[1] - point[1]) / radius_y

            inside = (dx * dx + dy * dy) <= 1.0

            if inside:
                if len(current_segment) > 1:
                    segments.append(
                        {
                            "id": self.generate_id(),
                            "type": "pencil",
                            "points": current_segment,
                            "color": stroke["color"],
                            "thickness": stroke["thickness"],
                        }
                    )

                current_segment = list()

            else:
                current_segment.append(p)

        if len(current_segment) > 1:
            segments.append(
                {
                    "id": self.generate_id(),
                    "type": "pencil",
                    "points": current_segment,
                    "color": stroke["color"],
                    "thickness": stroke["thickness"],
                }
            )

        return segments

    def hit_rectangle(self, stroke, point):

        p1 = stroke["start"]
        p2 = stroke["end"]

        xmin = min(p1[0], p2[0])
        xmax = max(p1[0], p2[0])

        ymin = min(p1[1], p2[1])
        ymax = max(p1[1], p2[1])

        px, py = point

        return xmin <= px <= xmax and ymin <= py <= ymax

    def hit_ellipse(self, stroke, point):

        p1 = stroke["start"]
        p2 = stroke["end"]

        cx = (p1[0] + p2[0]) * 0.5
        cy = (p1[1] + p2[1]) * 0.5

        rx = abs(p2[0] - p1[0]) * 0.5
        ry = abs(p2[1] - p1[1]) * 0.5

        if rx <= 0 or ry <= 0:
            return False

        px = point[0] - cx
        py = point[1] - cy

        value = ((px * px) / (rx * rx)) + ((py * py) / (ry * ry))

        return value <= 1.0

    def hit_txt(self, stroke, point):
        bounds = stroke.get("bounds")

        if not bounds:
            return False

        # normalized mouse -> image pixels
        px = point[0] * self.image_width
        py = point[1] * self.image_height

        # normalized text position -> image pixels
        tx = bounds["x"] * self.image_width
        ty = bounds["y"] * self.image_height

        left = tx
        right = tx + bounds["width"]

        top = ty - bounds["ascent"]
        bottom = top + bounds["height"]

        return left <= px <= right and top <= py <= bottom

    def hit_stroke(self, point):

        strokes = self.get_strokes()

        for stroke in reversed(strokes):

            typed = stroke["type"]

            if typed == "txt":
                if self.hit_txt(stroke, point):
                    return stroke

            elif typed == "rectangle":
                if self.hit_rectangle(stroke, point):
                    return stroke

            elif typed == "ellipse":
                if self.hit_ellipse(stroke, point):
                    return stroke

            elif typed == "pencil":
                if self.hit_pencil_move(stroke, point):
                    return stroke
        return None

    def hit_pencil_move(self, stroke, point):

        radius = 0.01

        for p in stroke["points"]:

            dx = p[0] - point[0]
            dy = p[1] - point[1]

            if (dx * dx + dy * dy) <= (radius * radius):
                return True

        return False

    def clear(self):
        """
        Remove all strokes from current frame.
        """

        if self.current_frame is None:
            return

        # Remove Frame Data
        self.strokes.pop(self.current_frame, None)

    def clear_all(self):
        """
        Remove all sketches from all frames.
        """

        self.strokes.clear()


if __name__ == "__main__":
    pass
