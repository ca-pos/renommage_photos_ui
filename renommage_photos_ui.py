import datetime, json, re, os
import pathlib
import shutil
import sys
from html.parser import commentabruptclose
from os.path import (basename, isdir)

import imageio.v3 as imageio

# import matplotlib.pyplot as plt
from PIL import Image

import rawpy
import pyexiv2
from PySide6.QtCore import (Slot, QFile, QIODevice, QTextStream)
from PySide6.QtGui import (QColor)
from PySide6.QtWidgets import (QMainWindow, QButtonGroup, QListWidgetItem, QApplication)

from CustomClasses import (GalleryDialog, PictureWithInfo)
from PhotoExif import PhotoExif
from constants import *
from set_colors import *
from interface2 import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Renommage des Photos')
        self.setupUi(self)
        # variables
        self.current_folder = str()
        self.pictures_list = list()
        self.files_list = list()
        self.type_list = list()
        self.task_to_do = NO_TASK
        self.pictures_in_tmp = list()
        self.pictures_with_date_and_selection = dict()
        self.with_info_dic = dict()
        self.num_part_for_created_names = None


        # creates type filters (TODO: get rid of get_type_filters static method !
        re_nef = re.compile(r".*\.nef$", re.IGNORECASE)  # nef filter
        re_jpg = re.compile(r".*\.jpe?g$", re.IGNORECASE)  # jpg filter
        self.type_filters = {NEF_TXT: re_nef, JPG_TXT: re_jpg}

        # set text rb buttons text
        self.rb_nef.setText(NEF_TXT)
        self.rb_jpg.setText(JPG_TXT)
        self.rb_all.setText(ALL_TXT)
        # group rb buttons ...
        self.type_group = QButtonGroup(self)
        self.type_group.addButton(self.rb_nef)
        self.type_group.addButton(self.rb_jpg)
        self.type_group.addButton(self.rb_all)

        # note: if more types are added, 'rb_all' must remain the last one
        self.type_radiobuttons_dict = {NEF_TXT: self.rb_nef, JPG_TXT: self.rb_jpg, ALL_TXT: self.rb_all}

        # connect buttons
        # BTN
        self.btn_gallery.clicked.connect(self.show_gallery)                 # show gallery
        self.btn_gallery.setEnabled(False)
        self.btn_quit.clicked.connect(self.close_window)                    # leave app
        self.btn_clear_output.clicked.connect(self.clear_console_output)    # clear console
        # tasks pushbuttons
        self.btn_exec.clicked.connect(self.execute)                         # execute chosen task
        self.btn_exec.setEnabled(False)
        self.btn_import.clicked.connect(self.import_card)                   # import button

        # clear everything on start, should be useless in final
        starting_dir = os.getcwd()
        go_to_dir = CARD_DIR+TMP_DIR
        # shutil.rmtree(go_to_dir)
        os.makedirs(go_to_dir, exist_ok=True)
        os.chdir(go_to_dir)
        for file in os.listdir('.'):
            if not isdir(file):
                os.remove(file)
        dir_list  = ['_REJECT', '_BIN', '_IGNORE', '_EXPORT']
        for dir_ in dir_list:
            os.makedirs(dir_, exist_ok=True)
            os.chdir('./'+dir_)
            for file in os.listdir('.'):
                os.remove(file)
            os.chdir('../')
        os.chdir(starting_dir)

    @Slot()
    def close_window(self):
        # do some cleaning here
        self.close()

    @Slot()
    def execute(self):
        self.pictures_selection()
        self.pictures_pre_sorted()
        os.chdir(IMPORT_DIR)
        if self.num_part_for_created_names:
            with open(UTIL_FILES_DIR_ABS+FILE_COUNTER, 'w') as counter:
                json.dump(self.num_part_for_created_names, counter)
        self.write_console(MSG_END, INFO_COLOR_ID )

    @Slot()
    def show_gallery(self):
        print('Show Gallery')
        os.makedirs(TMP_DIR, exist_ok=True) # creates temporary folder to hold jpeg (original or from nef)
        self.get_pictures_in_tmp()
        for photo in self.pictures_list:
            name, ext = os.path.splitext(photo)
            jpeg_filename = TMP_DIR + basename(name)
            jpeg_fullname = jpeg_filename + JPG_EXT

            if bool(self.type_filters[NEF_TXT].match(ext)): # nef file found
                if not jpeg_fullname in self.pictures_in_tmp:    # jpeg not yet in TMP_DIR
                    self.create_temporary_jpeg(photo, jpeg_fullname)    # create jpeg from NEF photo
                    get_flag = pathlib.Path(jpeg_filename + GET_EXT)  # picture to be imported
                    get_flag.touch()
            elif bool(self.type_filters[JPG_TXT].match(ext)):
                shutil.copy(photo, jpeg_fullname)
                get_flag = pathlib.Path(jpeg_filename + GET_EXT)    # picture to be imported
                get_flag.touch()
            else:
                msg = f'{ext} : extension non prévue !'
                self.console_warning(msg)
        self.write_console(MSG_CREATE_TMP_LIST, INFO_COLOR_ID)
        self.get_pictures_in_tmp()
        gallery_dialog = GalleryDialog(self.pictures_in_tmp)
        gallery_dialog.exec()
        self.pictures_with_date_and_selection = gallery_dialog.selected_pictures

        self.btn_exec.setEnabled(True)

    @Slot()
    def clear_console_output(self):
        self.console.clear()

    def pictures_pre_sorted(self):
        os.chdir(PRE_SORT_DIR_ABS)
        for key in self.pictures_with_date_and_selection.keys():
            base, _ = os.path.splitext(key)
            filename = self.find_file_in_list_orig(base)
            source = os.path.join(EXPORT_DIR_ABS, filename)
            #--------------------------------------------------------------------------
            #TODO: to be rewritten (removed) in future version
            # (ensure that file name comprises an XXX-, or IMG_, or _DSC pattern (nessary for renommage_photos_cli
            # to be used next in the workflow)
            with_info = PictureWithInfo(source)
            camera_name = with_info.name_from_camera.original_name
            created_camera_name = with_info.original_name
            if camera_name.startswith('XXX_'):
                base2, ext_ = os.path.splitext(source)
                temp = base2+'-'+created_camera_name+ext_
                os.rename(source, temp)
                source = temp
            #--------------------------------------------------------------------------
            decade = self.pictures_with_date_and_selection[key][1][0]
            day = self.pictures_with_date_and_selection[key][1][1]
            modifier = self.pictures_with_date_and_selection[key][1][2]
            day = day+modifier
            dest_dir = os.path.join(decade, day)
            os.makedirs(dest_dir,0o755, True)
            #---------------------------------------------------------------------------
            # TODO: see whether this is the best place to do this
            # while files are in export dir, create a dic for later use renommage_cli
            # os.chdir(EXPORT_DIR_ABS)
            name_from_camera = with_info.name_from_camera.original_name
            comment = with_info.comment
            thumb_title = with_info.thumbnail_title
            pixmap = with_info.pixmap
            self.with_info_dic[name_from_camera] = (comment, thumb_title)
            pix_file = UTIL_FILES_DIR_ABS+name_from_camera+PIX_EXT
            with open(pix_file, 'wb') as f:
                f.write(pixmap)
            # os.chdir(PRE_SORT_DIR_ABS)
            #---------------------------------------------------------------------------
            shutil.move(source, dest_dir)
        self.num_part_for_created_names = with_info.num_part_for_random

    def pictures_selection(self):
        dir_list = ['_REJECT', '_BIN', '_IGNORE', '_EXPORT']
        lst_temp = [filename for filename in os.listdir(TMP_DIR) if not filename in dir_list]
        lst_temp.sort()
        for filename in lst_temp:
            root, ext = os.path.splitext(filename)
            match ext:
                case '.GET':
                    os.chdir(CARD_DIR)
                    self.move_file(root, EXPORT_DIR, ext)
                    os.remove(TMP_DIR + filename)
                case '.REJECT':
                    os.chdir(CARD_DIR)
                    self.move_file(root, REJECT_DIR, ext)
                    os.remove(TMP_DIR + filename)
                case '.IGNORE':
                    os.chdir(CARD_DIR)
                    self.move_file(root, IGNORE_DIR, ext)
                    os.remove(TMP_DIR+filename)
                case '.JPG':
                    os.chdir(TEMP_DIR_ABS)
                    self.move_file(root, BIN_DIR, ext)
                case '_':
                    print('C\'est quoi ce fichier : ', root+ext) # TODO: change in final: warning to console
                    self.move_file(root, BIN_DIR, ext)

    def move_file(self, root, dest_dir, go_to):

        if go_to == JPG_EXT:
            file_to_move = root+go_to
        else:
            file_to_move = self.find_file_in_list_orig(root)
            base, ext_ = os.path.splitext(file_to_move)
            file_to_move = basename(base)+ext_

        to_tmp = dest_dir+file_to_move
        try:
            with open(file_to_move, 'rb') as f:
                img = f.read()
            os.remove(file_to_move)
        except:
            print('MOVE FILE PROBLEM ------------>', file_to_move, to_tmp, os.getcwd())
        with open(to_tmp, 'wb') as f:
            f.write(img)
        return

    def find_file_in_list_orig(self, root):
        for filename in self.pictures_list:
            if not root in filename:
                continue
            return filename
        return None

    def import_card(self):
        print('Importer la carte')
        self.write_console(MSG_FILE_READING, INFO_COLOR_ID)
        os.chdir(CARD_DIR)
        self.pictures_list = self.create_pictures_list()
        if self.pictures_list:
            self.write_console(MSG_CARD_READING_DONE, INFO_COLOR_ID)
        else:
            self.write_console(MSG_NO_PICTURE, WARNING_COLOR_ID)
        self.btn_gallery.setEnabled(True)

    # def content_info(self, type_list):
    #     """
    #     Summary
    #         provide console info about the content of the selected folder
    #     Args:
    #         type_list:
    #             list(bool) tells which type radiobutton is checked
    #     Returns:
    #         'False' if no picture files in the folder, 'True' otherwise
    #     """
    #     if type_list == [False]*len(type_list):
    #         self.console_warning(MSG_NO_PICTURE)
    #         return False
    #     if type_list[-1]:
    #         self.console_warning(MSG_IMPORT_ALL)
    #         self.write_console(MSG_SELECT_TYPE_TO_IMPORT)
    #     else:
    #         type_ = 'NEF' if type_list[NEF_ID] else 'JPG/JPEG' if type_list[JPG_ID] else None
    #         self.console_warning(MSG_IMPORT_TYPE + f'\'{type_}\'')
    #         for rb in self.type_radiobuttons_dict.values():
    #             rb.setEnabled(False)
    #     self.write_console(MSG_PRESS_EXECUTE)
    #     return True
    #
    # def set_searched_type(self, type_list):
    #     """
    #     set 'checked' of 'type buttons' according to the content of the directory: NEF, JPG, BOTH or NONE
    #     (note: the un/check job itself is done through the 'self.set_checked_type_buttons' routine)
    #     :param type_list: list(bool)
    #     :return: None
    #     """
    #     if [type_list[0]]*len(type_list) == type_list: # all values are equal either True or False
    #         full_type_list = [False]*(len(self.type_radiobuttons_dict) - 1)
    #         if type_list[0]:    # all True
    #             full_type_list.append(True) # 'ALL button' to be checked
    #         else:   # all False
    #             full_type_list.append(False) # no button to be checked
    #     else:
    #         full_type_list = type_list  # 'type buttons' are checked according 'type_list'
    #         full_type_list.append(False)    # 'ALL button' unchecked
    #     self.set_checked_type_buttons(full_type_list)

    def get_searched_type_filters(self):
        """
        Summary
            search across type (nef, jpg, etc.) radiobuttons which one, if any, is checked; if no buttons was checked
            this means that the 'all types' radiobutton was checked (since, one button was necessarily checked)

        Return
            filter(s) for the searched type (regular expression) or the list of filters if all types are to be searched
        """
        filters_list = self.get_type_filters()
        all_filters = list()
        for filter_ in filters_list.values():
            all_filters.append(filter_)

        for index in range(len(self.type_radiobuttons_dict)-1):
            if self.type_radiobuttons_dict[TXT_TYPES_LIST[index]].isChecked():
                return [filters_list[TXT_TYPES_LIST[index]]]
        return all_filters

    def create_pictures_list(self):
        """
        Summary
            read 'self.file_list', applies filter(s), and writes 'file' in 'pictures_list' if match
        Return
            list: selected pictures (nef, jpg, [etc., provision for adding more types in the future] or all)
        """
        pictures_list = list()
        filters = self.get_searched_type_filters()

        for file in os.listdir(CARD_DIR):
            if os.path.isdir(file):
                continue
            base, ext_ = os.path.splitext(file)
            not_a_picture = True
            for index in range(len(filters)):
                if bool(filters[index].match(ext_)):
                    not_a_picture = False
                    file = self.normalize_name_and_ext(file)
                    pictures_list.append(file)
                    self.write_console(file)    # display picture_list in console
            if not_a_picture:
                self.console_warning(f'"{file}": n\'est pas un fichier image ')
                continue
            # with_info = PictureWithInfo(file)
            # with_info.modifier = 'a'
            # print('credat', with_info.create_thumbnail_title())
        return pictures_list    # source files

    # def set_checked_type_buttons(self, full_type_list):
    #     """
    #     task buttons are set un/checked according to the value of 'full_type_list'
    #     :param full_type_list: list(bool)
    #     :return: None
    #     """
    #     for index in range(len(self.type_radiobuttons_dict)):
    #         self.type_radiobuttons_dict[TXT_TYPES_LIST[index]].setChecked(full_type_list[index])
    #
    def console_warning(self, message):
        """
        Summary
            print a warning message to the console
        Args:
            message: str:
            warning message to be displayed
        Returns: None

        """
        msg = '\n====> ' + message.upper() +'\n'
        self.write_console(msg, WARNING_COLOR_ID)
        # return

    # def examine_list(self, file_list):
    #     """
    #     check the type of pictures in file_list, NEF, JPG, both or none
    #     :param file_list: list: list of pictures to check
    #     :return: list(bool): telling the types of files found in 'file_list'
    #     """
    #     type_list = [False]*(len(self.type_radiobuttons_dict) - 1) # will allow more types in the future
    #     for file in file_list:
    #         tmp, ext = os.path.splitext(file)
    #         for index in range(len(self.type_filters)):
    #             if bool(self.type_filters[TXT_TYPES_LIST[index]].match(ext)):  # filter
    #                 type_list[index] = True
    #         if type_list[0] and all(type_list): # type_list[0] and all others are True no need to go any further
    #             return type_list
    #     return type_list
    #
    def write_console(self, message, color=WHITE_ID):
        message = QListWidgetItem(message)
        message.setBackground(QColor(colors[color]))
        self.console.addItem(message)
        self.console.scrollToBottom()
        return

    def get_pictures_in_tmp(self):
        self.pictures_in_tmp = ['./'+str(val) for val in pathlib.Path(TMP_DIR).iterdir()]
        tmp_dict = dict()
        for picture in self.pictures_in_tmp: # create a dict {datetime: picture path}
            if not JPG_EXT in picture or BLURRED in picture:    # skip blurred jpeg and get_flag files
                continue
            exif = PhotoExif(picture)
            try:
                key = exif.raw_date_time #TODO: problematic if 2 pictures are taken within 1 sec (burst mode)
            except:
                msg = picture+MSG_NO_EXIF
                self.console_warning(msg)
                root, ext = os.path.splitext(picture)
                ignore_file = root + IGNORE_EXT
                os.remove(root+GET_EXT)
                with open(ignore_file, 'w') as f:
                    f.write(msg)
                continue
            tmp_dict[key] = picture

        sorted_tmp_dict = dict(sorted(tmp_dict.items()))    # sort dict as a function of key (i.e. datetime)
        self.pictures_in_tmp = [val for val in sorted_tmp_dict.values()] # transfer datetime sorted values to

    @staticmethod
    def normalize_name_and_ext(file: str) -> str:
        base, ext_ = os.path.splitext(file)
        if not ext_.isupper():
            ext_ = ext_.upper() #insure uppercase ext
        if ext_ == '.JPEG':
            ext_ = JPG_EXT  # JPEG -> JPG
        temp = base+ext_
        while temp.find(' ') >0:
            temp = temp.replace(' ', '_')
        os.rename(file, temp)
        return temp

    @staticmethod
    def get_type_filters():
        """
        regular expressions used to identify the different format of pictures (nef, jpg, etc.)
        :return: list of filters
        """
        re_nef = re.compile(r".*\.nef$", re.IGNORECASE)  # nef filter
        re_jpg = re.compile(r".*\.jpe?g$", re.IGNORECASE)  # jpg filter
        # filters = [re_nef, re_jpg]
        filters = {NEF_TXT: re_nef, JPG_TXT: re_jpg}
        # for v in filters.values():
        #     print(v)
        # exit(6)
        return filters

    @staticmethod
    def suppress_spaces(string_):
        """
        suppress leading, and trailing in a string and replaces series of 2+ spaces by a single one
        :param string_: string in which extra spaces are to be removed
        :return: string with extra spaces removed
        """
        while string_[0] == ' ':  # get rid of leading spaces
            string_ = string_[1:len(string_)]
        while string_[len(string_) - 1] == ' ':  # get rid of trailing spaces
            string_ = string_[0:len(string_) - 1]
        while string_.find('  ') > 0:
            string_ = string_.replace('  ', ' ')  # replace double spaces with single space
        return string_

    @staticmethod
    def create_temporary_jpeg(photo, jpeg_fullname):
        """
        Summary
            create temporary jpeg: Creates temporary jpeg pictures from NEF. Needed for Gallery
        """
        photo_exif = PhotoExif(photo)
        year, month, day, hour, minute, second = list(map(int, photo_exif.date_time.split()))
        datetime_taken = datetime.datetime(year, month, day, hour, minute, second)

        with rawpy.imread(photo) as raw:
            jpeg_img = raw.postprocess()
            # thumb = raw.extract_thumb()
        imageio.imwrite(jpeg_fullname, jpeg_img)
        meta_data = pyexiv2.ImageMetadata(jpeg_fullname)
        meta_data.read()
        meta_data['Exif.Photo.DateTimeOriginal'] = str(datetime_taken)
        meta_data.write()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    renameWindow = MainWindow()

    f = QFile("./style.qss")
    f.open(QIODevice.ReadOnly)
    app.setStyleSheet(QTextStream(f).readAll())

    renameWindow.show()
    sys.exit(app.exec())