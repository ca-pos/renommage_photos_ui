import base64
import io
from functools import partial
#
from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox)
# from PySide6.QtGui import QPalette, QScreen
from PySide6.QtGui import (QPixmap, QIcon, QTransform)
from PySide6.QtCore import (Slot, Signal, Qt)
#
from PIL import (ImageQt, ImageFilter)
#
from PhotoExif import *
from CustomClasses import OriginalName
from ImageViewer import ImageViewer
#
from icons import (active_yes, color)
from constants import *
#


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
    active_yes_pix = ''
    color_pix = ''

    def __init__(self, photo, new_gallery):
        """
        __init__ creates Thumbnails objects

        Args:
            photo: str
                path to RAW file
            blur: str
                whether the displayed JPEG should be blurred: clear = empty string, blurred = BLURRED constant

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
        if new_gallery:
            Thumbnails.count = 0    # new gallery, restart thumbnails count
            Thumbnails.active_yes_pix = self.decode_base64(active_yes)
            Thumbnails.color_pix = self.decode_base64(color)
        self.exif = PhotoExif(photo)
        self.bg_color = '#bbb'  #maybe useless, to be checked
        self.is_selected = False
        self._full_path_tmp = TMP_DIR + self.exif.original_name + JPG_EXT
        self._full_path_tmp_blurred = TMP_DIR + self.exif.original_name + BLURRED + JPG_EXT
        Thumbnails.count += 1
        self.rank = Thumbnails.count  # used in gallery to access this thumbnail

        self.zoom = ImageViewer(self._full_path_tmp, self.rank)

        original_name = OriginalName(self._full_path_tmp)
        reversed_date = '/'.join(list(reversed(self.exif.date.split(' ')))) if self.exif.date else ''
        self.thumbnail_title = original_name.original_name + '  (' + reversed_date + self.exif.date_suffix + ')'
        self._label = QLabel(self)
        self._label.setStyleSheet('margin: 0px 0px 5px 0px')
        self.set_pixmap(self._full_path_tmp)

        # show/hide button (afficher/masquer)
        self.show_hide_btn = QPushButton('')
        self.update_hide_button(False)
        self.show_hide_btn.setCheckable(True)
        self.show_hide_btn.setFixedSize(MASK_BUTTON_H_SIZE, BUTTON_V_SIZE)
        self.show_hide_btn.clicked.connect(self.hide)

        # 100% zoom button
        self.zoom_btn = QPushButton()
        self.zoom_btn.setText('Zoom')
        # self.zoom_btn.setCheckable(True)
        self.zoom_btn.setStyleSheet('margin-left: 4px; background-color: #6e6')
        self.zoom_btn.setFixedSize(MASK_BUTTON_H_SIZE, BUTTON_V_SIZE)
        self.zoom_btn.clicked.connect(self.show_zoom)

        # change bg color pushbutton
        self.change_bg_color_btn = QPushButton()
        self.change_bg_color_btn.setStyleSheet('border-radius: 10px; border: 0; margin-right: 4px')
        self.change_bg_color_btn.setIcon(QIcon(QPixmap(self.color_pix)))
        self.change_bg_color_btn.setFixedSize(QSize(BUTTON_V_SIZE+10, BUTTON_V_SIZE))
        self.change_bg_color_btn.setIconSize(QSize(BUTTON_V_SIZE, BUTTON_V_SIZE))
        self.change_bg_color_btn.clicked.connect(self._change_color)

        # checkbox to select thumbnails
        self.select = QPushButton()
        self.select.setFixedSize(BUTTON_V_SIZE, BUTTON_V_SIZE)
        self.select.clicked.connect(self._selection)
        self.select.setStyleSheet(f'background-color: {self.bg_color}')
        self.select.setIconSize(QSize(ICON_H_SIZE, ICON_V_SIZE))
        self.set_selection(False)

        layout = QGridLayout()
        self.setLayout(layout)

        self.groupbox = QGroupBox(self.thumbnail_title)
        self.groupbox.setObjectName('thumb')
        self.groupbox.setFixedHeight(self._pixmap.height() + self.show_hide_btn.height() + 45)
        self.groupbox.setFixedWidth(int(1.0 * self._pixmap.width()))
        layout.addWidget(self.groupbox)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        self.groupbox.setLayout(vbox)
        vbox.addWidget(self._label)
        hbox.addWidget(self.show_hide_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        hbox.addWidget(self.zoom_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        hbox.addStretch()
        hbox.addWidget(self.change_bg_color_btn, alignment=Qt.AlignmentFlag.AlignRight)
        hbox.addWidget(self.select, alignment=Qt.AlignmentFlag.AlignRight)
        vbox.addLayout(hbox)
        vbox.setSpacing(0)
        vbox.addStretch()

    # --------------------------------------------------------------------------------
    def get_date_suffix(self):
        return self.exif.date_suffix

    # --------------------------------------------------------------------------------
    def get_thumbnail_title(self):
        return self.thumbnail_title

    # --------------------------------------------------------------------------------
    def set_thumbnail_title(self, title):
        self.groupbox.setTitle(title)

    # --------------------------------------------------------------------------------
    def set_selection(self, flag: bool):
        self.is_selected = flag
        if flag:
            self.select.setIcon(QIcon(QPixmap(Thumbnails.active_yes_pix)))
        else:
            self.select.setIcon(QIcon(''))

    # --------------------------------------------------------------------------------
    def get_selection(self):
        return self.is_selected

    # --------------------------------------------------------------------------------
    def blur_pixmap(self):
        if not Path(self._full_path_tmp_blurred).exists():
            img = Image.open(self._full_path_tmp)
            img = img.filter(ImageFilter.GaussianBlur(80))
            img.save(self._full_path_tmp_blurred)
        self.set_pixmap(self._full_path_tmp_blurred)

    # --------------------------------------------------------------------------------
    def get_bg_color(self):
        return self.bg_color

    # --------------------------------------------------------------------------------
    def set_bg_color(self, color: str):
        """
        set_bg_color set background color

        Args:
            color (str): color of the background
        """
        self.setStyleSheet(f'background-color: {color}')
        self.bg_color = color

    # --------------------------------------------------------------------------------
    def set_pixmap(self, pixmap_path: str):
        self._pixmap = QPixmap(pixmap_path)
        if self.exif.orientation == 'portrait':
            transform = QTransform().rotate(270)
            self._pixmap = self._pixmap.transformed(transform)
        self._pixmap = self._pixmap.scaled(PIXMAP_SCALE, Qt.AspectRatioMode.KeepAspectRatio)
        self._label.setPixmap(self._pixmap)

    # --------------------------------------------------------------------------------
    def update_hide_button(self, blur: bool):
        if blur:
            self.show_hide_btn.setStyleSheet('background-color: #e66')
            self.show_hide_btn.setText('Afficher')
        else:
            self.show_hide_btn.setStyleSheet('background-color: #6e6')
            self.show_hide_btn.setText('Masquer')

    # --------------------------------------------------------------------------------
    @Slot(result=bool)
    def _selection(self, e: int):
        self.selected.emit(True)

    @Slot(result=str)
    def _change_color(self, e: int):
        self.colored.emit(self.rank)

    @Slot(result=str)
    def hide(self):
        if self.show_hide_btn.isChecked():
            self.blur_pixmap()
            self.update_hide_button(True)
        else:
            self.set_pixmap(self._full_path_tmp)
            self.update_hide_button(False)

    @Slot()
    def show_zoom(self):
        # print('show zoom', self._full_path_tmp)
        # self.zoom.suppress.connect(self._suppress_thumb)
        self.zoom.exec()

    # @Slot()
    # def _suppress_thumb(self, thumb):
    #     print('sss', thumb)

    # --------------------------------------------------------------------------------
    @staticmethod
    def decode_base64(pix64):
        decoded_string = io.BytesIO(base64.b64decode(pix64))
        img = Image.open(decoded_string)
        img2 = ImageQt.ImageQt(img)
        return img2

