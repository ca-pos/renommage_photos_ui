# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'interface2.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(822, 576)
        MainWindow.setMinimumSize(QSize(800, 450))
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(129, 20, 83, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        brush2 = QBrush(QColor(193, 30, 125, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Light, brush2)
        brush3 = QBrush(QColor(161, 25, 104, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Midlight, brush3)
        brush4 = QBrush(QColor(64, 10, 41, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Dark, brush4)
        brush5 = QBrush(QColor(86, 13, 55, 255))
        brush5.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Mid, brush5)
        brush6 = QBrush(QColor(255, 254, 24, 255))
        brush6.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush6)
        brush7 = QBrush(QColor(255, 255, 255, 255))
        brush7.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.BrightText, brush7)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Active, QPalette.Base, brush7)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush)
        brush8 = QBrush(QColor(192, 137, 169, 255))
        brush8.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush8)
        brush9 = QBrush(QColor(255, 255, 220, 255))
        brush9.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush9)
        palette.setBrush(QPalette.Active, QPalette.ToolTipText, brush)
        brush10 = QBrush(QColor(0, 0, 0, 127))
        brush10.setStyle(Qt.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush10)
#endif
        palette.setBrush(QPalette.Active, QPalette.Accent, brush7)
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Light, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.BrightText, brush7)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush7)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush8)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush9)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush10)
#endif
        palette.setBrush(QPalette.Inactive, QPalette.Accent, brush7)
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Light, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Disabled, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.BrightText, brush7)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush9)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush)
        brush11 = QBrush(QColor(64, 10, 41, 127))
        brush11.setStyle(Qt.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush11)
