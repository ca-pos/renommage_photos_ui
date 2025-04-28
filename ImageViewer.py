import sys
import os
from PySide6.QtWidgets import QApplication, QLabel, QScrollArea, QWidget, QVBoxLayout, QPushButton
from PySide6.QtGui import QGuiApplication, QImageReader, QPixmap

class ImageViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_label = QLabel()
        self._image_label.setScaledContents(True)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidget(self._image_label)
        
        btn_quit = QPushButton('Quitter')
        btn_quit.clicked.connect(self.close)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self._scroll_area)
        layout.addWidget(btn_quit)

        self.resize(QGuiApplication.primaryScreen().availableSize() * 4/5)

        fileName = './Images/IMG_4125.JPEG'
        os.chdir('/home/camille/Programmes/_brouillons')
        reader = QImageReader(fileName)
        reader.setAutoTransform(True)
        new_image = reader.read()

        self._image = new_image
        self._image_label.setPixmap(QPixmap.fromImage(self._image))
        self._scale_factor = 1.0
        self._image_label.adjustSize()
        self._scroll_area.setVisible(True)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    image_viewer = ImageViewer()
    image_viewer.show()
    sys.exit(app.exec())