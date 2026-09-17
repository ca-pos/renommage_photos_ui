import sys, os, random, string, re, rawpy, json
import imageio.v3 as imageio

from PySide6.QtWidgets import (QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QDialog,
                               QScrollArea, QWidget)
from PySide6.QtGui import (QPalette, QScreen)
from PySide6.QtCore import (Signal, Slot, Qt)

from PhotoExif import PhotoExif
from constants import *

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
        """
        w2: shorthand to access gallery object
        w (from gallery): shorthand to access thumbnail object (widget)
        """
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
        # add more regex if needed
        regex = (r'.*(_DSC\d\d\d\d)\D',
                 r'.*(DSC_\d\d\d\d)\D',
                 r'.*(IMG_\d{4,4})\D',
                 r'.*(XXX-\d{4,4})\D')
        for r in regex:
            on = re.findall(r, file)
            if on:
                self._original_name = on[0]
                break
            else:
                self._original_name = 'XXX_0000' # TODO:change for None or '' in future version

    @property
    def original_name(self):
        """Essai de retrouver le nom original du fichier"""
        return self._original_name
#################################################################################
class PictureWithInfo:
    """
    Receives
        file name
    Provides
        name (from camera),
        jpeg,
        thumbnail title,
        comment (that is, modified name of the file if any)
    Allows to set modifier

    NOTE: most of this code is for future versions
    """
    random_letter_part = None # probably to be removed in future version (see below create_missing_names)
    with open(IMPORT_DIR+FILE_COUNTER, 'r') as counter:
        num_part_for_random = json.load(counter)

    def __init__(self, picture):
        self._picture = picture
        self.comment, ext_ = os.path.splitext(self._picture) #keep modified name, if any, in comment field
        modifier = ''
        self._modifier = modifier # modifier is set in gallery, unknown at this stage, set it later as a property

        exif = PhotoExif(self._picture) # some infos are from picture exif
        self.name_from_camera = OriginalName(self._picture)
        if self.name_from_camera.original_name == 'XXX_0000':# TODO: to be changed in future version (see OriginalName)
            self.original_name = self.create_missing_name(exif.nikon_file_number, exif.nikon_color_space)
        else:
            self.original_name = self.name_from_camera.original_name
        try:
            with rawpy.imread(self._picture) as raw_img:
                self.jpg_img = raw_img.postprocess()
                # os.chdir(EXPORT_DIR_ABS)
                # imageio.imwrite(self.original_name+JPG_EXT, self.jpg_img)
                # os.chdir(CARD_DIR)
        except rawpy.LibRawFileUnsupportedError:
            if not ext_ == JPG_EXT:
                sys.exit(f'Fichier non pris en charge {self._picture}') # should never occur
            with open(self._picture, 'rb') as jpg_img:
                self.jpg_img = imageio.imread(self._picture)
                # os.chdir(EXPORT_DIR_ABS)
                # imageio.imwrite(self.original_name+JPG_EXT, self.jpg_img)
                # os.chdir(CARD_DIR)
        except:
            print(f'Fichier {self._picture}:exception autre que \'rawpy.LibRawFileUnsupportedError\':class '
                  f'PictureWithInfo')
        self.reversed_date = '/'.join(list(reversed(exif.date.split(' ')))) if exif.date else 'non datée'
        self.thumbnail_title = self.create_thumbnail_title()

    def create_thumbnail_title(self):
        self.reversed_date = self.reversed_date+self.modifier
        return self.name_from_camera.original_name + ' (' + self.reversed_date + ')'

    @property
    def modifier(self):
        return self._modifier

    @modifier.setter
    def modifier(self, value):
        self._modifier = value

    @staticmethod
    def create_missing_name(file_number, color_space):
        if file_number == -1:
            # next if useful only in case of randomly generated letter part (that is, not here: letter part is XXX-)
            # TODO: to be removed in future version if the XXX- solution is kept
            if not PictureWithInfo.random_letter_part:
                letter_part = 'XXX-' #self.created_random_letter_part()
                # PictureWithInfo.random_letter_part = letter_part
            else:
                letter_part = PictureWithInfo.random_letter_part
            num_part = f'{PictureWithInfo.num_part_for_random:04d}'
            PictureWithInfo.num_part_for_random += 1
        else:
            letter_part = '_DSC' if color_space == 1 else 'DSC_' if color_space == 2 else 'DSC-'
            num_part = str(file_number)

        return letter_part+num_part

    # @staticmethod
    # def created_random_letter_part():
    #     uppercase_letters = string.ascii_uppercase
    #     letters = ''
    #     while True:
    #         for index in range(3):
    #             letters += uppercase_letters[random.randint(0, 25 )]
    #         if not (letters == 'DSC' or letters == 'IMG'):
    #             return letters+'-'
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