from PySide6.QtCore import QSize

BKG_COL = '#450A2C'
TXT_COL = '#FFE333'

NONE_ID = -1
NEF_ID = 0
JPG_ID = 1
ALL_ID = 99
TYPE_ID = [NEF_ID, JPG_ID]
IMPORT_ID = 0
RENAME_ID = 1
CORRECT_ID = 2

STEP_0 = '/home/camille/tmp/0. Tri & Renommage/tests_a_jeter/0._tri1/'      # to be changed in the final version
STEP_1 = '/home/camille/tmp/0. Tri & Renommage/tests_a_jeter/1._import/'    # to be changed in the final version

TMP_DIR = './tmp/'
BLURRED = '_blurred'

MSG_NO_PICTURE = 'Aucun fichier correspondant dans ce répertoire'
MSG_GROUP_NAME_MISSING = "N'entrez pas un nom vide"
MSG_END = '==== Terminé ===='

H_SIZE = 1000
V_SIZE = 600
MAIN_SIZE = QSize(H_SIZE, V_SIZE)
BUTTON_V_SIZE = 22
MASK_BUTTON_H_SIZE = 80
ICON_V_SIZE = 18
ICON_H_SIZE = 18

HI_RES = QSize(400, 400)

PIXMAP_MAX_SIZE = 300
PIXMAP_SCALE = QSize(PIXMAP_MAX_SIZE, PIXMAP_MAX_SIZE)



