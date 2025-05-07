# import os
# from pathlib import Path
import os
# import pyexiv2
import random
import re
from functools import partial

from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QGroupBox, QLabel, QPushButton, QHBoxLayout
from PySide6.QtGui import QPixmap, QTransform, QPalette, QKeyEvent, QIcon
from PySide6.QtCore import Qt, Signal, Slot, QObject, QFile, QTextStream, QIODevice

from PySide6.QtWidgets import QScrollArea, QCheckBox, QDialog, QDialogButtonBox
from PIL import Image, ImageFilter

from PhotoExif import *

from constants import *
# from icons import *

#################################################################################
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
    def __init__(self, pictures):
        super().__init__()

        controls = Controls()
        gallery = Gallery(controls, pictures)
        display = Display(gallery)
        layout = QVBoxLayout()
        layout.addWidget(display)
        layout.addWidget(controls)
        self.setLayout(layout)

#################################################################################
class Display(QScrollArea):
    def __init__(self, gallery) -> None:
        super().__init__()

        f = QFile('~/Programmes/011.(PY)-renommage_photos_ui/renommage_photos_ui/style.qss')
        f.open(QIODevice.ReadOnly)
        self.setStyleSheet(QTextStream(f).readAll())

        self.setBackgroundRole(QPalette.Dark)
        self.setStyleSheet('background-color: #303030')
        self.setWidget(gallery)
        self.setWidgetResizable(True)
