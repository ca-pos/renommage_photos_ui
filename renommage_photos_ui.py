# import os
# # import re
# # from functools import partial
# # from PySide6.QtCore import Slot, Qt, QIODevice
# #from PhotoExif import *
# from os.path import abspath, basename
# import sys
# import shutil
# import rawpy
# import imageio
# import pyexiv2
# import datetime
# import pathlib
# from functools import partial
#
# from PySide6.QtWidgets import (QMainWindow, QFileDialog, QButtonGroup)
# from PySide6.QtCore import QFile, QIODevice, QTextStream, Slot
#
# from interface import Ui_MainWindow
#
#
# from constants import *

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

        # initialize date suffix combobox. TODO: probably no needed any longer
        self.cbx_date_suffix.setPlaceholderText('Choisir')
        self.cbx_date_suffix.addItem('Aucun')
        self.cbx_date_suffix.setCurrentIndex(3)
        for suffix in range(0, 26):
            self.cbx_date_suffix.addItem(string.ascii_lowercase[suffix])

        # connect buttons
        # BTN
        self.btn_gallery.clicked.connect(self.show_gallery)                 # show gallery
        self.btn_gallery.setEnabled(False)
        self.btn_exec.clicked.connect(self.execute)                         # execute chosen task
        self.btn_exec.setEnabled(False)
        self.btn_quit.clicked.connect(self.close)                           # leave app
        self.btn_clear_output.clicked.connect(self.clear_console_output)    # clear console
        # tasks pushbuttons
        self.btn_import.clicked.connect(partial(self.prepare_task, IMPORT_TASK_ID))   # import button        
        # radiobuttons
        self.rb_nef.clicked.connect(self.type_rb_clicked)           # choose which type of picture not used yet
        self.rb_jpg.clicked.connect(self.type_rb_clicked)
        self.rb_all.clicked.connect(self.type_rb_clicked)
        # group name edit
        # self.edt_gname.editingFinished.connect(self.gname_done)     # group name entered

    @Slot()
    def prepare_task(self, btn_id):
        """
        Summary
            'prepare' common trunk for all tasks (select folder and set searched type(s) according to its content)
        Args
            btn_id: int: task id
        Return
            None
        """
        self.pictures_list = [] # force reading in 'execute' or 'show_gallery' to get rid of ancient values
        self.task_to_do = btn_id    # for later use by 'execute' function
        files_list = self.open_dir()
        if files_list:
            type_list = self.examine_list(files_list)    # find folder content, NEF, JPG, etc.
        else:   # no file in the folder ou 'NO' response from the user
            return
        self.files_list = files_list    # TODO: self.file_list could be set from self.open_dir !
        self.set_searched_type(type_list)           # set searched type according to folder content
        if self.content_info(type_list):            # display info about directory content
            self.btn_exec.setEnabled(True)          # enable exec and gallery buttons ...
            self.btn_gallery.setEnabled(True)       # unless no picture found in folder

    @Slot()
    def type_rb_clicked(self):
        pass
        # rb = self.sender()
        # self.searched_type = NEF_ID if rb.isChecked() else JPG_ID

    @Slot()
    def show_gallery(self):
        print('Show Gallery')
        if not self.pictures_list:  #self_pictures_list does not exist yet
            self.pictures_list = self.create_pictures_list()
        os.makedirs(TMP_DIR, exist_ok=True) # creates temporary folder to hold jpeg (original or from nef)
        self.get_pictures_in_tmp()
        for photo in self.pictures_list:
            name, ext = os.path.splitext(photo)
            jpeg_filename = TMP_DIR + basename(name) + JPG_EXT
            if bool(self.type_filters[NEF_TXT].match(ext)): # nef file found
                if not jpeg_filename in self.pictures_in_tmp:    # jpeg not yet in TMP_DIR
                    print(f'Création du JPEG ... {jpeg_filename}')
                    print('jjj', jpeg_filename)
                    self.create_temporary_jpeg(photo, jpeg_filename)    # create jpeg from NEF photo
            elif bool(self.type_filters[JPG_TXT].match(ext)):
                shutil.copy(photo, jpeg_filename)
            else:
                msg = f'{ext} : extension non prévue !'
                self.console_warning(msg)
        self.write_console('Liste temporaire créée')
        self.get_pictures_in_tmp()
        gallery_dialog = GalleryDialog(self.pictures_in_tmp)
        gallery_dialog.exec()

    @Slot()
    def clear_console_output(self):
        self.console.clear()

    @Slot()
    def execute(self):
        if not self.pictures_list:
            self.pictures_list = self.create_pictures_list()
        self.import_card()

    def import_card(self):
        print('Importer (tâche ', self.task_to_do, ')')

    def correct_names(self):
        pass

    def content_info(self, type_list):
        """
        provide console info about the content of the selected folder
        :param type_list: list(bool) tells which type radiobutton is checked
        :return: 'False' if no picture files in the folder, 'True' otherwise
        """
        if type_list == [False]*len(type_list):
            self.console_warning(MSG_NO_PICTURE)
            return False
        if type_list[-1]:
            self.console_warning(MSG_IMPORT_ALL)
            self.write_console(MSG_SELECT_TYPE_TO_IMPORT)
        else:
            type_ = 'NEF' if type_list[NEF_ID] else 'JPG/JPEG' if type_list[JPG_ID] else None
            self.console_warning(MSG_IMPORT_TYPE + f'\'{type_}\'')
            for rb in self.type_radiobuttons_dict.values():
                rb.setEnabled(False)
        self.write_console(MSG_PRESS_EXECUTE)
        return True

    def open_dir(self):
        """
        Summary
            Open directory containing the pictures to process
        Return
            list: list of all the files in the directory, excluding subdirectories
        """
        # open the dialog window for folder selection
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Répertoire des photos à renommer")
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setViewMode(QFileDialog.ViewMode.List)

        if file_dialog.exec():
            selected_directory = file_dialog.selectedFiles()[0]
            os.chdir(selected_directory)
            self.console.addItem( 'Contenu du répertoire : ' + selected_directory) # and display it
        else:   # cancel button was pressed by user
            return
        # display the content of the folder in console and save it in file_list
        file_list = list()
        for file in os.listdir('.'):
            if not os.path.isdir(file):
                file_list.append(abspath(file))
        file_list.sort()
        rank = 1
        for file in file_list:
            rank_str = str("{:03d}".format(rank)) + ':  '
            self.console.addItem( rank_str+basename(file))
            rank += 1

        # ask confirmation
        dlg = AcceptDialog()
        dlg.setWindowTitle('Choisir le répertoire')

        if not dlg.exec(): # not the right directory, returned list is emptied
            file_list = []

        return file_list # all files, pictures and others

    def set_searched_type(self, type_list):
        """
        set 'checked' of 'type buttons' according to the content of the directory: NEF, JPG, BOTH or NONE
        (note: the un/check job itself is done through the 'self.set_checked_type_buttons' routine)
        :param type_list: list(bool)
        :return: None
        """
        if [type_list[0]]*len(type_list) == type_list: # all values are equal either True or False
            full_type_list = [False]*(len(self.type_radiobuttons_dict) - 1)
            if type_list[0]:    # all True
                full_type_list.append(True) # 'ALL button' to be checked
            else:   # all False
                full_type_list.append(False) # no button to be checked
        else:
            full_type_list = type_list  # 'type buttons' are checked according 'type_list'
            full_type_list.append(False)    # 'ALL button' unchecked
        self.set_checked_type_buttons(full_type_list)

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
            list: selected pictures (nef, jpg, [etc., provision for adding more type in the future] or all)
        """
        pictures_list = list()
        filters = self.get_searched_type_filters()

        for file in self.files_list:
            name, ext = os.path.splitext(file)
            for index in range(len(filters)):
                if bool(filters[index].match(ext)):
                    pictures_list.append(file)

        return pictures_list

    def set_checked_type_buttons(self, full_type_list):
        """
        task buttons are set un/checked according to the value of 'full_type_list'
        :param full_type_list: list(bool)
        :return: None
        """
        for index in range(len(self.type_radiobuttons_dict)):
            self.type_radiobuttons_dict[TXT_TYPES_LIST[index]].setChecked(full_type_list[index])

    def console_warning(self, message):
        """
        Summary
            print a warning message to the console
        Args:
            message: str:
            warning message to be displayer
        Returns: None

        """
        msg = '\n====> ' + message.upper() +'\n'
        self.write_console(msg)
        # return

    def examine_list(self, file_list):
        """
        check the type of pictures in file_list, NEF, JPG, both or none
        :param file_list: list: list of pictures to check
        :return: list(bool): telling the types of files found in 'file_list'
        """
        type_list = [False]*(len(self.type_radiobuttons_dict) - 1) # will allow more types in the future
        for file in file_list:
            tmp, ext = os.path.splitext(file)
            for index in range(len(self.type_filters)):
                if bool(self.type_filters[TXT_TYPES_LIST[index]].match(ext)):  # filter
                    type_list[index] = True
            if type_list[0] and all(type_list): # type_list[0] and all others are True no need to go any further
                return type_list
        return type_list

    def write_console(self, message):
        carriage_return = '\n'
        positions = [0]  # start position
        positions += [i for i in range(len(message)) if message.startswith(carriage_return, i)] # add CR positions
        positions += [len(message)] # add end of message position

        for i in range(len(positions) - 1):
            start = positions[i] + 1 if i else positions[i]
            end = positions[i + 1]
            self.console.addItem(message[start:end])

        self.console.scrollToBottom()

    def get_pictures_in_tmp(self):
        self.pictures_in_tmp = ['./'+str(val) for val in pathlib.Path(TMP_DIR).iterdir()]
        tmp_dict = dict()
        for picture in self.pictures_in_tmp: # create a dict {datetime: picture path}
            exif = PhotoExif(picture)
            key = exif.raw_date_time
            tmp_dict[key] = picture
        sorted_tmp_dict = dict(sorted(tmp_dict.items()))    # sort dict as a function of key (i.e. datetime)
        self.pictures_in_tmp = [val for val in sorted_tmp_dict.values()] # transfer datetime sorted values to
        # self.pictures_in_tmp

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
            string_ = string_.replace("  ", " ")  # replace double spaces with single space

        return string_

    @staticmethod
    def create_temporary_jpeg(photo, jpeg_filename):
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
        imageio.imsave(jpeg_filename, jpeg_img)
        meta_data = pyexiv2.ImageMetadata(jpeg_filename)
        meta_data.read()
        key = 'Exif.Photo.DateTimeOriginal'
        meta_data[key] = datetime_taken
        meta_data.write()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    renameWindow = MainWindow()

    f = QFile("./style.qss")
    f.open(QIODevice.ReadOnly)
    app.setStyleSheet(QTextStream(f).readAll())

    renameWindow.show()
    sys.exit(app.exec())