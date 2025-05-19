import random
import string

# import io
# # from io import BytesIO

from functools import partial

from PySide6.QtWidgets import (QWidget, QHBoxLayout)
# from PySide6.QtGui import QPixmap, QTransform, QPalette, QIcon, QScreen
# from PySide6.QtCore import Qt, Signal, Slot
# from PIL import ImageFilter, ImageQt

from Thumbnails import Thumbnails

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
            new_gallery = False if i_thumb else True    # if new_gallery, restart thumbnails count
            photo_file = fichier_raw[i_thumb]
            th = Thumbnails(photo_file, new_gallery)
            self.layout.addWidget(th)
            # print('iii', self.layout.indexOf(th), th.rank)
            th.set_bg_color(self.assign_bg_color(th.rank))
            # process signals from thumbnails
            th.selected.connect(partial(self.thumb_selected, th.rank))
            th.colored.connect(partial(self.change_group_bg_color, th.rank))
        # process signals from controls
        controls.sliced.connect(self.slice_date)
        controls.cleared.connect(self.clear_selection)

        # b = self.layout.takeAt(3)
        # b.widget().deleteLater()

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