#################################################################################
class Gallery(QWidget):
    """
    Gallery creates a widget that contains Thumbnails object

    Args:
        QWidget: QWidget

    Signals:
        When a Thumbnails object is changed (on a signal emitted by the Thumbnails object) the Gallery object is updated and a changed signal (an empty str) is emitted

    Class Variables:
        hidden_list: list of the thumbnails to be displayed blurred
    """

    def __init__(self, controls, fichier_raw):
        """
        __init__ creates Gallery objects
        """
        super().__init__()
        # development only ---------------------------------------------------------
        # fichier_raw = [str(fichier) for fichier in Path('./pictures').glob('*.NEF')]
        # fichier_raw = sorted(fichier_raw)
        # ----------------------------------------------------------------------------
        self.first = -1
        self.last = -1
        self.list_set = False
        self.checked_list = list()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.addStretch()
        self.setLayout(self.layout)
        # create Thumbnails and add to Gallery
        for i_thumb in range(len(fichier_raw)):
            photo_file = fichier_raw[i_thumb]
            th = Thumbnails(photo_file)
            self.layout.addWidget(th)
            th.set_bg_color(self.assign_bg_color(th.rank))
            # process signals from thumbnails
            th.selected.connect(partial(self.thumb_selected, th.rank))
            th.colored.connect(partial(self.change_group_bg_color, th.rank))
        # process signals from controls
        controls.sliced.connect(self.slice_date)
        controls.cleared.connect(self.clear_selection)

    # --------------------------------------------------------------------------------
    def slice_date(self):
        if len(self.checked_list) == 0:  # no selection
            return
        first_index = self.checked_list[0]
        original_suffix = self.w(first_index).exif.date_suffix
        if not self.valid_selection(first_index, original_suffix):
            return
        if original_suffix == '':
            self.initialize_all_dates(first_index)  # replace '' with '?' & update thumbnail title

        suffix = self.get_suffix(first_index)
        for i in self.checked_list:
            self.w(i).exif.date_suffix = suffix
            self.update_thumbnail_title(i)
        self.change_group_bg_color(first_index, 0)
        self.clear_selection()

        for i in range(1, Thumbnails.count + 1):
            print(self.w(i).exif.compressed_date)
        return

    # --------------------------------------------------------------------------------
    def valid_selection(self, first_index, original_suffix) -> bool:
        print('La sélection est-elle valide ?')
        boundary = self.different_dates()
        if boundary > 0:
            print(f'Pas la même date aux rangs', {boundary - 1}, 'et', {boundary})
            return False
        if original_suffix == '' and not self.first_series_of_day(first_index):
            print(f'Le début de la sélection', {first_index}, 'ne coincide pas avec un début de date')
            return False
        if original_suffix in list(string.ascii_lowercase):
            print('La vignette n°', {original_suffix}, 'fait déjà partie d\'un groupe')
            return False
        if original_suffix == '?' and self.w(first_index - 1).exif.date_suffix == '?':
            print('Un ou plusieurs items oubliés avant', {first_index})
            return False
        return True

    # --------------------------------------------------------------------------------
    def initialize_all_dates(self, first):
        items_per_date = list()
        for i in range(1, Thumbnails.count + 1):
            if self.w(i).exif.date == self.w(first).exif.date:
                items_per_date.append(i)
        for i in items_per_date:
            self.w(i).exif.date_suffix = '?'

    # --------------------------------------------------------------------------------
    def update_thumbnail_title(self, index):
        title1 = self.w(index).get_thumbnail_title()[:-13]
        title = self.w(index).get_thumbnail_title()[-12:-1]
        title = title + self.w(index).get_date_suffix() + ')'
        print('title', title1, title)
        self.w(index).set_thumbnail_title(title1 + title)

    # --------------------------------------------------------------------------------
    def different_dates(self) -> int:
        """
        different_dates checks if the selecter items lies across date boundary

        Returns:
            int:
                -1 if date is the same for all items
                the boundary where the date change otherwise
        """
        for i in self.checked_list[1:]:
            if not self.w(i).exif.date == self.w(i - 1).exif.date:
                return i
        return -1

    # --------------------------------------------------------------------------------
    def clear_selection(self):
        for i in self.checked_list:
            self.w(i).set_selection(False)
        self.first = -1
        self.last = -1
        self.checked_list.clear()

    # --------------------------------------------------------------------------------
    def thumb_selected(self, rank: int, button_checked: bool):
        self._modifier = str(Thumbnails.modifier).split('.')[1][:-8]
        if self._modifier == 'Control':
            if not self.in_list_ok(rank):
                return
            flag = not self.w(rank).get_selection()
            self.w(rank).set_selection(flag)
            return

        print('--->', self.checked_list)

        length = len(self.checked_list)
        if length == 0:
            print('LISTE VIDE')
        if self.first == -1:
            print('On a le premier :', end=' ')
            print(rank)
            self.update_checked_list(rank)
            self.first = rank
            self.w(rank).set_selection(True)
            return
        if self.last == -1:
            if rank == self.first:  # same thumb clicked twice
                self.w(rank).set_selection(False)
                self.first = -1
                self.checked_list.clear()
                return
            print('On a le second :', end=' ')
            print(rank)
            self.update_checked_list(rank)
            tmp = self.first
            self.first = min(rank, tmp)
            self.last = max(rank, tmp)
            self.w(rank).set_selection(True)
            for i in range(self.first + 1, self.last):
                self.w(i).set_selection(True)
                self.update_checked_list(i)
            return
        else:
            print('ON CHANGE DE LISTE')
            if rank in self.checked_list:
                print('INTÉRIEUR')
            else:
                print('EXTÉRIEUR')
            for i in self.checked_list:
                self.w(i).set_selection(False)
            self.w(rank).set_selection(True)
            self.checked_list.clear()
            self.first = rank
            self.last = -1
            self.update_checked_list(rank)

    # --------------------------------------------------------------------------------
    def assign_bg_color(self, rank: int):
        if rank > 1 and self.w(rank).exif.date == self.w(rank - 1).exif.date:
            color = self.w(rank - 1).get_bg_color()
        else:
            color = self.new_color()
        return str(color)

    # --------------------------------------------------------------------------------
    def change_group_bg_color(self, rank: int, e: int):
        date = self.w(rank).exif.compressed_date
        bg_color = self.new_color()
        for i in range(1, Thumbnails.count + 1):
            if self.w(i).exif.compressed_date == date:
                self.w(i).set_bg_color(bg_color)

    # --------------------------------------------------------------------------------
    def new_color(self):
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)
        return '#%02x%02x%02x' % (red, green, blue)

    # --------------------------------------------------------------------------------
    def in_list_ok(self, rank):
        ok = list()
        ok.append(self.checked_list[0])
        ok.append(self.checked_list[-1])
        ok.append(self.checked_list[0] - 1)
        ok.append(self.checked_list[-1] + 1)
        if not rank in ok:
            print('Il y a un trou')
            return False
        if rank in ok[:-2]:
            rank = -rank
        self.update_checked_list(rank)
        return True

    # --------------------------------------------------------------------------------
    def first_series_of_day(self, first_index: int):
        if first_index == 1:
            return True
        if not self.w(first_index).exif.date == self.w(first_index - 1).exif.date:
            return True
        return False

    # --------------------------------------------------------------------------------
    def get_suffix(self, first_index):
        if self.first_series_of_day(first_index):
            return 'a'
        else:
            previous = self.w(first_index - 1).exif.date_suffix
            print('prev1', previous)
            if not previous:
                print('Erreur de début')
                return ''
            return self.get_next_letter(previous)

    # --------------------------------------------------------------------------------
    def get_next_letter(self, letter):
        letters = string.ascii_lowercase
        print('gnext', letter, letters)
        return letters[letters.index(letter) + 1]

    # --------------------------------------------------------------------------------
    def update_checked_list(self, item: int):
        if item == 0:
            print('item == 0, est-ce normal ?')
            return
        if item > 0:
            self.checked_list.append(item)
        if item < 0:
            item = -item
            self.checked_list.remove(item)
        self.checked_list.sort()
        print('upd lst', self.checked_list)

    # --------------------------------------------------------------------------------
    def w(self, rank: int):
        return self.layout.itemAt(rank).widget()

    # --------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------
    def update_next_item_date(self, original_date, suffix):
        next_suffix = self.get_next_letter(suffix)
        first = -1
        for i in range(1, Thumbnails.count + 1):
            if self.w(i).exif.compressed_date == original_date:
                if first == -1:
                    first = i
                self.update_thumbnail_date(i, next_suffix)
        print('i', first)

    # --------------------------------------------------------------------------------
    def update_thumbnail_date(self, i, suffix):
        # update suffix
        self.w(i).exif.date_suffix = suffix
        # update title
        thumbnail_title = self.w(i).get_thumbnail_title()[:-1] + suffix + ')'
        self.w(i).set_thumbnail_title(thumbnail_title)
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

    def __init__(self, photo):
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
        self._full_path_tmp = TMP_DIR + self.exif.original_name + JPG_EXT
        self._full_path_tmp_blurred = TMP_DIR + self.exif.original_name + BLURRED + JPG_EXT
        Thumbnails.count += 1
        self.rank = Thumbnails.count    # used in gallery to access this thumbnail

        on = OriginalName(self._full_path_tmp)
        reversed_date = '/'.join(list(reversed(self.exif.date.split(' ')))) if self.exif.date else ''
        self.thumbnail_title = on.original_name + '  (' + reversed_date + self.exif.date_suffix + ')'
        self._label = QLabel(self)
        self._label.setStyleSheet('margin: 0px 0px 5px 0px')
        print('sss', self._full_path_tmp)
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
class Controls(QWidget):
    sliced = Signal(bool)
    cleared = Signal(bool)

    def __init__(self):
        super().__init__()

        # vbox_lbl = QVBoxLayout()
        vbox_btn = QVBoxLayout()
        # add suffix to selection
        btn_slice_date = QPushButton('Ajouter un suffixe à la date de la sélection')
        # btn_slice_date.setFixedSize(BUTTON_V_SIZE, BUTTON_V_SIZE)
        btn_slice_date.clicked.connect(self._slice)
        # clear checked list
        btn_clear_checked_list = QPushButton('Tout désélectionner')
        # btn_clear_checked_list.setFixedSize(BUTTON_V_SIZE, BUTTON_V_SIZE)
        btn_clear_checked_list.clicked.connect(self._clear_selection)

        # add widgets to vboxes
        vbox_btn.addWidget(btn_slice_date)
        vbox_btn.addWidget(btn_clear_checked_list)

        layout = QGridLayout()
        self.setLayout(layout)
        groupbox_op = QGroupBox('Opérations')
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

        groupbox_op.setLayout(hbox)

    # --------------------------------------------------------------------------------
    @Slot(result=bool)
    def _clear_selection(self, event: int):
        self.cleared.emit(True)

    @Slot(result=bool)
    def _slice(self, event: int):
        self.sliced.emit(True)
#################################################################################
class OriginalName:
    '''Try to find the original name of the file'''
    def __init__(self, current_ext):
        """
        :param current_name: name of the file in which the original is to be found
        """
        self._original_name = ''
        regex = (r'.*(_DSC\d\d\d\d)\D', r'.*(DSC_\d\d\d\d)\D', r'.*(IMG_\d{4,4})\D')

        for r in regex:
            on = re.findall(r, current_ext)
            if on:
                self._original_name = on[0]
                break
            else:
                self._original_name = 'XXX_0000'

    @property
    def original_name(self):
        """Essai de retrouver le le nom original du fichier"""
        return self._original_name
#################################################################################
