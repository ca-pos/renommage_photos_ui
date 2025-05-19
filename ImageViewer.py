# import sys
#
# from PySide6.QtWidgets import QApplication, QLabel, QScrollArea, QHBoxLayout, QVBoxLayout, QPushButton, QDialog
from PySide6.QtWidgets import (QDialog, QLabel, QScrollArea, QPushButton, QHBoxLayout, QVBoxLayout)
# from PySide6.QtGui import QGuiApplication, QImageReader, QPixmap
from PySide6.QtGui import (QGuiApplication, QImageReader, QPixmap)
# from PySide6.QtCore import Qt
from PySide6.QtCore import Qt
#
from constants import *

class ImageViewer(QDialog):
    def __init__(self, file_name, parent=None):
        super().__init__()
        self._scale_factor = 1
        self._image_label = QLabel()
        self._image_label.setScaledContents(True)
        self._original_pixmap_size = 0

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidget(self._image_label)
        
        btn_quit = QPushButton('Fermer')
        btn_quit.clicked.connect(self.close)
        btn_original_size = QPushButton('Taille originale')
        btn_original_size.clicked.connect(self._original_size)
        btn_zoom_in = QPushButton('Zoomer')
        btn_zoom_in.clicked.connect(self._zoom_in)
        btn_zoom_out = QPushButton('Dézoomer')
        btn_zoom_out.clicked.connect(self._zoom_out)
        btn_suppress = QPushButton('Supprimer')
        btn_suppress.clicked.connect(self._suppress_picture)
        btn_suppress.setEnabled(True)  # TODO: emit a signal to suppress picture in gallery


        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self._scroll_area)

        layout_btn = QVBoxLayout()
        layout_btn.addWidget(btn_original_size, alignment=Qt.AlignmentFlag.AlignTop)
        layout_btn.addWidget(btn_zoom_in,alignment=Qt.AlignmentFlag.AlignTop)
        layout_btn.addWidget(btn_zoom_out, alignment=Qt.AlignmentFlag.AlignTop)
        layout_btn.addWidget(btn_suppress, alignment=Qt.AlignmentFlag.AlignTop)
        layout_btn.addStretch()
        layout_btn.addWidget(btn_quit,alignment=Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(layout_btn)

        available_size = QGuiApplication.primaryScreen().availableSize()
        self.resize(available_size)

        reader = QImageReader(file_name)
        # reader.setAutoTransform(True)
        new_image = reader.read()

        self._image = new_image
        pixmap = QPixmap.fromImage(self._image)
        self._original_pixmap_size = pixmap.size()
        pixmap = pixmap.scaled(available_size*self._scale_factor, Qt.AspectRatioMode.KeepAspectRatio)
        self._image_label.setPixmap(pixmap)
        self._image_label.adjustSize()
        self._scroll_area.setVisible(True)

    def _zoom_in(self):
        self._scale_image(ZOOM_IN_RATIO)

    def _zoom_out(self):
        self._scale_image(ZOOM_OUT_RATIO)

    def _scale_image(self, factor):
        self._scale_factor *= factor
        if self._scale_factor > 1.0:
            self._original_size()
        else:
            new_size = self._scale_factor * self._image_label.pixmap().size()
            self._image_label.resize(new_size)

    def _original_size(self):
        self._image_label.resize(self._original_pixmap_size)
        self._scale_factor = 1.0

    def _suppress_picture(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    image_viewer = ImageViewer('/home/camille/Programmes/_brouillons/Images/IMG_4125.JPEG')
    image_viewer.show()
    sys.exit(app.exec())