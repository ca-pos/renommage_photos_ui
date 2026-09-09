import sys, os
import re

from PySide6.QtWidgets import (QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QDialog,
                               QScrollArea, QWidget)
from PySide6.QtGui import (QPalette, QScreen)
from PySide6.QtCore import (Signal, Slot, Qt)

from PhotoExif import PhotoExif
from constants import *

# class AcceptDialog(QDialog):
#     def __init__(self):
#         super().__init__()
#
#         self.buttonBox = QDialogButtonBox()
#         self.btn_dir_ok = QPushButton('Oui')
#         self.btn_dir_ok.clicked.connect(self.accept)
#         self.btn_dir_wrong = QPushButton('Non')
#         self.btn_dir_wrong.clicked.connect(self.reject)
#
#         layout_h = QHBoxLayout()
#         layout_h.addWidget(self.btn_dir_wrong)
#         layout_h.addWidget(self.btn_dir_ok)
#         layout_v = QVBoxLayout()
#         message = QLabel('Est-ce le bon répertoire ?')
#         layout_v.addWidget(message)
#         layout_v.addLayout(layout_h)
#         self.setLayout(layout_v)

#################################################################################

class GalleryDialog(QDialog):
    def __init__(self, pictures):
        super().__init__()

        from Gallery import Gallery # imported here to avoid circular import problem

        self.selected_pictures = dict()

        self._pictures = pictures
        controls = Controls()
        self.gallery = Gallery(controls, self._pictures)
        display = Display(self.gallery)
        layout = QVBoxLayout()
        layout.addWidget(display)
        layout.addWidget(controls)
        screen_size = QScreen.availableGeometry(QApplication.primaryScreen())
        self.setMinimumSize(QSize(screen_size.width(), DISPLAY_HEIGHT))
        self.setStyleSheet('background-color: #666')
        self.setLayout(layout)

        controls.close_gallery.connect(self.update_and_close)

    def update_and_close(self):
        for index in range(len(self._pictures)):
            rank = index + 1
            if not  self.w2(rank).is_blurred:
                original_name = self.w2(rank).exif.original_name+self.w2(rank).exif.original_ext
                date = self.w2(rank).exif.date
                compressed_date = self.w2(rank).exif.compressed_date
                self.selected_pictures[original_name] = (date, compressed_date)
        self.close()

    def w2(self, rank):
        return self.gallery.w(rank)

#################################################################################

class Display(QScrollArea):
    def __init__(self, gallery) -> None:
        super().__init__()

        self.setBackgroundRole(QPalette.Dark)
        self.setStyleSheet('background-color: #808080')
        self.setWidget(gallery)
        self.setWidgetResizable(True)

#################################################################################

class Controls(QWidget):
    sliced = Signal(bool)
    cleared = Signal(bool)
    close_gallery = Signal(bool)

    def __init__(self):
        super().__init__()

        btn_close_gallery = QPushButton('Quitter')
        btn_close_gallery.clicked.connect(self._close_parent)

        vbox_btn = QVBoxLayout()
        # add suffix to selection
        btn_slice_date = QPushButton('Ajouter un suffixe à la date de la sélection')
        btn_slice_date.clicked.connect(self._slice)
        # clear checked list
        btn_clear_checked_list = QPushButton('Tout désélectionner')
        btn_clear_checked_list.clicked.connect(self._clear_selection)

        # add widgets to vboxes
        vbox_btn.addWidget(btn_slice_date)
        vbox_btn.addWidget(btn_clear_checked_list)

        layout = QGridLayout()
        self.setLayout(layout)
        groupbox_op = QGroupBox('Opérations sur la sélection')
        groupbox_op.setObjectName('ctrl1')
        groupbox_op.setFixedSize(int(.3 * H_SIZE), 100)
        layout.addWidget(groupbox_op)
        layout.setColumnStretch(1, 5)

        # add vboxes to hbox
        hbox = QHBoxLayout()
        hbox.addLayout(vbox_btn)
        # set self layout
        self.setLayout(hbox)
        hbox.addStretch()

        layout.addWidget(btn_close_gallery, 0, 1, 2, 1, alignment=Qt.AlignmentFlag.AlignHorizontal_Mask)
        groupbox_op.setLayout(hbox)

    # --------------------------------------------------------------------------------
    @Slot(result=bool)
    def _close_parent(self, event):
        self.close_gallery.emit(True)

    @Slot(result=bool)
    def _clear_selection(self, event: int):
        self.cleared.emit(True)

    @Slot(result=bool)
    def _slice(self, event: int):
        self.sliced.emit(True)

#################################################################################

class OriginalName:
    """Try to find the original name of the file"""

    def __init__(self, file):
        """
        :param current_name: name of the file in which the original is to be found
        """
        self._original_name = ''
        regex = (r'.*(_DSC\d\d\d\d)\D', r'.*(DSC_\d\d\d\d)\D', r'.*(IMG_\d{4,4})\D')
        for r in regex:
            on = re.findall(r, file)
            if on:
                self._original_name = on[0]
                break
            else:
                exif = PhotoExif(file)
                self._original_name = 'XXX_0000'


    @property
    def original_name(self):
        """Essai de retrouver le nom original du fichier"""
        return self._original_name

#################################################################################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    os.chdir('/home/camille/Images/_Importation/CARTE/')
    pictures = os.listdir('./tmp')
    pictures = ['./tmp/' + val for val in pictures]
    pictures.sort()

    gallery_dialog = GalleryDialog(pictures)
    gallery_dialog.show()

    sys.exit(app.exec())