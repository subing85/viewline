import sys
import os
import re
import glob
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QCheckBox,
    QStyledItemDelegate,
    QFileSystemModel,
)
from PySide6.QtCore import QSortFilterProxyModel, Qt


class SequenceDisplayDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        proxy = index.model()
        if hasattr(proxy, "_combine_sequences") and proxy._combine_sequences:
            if index.column() == 0:
                # Replace .1234. with .####.
                option.text = re.sub(
                    r"\.(\d+)\.", lambda m: "." + ("#" * len(m.group(1))) + ".", option.text
                )


class SequenceFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._combine_sequences = False
        self._seen_sequences = set()

    def setCombineSequences(self, enable):
        self._combine_sequences = enable
        self.clear_cache()

    def clear_cache(self):
        self._seen_sequences.clear()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self._combine_sequences:
            return True

        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)

        # Always show directories
        if source_model.isDir(index):
            return True

        file_name = source_model.fileName(index)
        # Match pattern: name.number.ext
        match = re.search(r"(.*)\.(\d+)\.(\w+)$", file_name)

        if match:
            # Create key: "filename.ext"
            seq_key = f"{match.group(1)}.{match.group(3)}"
            if seq_key not in self._seen_sequences:
                self._seen_sequences.add(seq_key)
                return True
            return False

        return True


class SequenceFileDialog(QFileDialog):
    def __init__(self):
        super().__init__()
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True)

        # 1. Setup Proxy
        self.proxy = SequenceFilterProxyModel(self)
        self.setProxyModel(self.proxy)

        # 2. Setup Delegate
        self.delegate = SequenceDisplayDelegate(self)
        self.setItemDelegate(self.delegate)

        # 3. Connect to the internal FileSystemModel
        # This is the secret sauce: clear cache when the folder actually changes
        source_model = self.proxy.sourceModel()
        if isinstance(source_model, QFileSystemModel):
            source_model.rootPathChanged.connect(self.proxy.clear_cache)

        # 4. UI Layout
        self.seq_checkbox = QCheckBox("Collapse Sequences (####)")
        self.seq_checkbox.toggled.connect(self.proxy.setCombineSequences)

        layout = self.layout()
        layout.addWidget(self.seq_checkbox, layout.rowCount(), 0)

    def get_full_sequence(self):
        selected = self.selectedFiles()
        if not self.seq_checkbox.isChecked() or not selected:
            return selected

        all_frames = []
        for f in selected:
            # Pattern: path/to/file.1001.exr -> path/to/file.*.exr
            pattern = re.sub(r"\.\d+\.", ".*.", f)
            all_frames.extend(glob.glob(pattern))

        return sorted(list(set(all_frames)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = SequenceFileDialog()
    if dialog.exec():
        print(f"Total Selected Files: {len(dialog.get_full_sequence())}")