#endif
        brush12 = QBrush(QColor(168, 26, 108, 255))
        brush12.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Accent, brush12)
        MainWindow.setPalette(palette)
        font = QFont()
        font.setFamilies([u"Ubuntu"])
        font.setPointSize(10)
        MainWindow.setFont(font)
        MainWindow.setToolTipDuration(21)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        palette1 = QPalette()
        palette1.setBrush(QPalette.Active, QPalette.WindowText, brush6)
        palette1.setBrush(QPalette.Active, QPalette.ButtonText, brush6)
        brush13 = QBrush(QColor(102, 102, 102, 255))
        brush13.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Base, brush13)
        palette1.setBrush(QPalette.Active, QPalette.ToolTipText, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.WindowText, brush6)
        palette1.setBrush(QPalette.Inactive, QPalette.ButtonText, brush6)
        palette1.setBrush(QPalette.Inactive, QPalette.Base, brush13)
        palette1.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush)
        palette1.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush)
        self.centralwidget.setPalette(palette1)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.btn_import = QPushButton(self.centralwidget)
        self.btn_import.setObjectName(u"btn_import")
        self.btn_import.setChecked(False)
        self.btn_import.setAutoExclusive(False)

        self.verticalLayout_2.addWidget(self.btn_import)

        self.btn_rename = QPushButton(self.centralwidget)
        self.btn_rename.setObjectName(u"btn_rename")
        self.btn_rename.setChecked(False)
        self.btn_rename.setAutoExclusive(False)

        self.verticalLayout_2.addWidget(self.btn_rename)

        self.btn_correct = QPushButton(self.centralwidget)
        self.btn_correct.setObjectName(u"btn_correct")
        self.btn_correct.setAutoExclusive(False)

        self.verticalLayout_2.addWidget(self.btn_correct)


        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 4, 1)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 0, 1, 4, 1)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lbl_type_of_files = QLabel(self.centralwidget)
        self.lbl_type_of_files.setObjectName(u"lbl_type_of_files")

        self.verticalLayout_3.addWidget(self.lbl_type_of_files)

        self.verticalSpacer_2 = QSpacerItem(20, 53, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)


        self.gridLayout.addLayout(self.verticalLayout_3, 0, 2, 4, 1)

        self.rb_nef = QRadioButton(self.centralwidget)
        self.rb_nef.setObjectName(u"rb_nef")
        self.rb_nef.setChecked(False)
        self.rb_nef.setAutoExclusive(False)

        self.gridLayout.addWidget(self.rb_nef, 0, 3, 1, 1)

        self.line_3 = QFrame(self.centralwidget)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_3, 0, 4, 4, 1)

        self.btn_gallery = QPushButton(self.centralwidget)
        self.btn_gallery.setObjectName(u"btn_gallery")

        self.gridLayout.addWidget(self.btn_gallery, 0, 5, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(140, 17, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_3, 0, 6, 1, 1)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.btn_exec = QPushButton(self.centralwidget)
        self.btn_exec.setObjectName(u"btn_exec")

        self.verticalLayout_4.addWidget(self.btn_exec)

        self.btn_reset = QPushButton(self.centralwidget)
        self.btn_reset.setObjectName(u"btn_reset")

        self.verticalLayout_4.addWidget(self.btn_reset)

        self.btn_quit = QPushButton(self.centralwidget)
        self.btn_quit.setObjectName(u"btn_quit")

        self.verticalLayout_4.addWidget(self.btn_quit)


        self.gridLayout.addLayout(self.verticalLayout_4, 0, 7, 4, 1)

        self.rb_jpg = QRadioButton(self.centralwidget)
        self.rb_jpg.setObjectName(u"rb_jpg")
        self.rb_jpg.setChecked(False)
        self.rb_jpg.setAutoExclusive(False)

        self.gridLayout.addWidget(self.rb_jpg, 1, 3, 2, 1)

        self.horizontalSpacer_4 = QSpacerItem(226, 17, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_4, 2, 5, 1, 2)

        self.rb_all = QRadioButton(self.centralwidget)
        self.rb_all.setObjectName(u"rb_all")
        self.rb_all.setAutoExclusive(False)

        self.gridLayout.addWidget(self.rb_all, 3, 3, 1, 1)

        self.line_2 = QFrame(self.centralwidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_2, 4, 0, 1, 8)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lbl_group_name = QLabel(self.centralwidget)
        self.lbl_group_name.setObjectName(u"lbl_group_name")

        self.horizontalLayout.addWidget(self.lbl_group_name)

        self.horizontalSpacer_2 = QSpacerItem(638, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.edt_gname = QLineEdit(self.centralwidget)
        self.edt_gname.setObjectName(u"edt_gname")

        self.verticalLayout.addWidget(self.edt_gname)


        self.gridLayout.addLayout(self.verticalLayout, 5, 0, 1, 8)

        self.line_4 = QFrame(self.centralwidget)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_4, 6, 0, 1, 8)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lbl_list_of_files = QLabel(self.centralwidget)
        self.lbl_list_of_files.setObjectName(u"lbl_list_of_files")

        self.horizontalLayout_2.addWidget(self.lbl_list_of_files)

        self.horizontalSpacer = QSpacerItem(638, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.btn_clear_output = QPushButton(self.centralwidget)
        self.btn_clear_output.setObjectName(u"btn_clear_output")

        self.horizontalLayout_2.addWidget(self.btn_clear_output)


        self.gridLayout.addLayout(self.horizontalLayout_2, 7, 0, 1, 8)

        self.console = QListWidget(self.centralwidget)
        self.console.setObjectName(u"console")

        self.gridLayout.addWidget(self.console, 8, 0, 1, 8)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
#if QT_CONFIG(shortcut)
        self.lbl_group_name.setBuddy(self.edt_gname)
        self.lbl_list_of_files.setBuddy(self.console)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Renommage des photos", None))
        self.btn_import.setText(QCoreApplication.translate("MainWindow", u"Importer la carte m\u00e9moire", None))
        self.btn_rename.setText(QCoreApplication.translate("MainWindow", u"Renommer", None))
        self.btn_correct.setText(QCoreApplication.translate("MainWindow", u"Corriger", None))
        self.lbl_type_of_files.setText(QCoreApplication.translate("MainWindow", u"Quels fichiers", None))
        self.rb_nef.setText(QCoreApplication.translate("MainWindow", u"NEF", None))
        self.btn_gallery.setText(QCoreApplication.translate("MainWindow", u"Galerie", None))
        self.btn_exec.setText(QCoreApplication.translate("MainWindow", u"                         Ex\u00e9cuter                       ", None))
        self.btn_reset.setText(QCoreApplication.translate("MainWindow", u"  R\u00e9initialiser", None))
        self.btn_quit.setText(QCoreApplication.translate("MainWindow", u"  Quitter", None))
        self.rb_jpg.setText(QCoreApplication.translate("MainWindow", u"JPG/JPEG", None))
        self.rb_all.setText(QCoreApplication.translate("MainWindow", u"Tout", None))
        self.lbl_group_name.setText(QCoreApplication.translate("MainWindow", u"Nom du groupe de fichiers", None))
        self.lbl_list_of_files.setText(QCoreApplication.translate("MainWindow", u"Console", None))
        self.btn_clear_output.setText(QCoreApplication.translate("MainWindow", u"Effacer", None))
    # retranslateUi

