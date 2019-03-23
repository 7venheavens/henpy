# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Tue Mar 19 21:16:59 2019
#      by: pyside2-uic 2.0.0 running on PySide2 5.6.0~a1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1120, 447)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_3.addWidget(self.lineEdit_2)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.splitter = QtWidgets.QSplitter(self.groupBox_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tableWidget = QtWidgets.QTableWidget(self.splitter)
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.graphicsView = QtWidgets.QGraphicsView(self.splitter)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout_4.addWidget(self.splitter, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.verticalLayout.setStretch(1, 1)
        self.gridLayout_5.addLayout(self.verticalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1120, 21))
        self.menubar.setObjectName("menubar")
        self.menuFIle = QtWidgets.QMenu(self.menubar)
        self.menuFIle.setObjectName("menuFIle")
        self.menu_Tools = QtWidgets.QMenu(self.menubar)
        self.menu_Tools.setObjectName("menu_Tools")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoad_Folder = QtWidgets.QAction(MainWindow)
        self.actionLoad_Folder.setObjectName("actionLoad_Folder")
        self.actionPurge_Data = QtWidgets.QAction(MainWindow)
        self.actionPurge_Data.setObjectName("actionPurge_Data")
        self.action_Statistics = QtWidgets.QAction(MainWindow)
        self.action_Statistics.setObjectName("action_Statistics")
        self.actionPurge_Data_2 = QtWidgets.QAction(MainWindow)
        self.actionPurge_Data_2.setObjectName("actionPurge_Data_2")
        self.action_open_containing_folder = QtWidgets.QAction(MainWindow)
        self.action_open_containing_folder.setObjectName("action_open_containing_folder")
        self.menuFIle.addAction(self.actionLoad_Folder)
        self.menu_Tools.addAction(self.action_Statistics)
        self.menu_Tools.addAction(self.actionPurge_Data_2)
        self.menubar.addAction(self.menuFIle.menuAction())
        self.menubar.addAction(self.menu_Tools.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "MainWindow", None, -1))
        self.groupBox.setTitle(QtWidgets.QApplication.translate("MainWindow", "Search", None, -1))
        self.groupBox_2.setTitle(QtWidgets.QApplication.translate("MainWindow", "GroupBox", None, -1))
        self.menuFIle.setTitle(QtWidgets.QApplication.translate("MainWindow", "&FIle", None, -1))
        self.menu_Tools.setTitle(QtWidgets.QApplication.translate("MainWindow", "&Tools", None, -1))
        self.actionLoad_Folder.setText(QtWidgets.QApplication.translate("MainWindow", "Load Folder", None, -1))
        self.actionPurge_Data.setText(QtWidgets.QApplication.translate("MainWindow", "Purge Data", None, -1))
        self.action_Statistics.setText(QtWidgets.QApplication.translate("MainWindow", "&Statistics", None, -1))
        self.actionPurge_Data_2.setText(QtWidgets.QApplication.translate("MainWindow", "Purge Data", None, -1))
        self.action_open_containing_folder.setText(QtWidgets.QApplication.translate("MainWindow", "Open Containing Folder", None, -1))
        self.action_open_containing_folder.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Open Containing Folder", None, -1))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
