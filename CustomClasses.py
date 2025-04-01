from pathlib import Path

import pyexiv2
import random
import string
from functools import partial

from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QGroupBox, QLabel, QPushButton, QHBoxLayout
from PySide6.QtGui import QPixmap, QTransform, QPalette, QKeyEvent, QIcon
from PySide6.QtCore import Qt, Signal, Slot, QObject
from PySide6.QtWidgets import QScrollArea, QCheckBox, QDialog, QDialogButtonBox
from PIL import Image, ImageFilter

from PhotoExif import *

from constants import *

class AcceptDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.buttonBox = QDialogButtonBox()
        self.btn_dir_ok = QPushButton('Oui')
        self.btn_dir_ok.clicked.connect(self.accept)
        self.btn_dir_wrong = QPushButton('Non')
        self.btn_dir_wrong.clicked.connect(self.reject)

        layout_h = QHBoxLayout()
        layout_h.addWidget(self.btn_dir_wrong)
        layout_h.addWidget(self.btn_dir_ok)
        layout_v = QVBoxLayout()
        message = QLabel('Est-ce le bon répertoire ?')
        layout_v.addWidget(message)
        layout_v.addLayout(layout_h)
        self.setLayout(layout_v)

#################################################################################
class GalleryDialog(QDialog):
    def __init__(self):
        super().__init__()
#################################################################################
class Display(QScrollArea):
    def __init__(self, gallery) -> None:
        super().__init__()
        # self.setBackgroundRole(QPalette.Dark)
        self.setStyleSheet('background-color: #303030')
        #self.setWidget(gallery)
        self.setWidgetResizable(True)
#################################################################################
class Thumbnails(QWidget):
    """
    Thumbnails summary: Thumbnails object comprised
        - a title (original name of the image from exif data),
        - the JPEG embedded in the RAW file,
        - a Show (Afficher) / Hide (Masquer) checkable pushbutton,
        - a checkbox for thumbnail selection.
    JPEG of hidden thumbnails are blurred.

    Args:
        QWidget: QWidget

    Signals:
        When status is changed (hidden/shown) a changed signal is emitted which contains the exif original name (stem)
    """
    selected = Signal(bool)
    colored = Signal(str)
    modifier = Qt.KeyboardModifier.NoModifier
    count: int = 0

    def __init__(self, photo: str):
        """
        __init__ creates Thumbnails objects

        Args:
            photo: str
                path to RAW file
            blur: str
                whether or not the displayed JPEG should be blurred: clear = empty string, blurred = BLURRED constant

            id: int
                id number

        Attributes:
            id: int
                id number
            exif: <RenameCls.PhotoExif>
                exif data (of the original RAW file) needed for the present program
            bg_color: int
                background color of the Thumbnails

        Methods:
            set_bg_color(color: str)
                set background color to "color"
        """
        super().__init__()
        self.exif = PhotoExif(photo)
        self.bg_color = '#bbb' #maybe useless, to check
        self.is_selected = False
        self._full_path_tmp = TMP_DIR + self.exif.original_name + '.jpeg'
        self._full_path_tmp_blurred = TMP_DIR + self.exif.original_name + BLURRED + '.jpeg'
        Thumbnails.count += 1
        self.rank = Thumbnails.count    # used in gallery to acces this thumbnail

        # self._thumbnail_title = ''
        self.thumbnail_title = self.exif.original_name + '  ('  + self.exif.date.replace(' ', '/') + ')'
        reversed_date = '/'.join(list(reversed(self.exif.date.split(' '))))
        self.thumbnail_title = self.exif.original_name + '  (' + reversed_date + self.exif.date_suffix + ')'

        self._label = QLabel(self)
        self._label.setStyleSheet('margin: 0px 0px 5px 0px')
        self.set_pixmap(self._full_path_tmp)

        # create the show/hide button (afficher/masquer)
        self.btn = QPushButton('')
        self.update_hide_button(False)
        self.btn.setCheckable(True)
        self.btn.setFixedSize(MASK_BUTTON_H_SIZE, BUTTON_V_SIZE)
        self.btn.clicked.connect(self.hide)

        # creates a checkbox to change bg color
        self.change_bg_color = QCheckBox()
        self.change_bg_color.setObjectName('colored')
        self.change_bg_color.setFixedSize(BUTTON_V_SIZE, BUTTON_V_SIZE)
        self.change_bg_color.stateChanged.connect(self._change_color)

        # creates a checkbox to select thumbnails
        self.select = QPushButton()# QCheckBox()
        self.select.setFixedSize(BUTTON_V_SIZE, BUTTON_V_SIZE)
        self.select.clicked.connect(self._selection)
        self.select.setStyleSheet(f'background-color: {self.bg_color}')
        self.select.setIconSize(QSize(ICON_H_SIZE, ICON_V_SIZE))
        self.set_selection(False)

        layout  = QGridLayout()
        self.setLayout(layout)

        self.groupbox = QGroupBox(self.thumbnail_title)
        self.groupbox.setObjectName('thumb')
        self.groupbox.setFixedHeight(self._pixmap.height()+self.btn.height()+45)
        self.groupbox.setFixedWidth(int(1.0*self._pixmap.width()))
        layout.addWidget(self.groupbox)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        self.groupbox.setLayout(vbox)
        vbox.addWidget(self._label)
        hbox.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignLeft)
        hbox.addStretch()
        hbox.addWidget(self.change_bg_color, alignment=Qt.AlignmentFlag.AlignRight)
        hbox.addWidget(self.select, alignment=Qt.AlignmentFlag.AlignRight)
        vbox.addLayout(hbox)
        vbox.setSpacing(0)
        vbox.addStretch()
