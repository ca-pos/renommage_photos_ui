from PySide6.QtCore import QSize

BKG_COL = '#450A2C'
TXT_COL = '#FFE333'

NONE_ID = -1
NEF_ID = 0
JPG_ID = 1
ALL_ID = 99
# TYPE_ID = [NEF_ID, JPG_ID]

NEF_EXT = '.NEF'
JPG_EXT = '.JPG'

NEF_TXT = 'NEF'
JPG_TXT = 'JPG/JPEG'
ALL_TXT = 'Tout'
TXT_TYPES_LIST = [NEF_TXT, JPG_TXT, ALL_TXT]

NO_TASK = -1
IMPORT_TASK_ID = 0
RENAME_TASK_ID = 1
CORRECT_TASK_ID = 2

STEP_0 = '/home/camille/tmp/0. Tri & Renommage/tests_a_jeter/step_0/'      # to be changed in the final version
STEP_1 = '/home/camille/tmp/0. Tri & Renommage/tests_a_jeter/step_1/'    # to be changed in the final version

TMP_DIR = './tmp/'
BLURRED = '_blurred'
FULL_SIZE = '_full_size'
THUMB_SIZE = '_thumb_size'

MSG_IMPORT_ALL = 'Importation de tous les fichiers images ...'
MSG_IMPORT_TYPE = 'Importation des fichiers '
MSG_PRESS_EXECUTE = "Cliquez sur le bouton 'Exécuter' pour effectuer l'importation"
MSG_SELECT_TYPE_TO_IMPORT = "Sinon, choisir le type d'images à importer puis ...\n"
MSG_NO_PICTURE = 'Aucun fichier image dans ce répertoire'
MSG_GROUP_NAME_MISSING = "N'entrez pas un nom vide"
MSG_END = '==== Terminé ===='

DISPLAY_HEIGHT = 720
H_SIZE = 1000
V_SIZE = 600
MAIN_SIZE = QSize(H_SIZE, V_SIZE)
BUTTON_V_SIZE = 22
MASK_BUTTON_H_SIZE = 80
ICON_V_SIZE = 18
ICON_H_SIZE = 18

HI_RES = QSize(600, 600)

PIXMAP_MAX_SIZE = 450
PIXMAP_SCALE = QSize(PIXMAP_MAX_SIZE, PIXMAP_MAX_SIZE)

ZOOM_IN_RATIO = 1.1
ZOOM_OUT_RATIO = .92


# size of iphone jpeg: (1354, 2323)
# size of NEF-embedded thumb (6000, 4000)
