#import string
import sys
import os
import shutil
import re
import rawpy
from os.path import abspath, splitext, basename
#from functools import partial

from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QButtonGroup, QDialog, QDialogButtonBox,
                               QHBoxLayout, QVBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import Slot, Qt, QIODevice

from interface import Ui_MainWindow

from PhotoExif import *
from CustomClasses import *

from constants import *

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Renommage des Photos')
        self.setupUi(self)
        # variables
        self.pictures_list = list()
        self.current_folder = str()
        self.task_to_do = NO_TASK

        # set rb buttons text
        self.rb_nef.setText(NEF_TXT)
        self.rb_jpg.setText(JPG_TXT)
        self.rb_all.setText(ALL_TXT)
        # group rb buttons ...
        self.type_group = QButtonGroup(self)
        self.type_group.addButton(self.rb_nef)
        self.type_group.addButton(self.rb_jpg)
        self.type_group.addButton(self.rb_all)
        # set rb buttons ID
        self.type_group.setId(self.rb_nef, NEF_ID)
        self.type_group.setId(self.rb_jpg, JPG_ID)
        self.type_group.setId(self.rb_all, ALL_ID)

        # note: if more types are added, 'rb_all' must remain the last one
        self.type_radiobuttons_list = [self.rb_nef, self.rb_jpg, self.rb_all]

        # initialize date suffix combobox
        self.cbx_date_suffix.setPlaceholderText('Choisir')
        self.cbx_date_suffix.addItem('Aucun')
        self.cbx_date_suffix.setCurrentIndex(3)
        for suffix in range(0, 26):
            self.cbx_date_suffix.addItem(string.ascii_lowercase[suffix])

        # connect buttons
        # BTN
        self.btn_gallery.clicked.connect(self.show_gallery)                 # show gallery
        self.btn_exec.clicked.connect(self.execute)                         # execute chosen task
        self.btn_quit.clicked.connect(self.close)                           # leave app
        self.btn_clear_output.clicked.connect(self.clear_console_output)    # clear console
        # BTN tasks
        self.btn_import.clicked.connect(partial(self.prepare_task, IMPORT_TASK_ID))   # import button        
        # RB
        self.rb_nef.clicked.connect(self.type_rb_clicked)                       # choose which type of picture
        self.rb_jpg.clicked.connect(self.type_rb_clicked)
        self.rb_all.clicked.connect(self.type_rb_clicked)

        self.edt_gname.editingFinished.connect(self.gname_done)             # group name entered

    @Slot()
    def prepare_task(self, btn_id):
        self.task_to_do = btn_id
        file_list = self.open_dir()
        type_list = self.examine_list(file_list)    # find folder content, NEF, JPG, etc.
        self.set_searched_type(type_list) # set searched type according to folder content
        self.content_info(type_list)    # display info about directory content

    @Slot()
    def type_rb_clicked(self):
        rb = self.sender()
        print(rb.text())
        self.searched_type = NEF_ID if rb.isChecked() else JPG_ID

    @Slot()
    def show_gallery(self):
        print('Show Gallery')
        gallery_dialog = GalleryDialog(self.pictures_list)
        gallery_dialog.exec()

    @Slot()
    def clear_console_output(self):
        self.console.clear()

    @Slot()
    def gname_done(self):
        if not self.edt_gname.text():  # enter pressed by itself
            # ----> replace with a QMessage (?)
            self.console_warning(MSG_GROUP_NAME_MISSING)
            return
        else:
            self.activate_task_buttons(True, True, True)

    @Slot()
    def execute(self):
        pass

    def import_card(self):
        rank = 1
        for file in self.pictures_list:
            exif = PhotoExif(file)
            dest_folder = STEP_0 + exif.compressed_date[0] + '/' + exif.compressed_date[1]
            os.makedirs(dest_folder, exist_ok=True) # create the destination folder if necessary
            try:
                shutil.copy(file, dest_folder)          # ----> replace with shutil.move
            except shutil.SameFileError: # ---->replace next two lines with a QMessage
                print('Tentative de recopier une fichier sur lui-même !')
                print('Sans doute une erreur de choix de tâche, p.ex. Importer au lieu de renommer')
                return
            print('$$$', rank, file) # ----> replace with a progress bar here
            rank += 1
        print('Déplacement/Tri par jour terminé') # ----> replace with a QMessage
        # do the cleaning
        self.pictures_list = []
        #self.lst_files.clear()
        self.btn_exec.setEnabled(False) #----> uncomment
        self.btn_gallery.setEnabled(False)  #----> uncomment
        self.btn_rename.setChecked(True)

    def rename_pictures(self):
        group_name = self.edt_gname.text()
        # these parts which are the same for all pictures are taken from the first one
        #   target directory : STEP1 / decade / parent folder
        #   where parent folder = compressed date + '-' + group name
        photo = PhotoExif(self.pictures_list[0])
        photo_date = photo.date
        photo_compressed_date = photo.compressed_date
        decade = photo_compressed_date[0]
        date = '(' + photo_date.replace(' ', '-') + ')_'
        date_suffix = self.cbx_date_suffix.currentText()
        if date_suffix == 'Aucun':
            date_suffix = ''
        compressed_date = ''.join(photo_compressed_date[1:3]) + date_suffix
        group_name = self.suppress_spaces(group_name).replace(' ', '-').lower()
        parent_folder = compressed_date + '-' + group_name
        ext = photo.original_suffix
        directory = STEP_1 + decade + '/' + parent_folder
        os.makedirs(directory + '/', exist_ok=True)

        rank = 1
        for picture in self.pictures_list:
            photo = PhotoExif(picture)
            rank_str = str("{:03d}".format(rank)) + '_'
            camera_name = '['+photo.original_name+']_'
            rank += 1
            new_name = date + rank_str + camera_name + group_name + ext
            shutil.copy(picture, directory + '/' + new_name)    # ----> replace with move

        self.console.clear()
        self.console.addItem(MSG_END.upper())
        self.activate_all_buttons(False)

    def correct_names(self):
        pass

    def content_info(self, type_list):
        if type_list == [False]*len(type_list):
            self.console_warning(MSG_NO_PICTURE)
            return
        if type_list[-1]:
            self.console_warning(MSG_IMPORT_ALL)
            self.write_console(MSG_SELECT_TYPE_TO_IMPORT)
        else:
            type_ = 'NEF' if type_list[NEF_ID] else 'JPG/JPEG' if type_list[JPG_ID] else None
            self.console_warning(MSG_IMPORT_TYPE + f'\'{type_}\'')
        self.write_console(MSG_PRESS_EXECUTE)

    def generate_new_name_and_directory(self):
        pass

    def open_dir(self):
        """
        Open directory containing the pictures to process
        :return: list: list of all the files in the directory, excluding subdirectories
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
        # display the content of the folder in lst_files display and save it in file_list
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

        return file_list

        # self.set_default_type(type_list)
        #
        #
        # # not ok (wrong folder or no image file), clear lst_files display et truncate file_list
        # if not self.pictures_list:
        #     self.console_warning(MSG_NO_PICTURE + ' (' + str(self.searched_type)+ ')')
        # # clear pictures list
        # self.pictures_list = []

    def set_searched_type(self, type_list):
        """
        set 'checked' of 'type buttons' according to the content of the directory: NEF, JPG, BOTH or NONE
        (note: the un/check job itself is done through the 'self.set_checked_type_buttons' routine)
        :param type_list: list(bool)
        :return: None
        """
        if [type_list[0]]*len(type_list) == type_list: # all values are equal either True or False
            full_type_list = [False]*(len(self.type_radiobuttons_list) - 1)
            if type_list[0]:    # all True
                full_type_list.append(True) # 'ALL button' to be checked
            else:   # all False
                full_type_list.append(False) # no button to be checked
        else:
            full_type_list = type_list  # 'type buttons' are checked according 'type_list'
            full_type_list.append(False)    # 'ALL button' unchecked
        self.set_checked_type_buttons(full_type_list)

    def set_checked_type_buttons(self, full_type_list):
        """
        task buttons are set un/checked according to the value of 'full_type_list'
        :param full_type_list: list(bool)
        :return: None
        """
        for index in range(len(self.type_radiobuttons_list)):
            self.type_radiobuttons_list[index].setChecked(full_type_list[index])

    def activate_exec_gallery_buttons(self, flag):
        # enable/disable EXEC and GALLERY buttons
        self.btn_exec.setEnabled(flag)
        self.btn_gallery.setEnabled(flag)

    def create_pictures_list(self, p_list):
        # find picture files using filters
        re_nef = re.compile(r".*\.nef$", re.IGNORECASE)  # nef filter
        re_jpg = re.compile(r".*\.jpe?g$", re.IGNORECASE)  # jpg filter
        filters = (re_nef, re_jpg)
        index = self.type_group.checkedId()
        for file in p_list:
            if not bool(filters[index].match(file)):  # filter
                continue
            self.pictures_list.append(file) # store
        self.pictures_list.sort()   # and sort the list

    def console_warning(self, message):
        msg = '\n====> ' + message.upper() +'\n'
        self.write_console(msg)
        return

    def create_thumb_jpeg(self):
        """
        Summary
            create_thumb_jpeg: Creates a temporary directory for JPEG embedded in NEF files

        Args:
            photos_test: list[str]
                list of the RAW files from which the JPEG is to be extracted
        """
        print(os.getcwd())
        os.makedirs(TMP_DIR, exist_ok=True)
        if self.searched_type:
            for i in range(0, len(self.pictures_list)):
                shutil.copy(self.pictures_list[i], TMP_DIR)
        else:
            for i in range(0, len(self.pictures_list)):
                photo_file = self.pictures_list[i]
                photo_exif = PhotoExif(photo_file)
                full_path_for_thumb = TMP_DIR + photo_exif.original_name + '.jpeg'
                print(full_path_for_thumb)
                # file_path = './pictures/' + photos_test[i]
                with rawpy.imread(photo_file) as raw:
                    thumb = raw.extract_thumb()
                with open(full_path_for_thumb, 'wb') as file:
                    file.write(thumb.data)

    def examine_list(self, file_list):
        """
        check the type of pictures in file_list, NEF, JPG, both or none
        :param file_list: list: list of pictures to check
        :return: list(bool): telling the types of files found in 'file_list'
        """
        type_list = [False]*(len(self.type_radiobuttons_list) - 1) # will allow more types in the future
        re_nef = re.compile(r".*\.nef$", re.IGNORECASE)  # nef filter
        re_jpg = re.compile(r".*\.jpe?g$", re.IGNORECASE)  # jpg filter
        filters = (re_nef, re_jpg)

        for file in file_list:
            for index in range(len(filters)):
                if bool(filters[index].match(file)):  # filter
                    type_list[index] = True
            if type_list[0] and all(type_list): #type_list[0] and all others are True
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

    @staticmethod
    def suppress_spaces(string_):
        while string_[0] == ' ':  # get rid of leading spaces
            string_ = string_[1:len(string_)]

        while string_[len(string_) - 1] == ' ':  # get rid of trailing spaces
            string_ = string_[0:len(string_) - 1]

        while string_.find('  ') > 0:
            string_ = string_.replace("  ", " ")  # replace double spaces with single space

        return string_




if __name__ == '__main__':
    app = QApplication(sys.argv)
    renameWindow = MainWindow()


    renameWindow.show()

    sys.exit(app.exec())