#--------------------------------------------------------------------------------
    def get_date_suffix(self):
        return self.exif.date_suffix
#--------------------------------------------------------------------------------
    def get_thumbnail_title(self):
        return self.thumbnail_title
#--------------------------------------------------------------------------------
    def set_thumbnail_title(self, title):
        self.groupbox.setTitle(title)
#--------------------------------------------------------------------------------
    def set_selection(self, flag: bool):
        self.is_selected = flag
        if flag:
            self.select.setIcon(QIcon('./icons/_active__yes.png'))
        else:
            self.select.setIcon(QIcon(''))
#--------------------------------------------------------------------------------
    def get_selection(self):
        return self.is_selected
#--------------------------------------------------------------------------------
    def blur_pixmap(self):
        if not Path(self._full_path_tmp_blurred).exists():
            img = Image.open(self._full_path_tmp)
            img = img.filter(ImageFilter.GaussianBlur(80))
            img.save(self._full_path_tmp_blurred)
        self.set_pixmap(self._full_path_tmp_blurred)
#--------------------------------------------------------------------------------
    def get_bg_color(self):
        return self.bg_color
#--------------------------------------------------------------------------------
    def set_bg_color(self, color: str):
        """
        set_bg_color set background color

        Args:
            color (str): color of the background
        """
        self.setStyleSheet(f'background-color: {color}')
        self.bg_color = color
#--------------------------------------------------------------------------------
    def set_pixmap(self, pixmap_path: str):
        self._pixmap = QPixmap(pixmap_path)
        if self.exif.orientation == 'portrait':
            transform = QTransform().rotate(270)
            self._pixmap = self._pixmap.transformed(transform)
        self._pixmap = self._pixmap.scaled(PIXMAP_SCALE, Qt.AspectRatioMode.KeepAspectRatio)
        self._label.setPixmap(self._pixmap)
#--------------------------------------------------------------------------------
    def update_hide_button(self, blur: bool):
        if blur:
            self.btn.setStyleSheet('background-color: #e66')
            self.btn.setText('Afficher')
        else:
            self.btn.setStyleSheet('background-color: #6e6')
            self.btn.setText('Masquer')
#--------------------------------------------------------------------------------
    @Slot(result=bool)
    def _selection(self, e: int):
        self.selected.emit(True)
    @Slot(result=str)
    def _change_color(self, e: int):
        self.colored.emit(self.rank)
    @Slot(result=str)
    def hide(self):
        if self.btn.isChecked():
            self.blur_pixmap()
            self.update_hide_button(True)
        else:
            self.set_pixmap(self._full_path_tmp)
            self.update_hide_button(False)
#################################################################################


