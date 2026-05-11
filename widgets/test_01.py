import sys
from PySide6.QtWidgets import QApplication, QFileDialog, QCheckBox, QVBoxLayout, QGridLayout


class SequenceFileDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. Force the dialog to use Qt's layout instead of the OS native one
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True)

        # 2. Create the checkbox
        self.seq_checkbox = QCheckBox("Show Sequences as Single File")
        self.seq_checkbox.setChecked(False)

        # 3. Access the internal layout of the dialog
        # QFileDialog uses a QGridLayout internally
        layout = self.layout()
        if isinstance(layout, QGridLayout):
            # Add the checkbox at the bottom (usually row 4 or 5)
            row_count = layout.rowCount()
            layout.addWidget(self.seq_checkbox, row_count, 0, 1, layout.columnCount())

    def is_sequence_checked(self):
        return self.seq_checkbox.isChecked()


# --- Example Usage ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = SequenceFileDialog()
    dialog.setWindowTitle("Select Image Sequence")
    dialog.setNameFilters(["Images (*.exr *.jpg *.png)", "All Files (*)"])

    if dialog.exec():
        files = dialog.selectedFiles()
        is_seq = dialog.is_sequence_checked()

        print(f"Selected Files: {files}")
        print(f"Sequence Mode Enabled: {is_seq}")

        # Logic for shot.####.exr would go here
        if is_seq and files:
            print("Processing list as a sequence...")
