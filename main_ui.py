# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication,
    QMetaObject, QRect)

from PySide6.QtWidgets import ( QLabel, QMenu,
    QMenuBar, QPushButton, QStatusBar,
    QTextBrowser, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.btn_selectWindow = QPushButton(self.centralwidget)
        self.btn_selectWindow.setObjectName(u"btn_selectWindow")
        self.btn_selectWindow.setGeometry(QRect(130, 70, 131, 31))
        self.btn_loadModel = QPushButton(self.centralwidget)
        self.btn_loadModel.setObjectName(u"btn_loadModel")
        self.btn_loadModel.setGeometry(QRect(130, 130, 131, 31))
        self.btn_startScan = QPushButton(self.centralwidget)
        self.btn_startScan.setObjectName(u"btn_startScan")
        self.btn_startScan.setGeometry(QRect(130, 190, 131, 31))
        self.label_hwd = QLabel(self.centralwidget)
        self.label_hwd.setObjectName(u"label_hwd")
        self.label_hwd.setGeometry(QRect(280, 80, 491, 16))
        self.label_loadRet = QLabel(self.centralwidget)
        self.label_loadRet.setObjectName(u"label_loadRet")
        self.label_loadRet.setGeometry(QRect(280, 140, 501, 16))
        self.label_result = QLabel(self.centralwidget)
        self.label_result.setObjectName(u"label_result")
        self.label_result.setGeometry(QRect(280, 200, 481, 16))
        self.textBrowser = QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(10, 451, 781, 111))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.menutestyolo = QMenu(self.menubar)
        self.menutestyolo.setObjectName(u"menutestyolo")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menutestyolo.menuAction())

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btn_selectWindow.setText(QCoreApplication.translate("MainWindow", u"\u9009\u62e9\u7a97\u53e3\u53e5\u67c4", None))
        self.btn_loadModel.setText(QCoreApplication.translate("MainWindow", u"\u52a0\u8f7d\u6a21\u578b", None))
        self.btn_startScan.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb\u8bc6\u522b", None))
        self.label_hwd.setText(QCoreApplication.translate("MainWindow", u"\u53e5\u67c4\uff1a", None))
        self.label_loadRet.setText(QCoreApplication.translate("MainWindow", u"\u3002\u3002\u3002", None))
        self.label_result.setText(QCoreApplication.translate("MainWindow", u"\u53e5\u67c4\uff1a", None))
        self.menutestyolo.setTitle(QCoreApplication.translate("MainWindow", u"testyolo", None))
    # retranslateUi

