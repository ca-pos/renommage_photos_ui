#import string
import sys
import os
import shutil
import re
from os.path import abspath
from functools import partial

from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QButtonGroup, QDialog, QDialogButtonBox,
                               QHBoxLayout, QVBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import Slot, Qt

from interface import Ui_MainWindow

from PhotoExif import *
from constants import *

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Renommage des Photos')
        self.setupUi(self)

        # selected (current) folder and its content saved in file_list
        self.pictures_list = list()
        self.current_folder = str()
        # self.gname_exist = False

        # group type of image (NEF or JPG) radiobutton and set the id's
        self.rb_nef.setChecked(True)    # default NEF files
        self.type_group = QButtonGroup(self)
        self.type_group.addButton(self.rb_nef)
        self.type_group.setId(self.rb_nef, NEF_ID)
        self.type_group.addButton(self.rb_jpg)
        self.type_group.setId(self.rb_jpg, JPG_ID)
        # group tasks (IMPORT, RENAME, CORRECT) radiobutton and set the id's
        self.op_group = QButtonGroup(self)
        self.op_group.addButton(self.rb_initial_sort)
        self.op_group.setId(self.rb_initial_sort, IMPORT_ID)
        self.op_group.addButton(self.rb_rename)
        self.op_group.setId(self.rb_rename, RENAME_ID)
        self.op_group.addButton(self.rb_correct)
        self.op_group.setId(self.rb_correct, CORRECT_ID)

        # initialize date suffix combobox
        self.cbx_date_suffix.setPlaceholderText('Choisir')
        self.cbx_date_suffix.addItem('Aucun')
        self.cbx_date_suffix.setCurrentIndex(3)
        for suffix in range(0, 26):
            self.cbx_date_suffix.addItem(string.ascii_lowercase[suffix])

        self.activate_all_buttons(False) # at start, no action allowed

        # connect the buttons
        self.btn_select.clicked.connect(self.open_dir)                      # select dir
        self.btn_gallery.clicked.connect(self.show_gallery)                 # show gallery
        self.btn_exec.clicked.connect(self.execute)                         # execute chosen task
        self.btn_quit.clicked.connect(self.close)                           # leave app
        self.btn_clear_output.clicked.connect(self.clear_console_output)    # clear console
        self.edt_gname.editingFinished.connect(self.gname_done)             # group name entered

    def import_card(self):
        print('Import')
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
            print(rank, file) # ----> replace with a progress bar here
            rank += 1
        print('Déplacement/Tri par jour terminé') # ----> replace with a QMessage
        # do the cleaning
        self.pictures_list = []
        self.lst_files.clear()
        self.btn_exec.setEnabled(False) #----> uncomment
        self.btn_gallery.setEnabled(False)  #----> uncomment
        self.rb_rename.setChecked(True)

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
            self.txt_old_name.setText(directory + '/' + new_name)
            shutil.copy(picture, directory + '/' + new_name)    # ----> replace with move

        self.console.clear()
        self.console.addItem(MSG_END.upper())
        self.activate_all_buttons(False)

    def correct_names(self):
        print('Correct')

    def generate_new_name_and_directory(self):
        pass

    @Slot()
    def execute(self):
        # execute the checked task (import, rename, correct)
        [self.import_card, self.rename_pictures, self.correct_names][self.op_group.checkedId()]()

    @Slot()
    def show_gallery(self):
        print('Show Gallery')
        
    @Slot()
    def open_dir(self):
        # open the dialog window for folder selection
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Répertoire des photos à renommer")
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setViewMode(QFileDialog.ViewMode.List)

        # clear the display lst_files
        self.console.clear()

        if file_dialog.exec():
            selected_directory = file_dialog.selectedFiles()[0]
            os.chdir(selected_directory)  # go in the selected dir
            self.current_folder = abspath(selected_directory)
            self.console.addItem( 'Contenu du répertoire : ' + self.current_folder) # and display it
        else:   # cancel button was pressed by user
            return
        # display the content of the folder in lst_files display and save it in file_list
        file_list = list()
        for file in os.listdir('.'):
            if not os.path.isdir(file):
                file_list.append(file)
        file_list.sort()
        rank = 1
        for file in file_list:
            rank_str = str("{:03d}".format(rank)) + ':  '
            self.console.addItem( rank_str+file)
            rank += 1

        self.create_pictures_list(file_list)

        # ask confirmation
        dlg = AcceptDialog()
        dlg.setWindowTitle('Choisir le répertoire')

        if dlg.exec() and self.pictures_list: # ok, enable exec & gallery buttons
            self.activate_task_buttons(True, False, True)
            self.activate_exec_gallery_buttons(True)
            return
        # not ok (wrong folder or no image file), clear lst_files display et truncate file_list
        self.console.clear()
        if not self.pictures_list:
            self.console.insertItem( 0, MSG_NO_PICTURE)
            print('Pas de fichers NEF/JPG')     # replace with a QMessage
        # clear display and list
        self.pictures_list = []

    @Slot()
    def clear_console_output(self):
        self.console.clear()

    @Slot()
    def gname_done(self):
        if not self.edt_gname.text():  # enter pressed by itself
            # ----> replace with a QMessage (?)
            self.message_in_console(MSG_GROUP_NAME_MISSING)
            return
        else:
            self.activate_task_buttons(True, True, True)

    def activate_exec_gallery_buttons(self, flag):
        # enable/disable EXEC and GALLERY buttons
        self.btn_exec.setEnabled(flag)
        self.btn_gallery.setEnabled(flag)

    def activate_task_buttons(self, flag_sort, flag_rename, flag_correct):
        # enable/disable task buttons
        self.rb_initial_sort.setEnabled(flag_sort)
        self.rb_rename.setEnabled(flag_rename)
        self.rb_correct.setEnabled(flag_correct)

    def activate_all_buttons(self, flag):
        self.activate_task_buttons( flag, flag, flag)
        self.activate_exec_gallery_buttons(flag)

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

    def message_in_console(self, message):
        msg = '\n====> ' + message.upper() +'\n'
        self.console.addItem(msg)
        self.console.scrollToBottom()

    def suppress_spaces(self, string):
        while string[0] == ' ':  # get rid of leading spaces
            string = string[1:len(string)]

        while string[len(string) - 1] == ' ':  # get rid of trailing spaces
            string = string[0:len(string) - 1]

        while string.find('  ') > 0:
            string = string.replace("  ", " ")  # replace double spaces with single space

        return string

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    renameWindow = MainWindow()
    renameWindow.show()

    sys.exit(app.exec())