from PySide2 import QtCore, QtGui, QtWidgets
import os

from henpy.ui_designer.main import Ui_MainWindow
from henpy.utilities.misc import dotdict, title_case


class MainWindowController(Ui_MainWindow):
    def __init__(self, parent, *args, **kwargs):
        super().__init__()
        self.parent = parent
        self.idx = dotdict(**{"code": 0,
                              "stars": 1,
                              "tags": 2,
                              "maker": 3,
                              "publisher": 4,
                              "path": 5})

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.setup_tablewidget()

    def setup_tablewidget(self):
        # Setup context Menu
        self.tableWidget.customContextMenuRequested.connect(self.on_context_menu)
        self.tableWidget.cellDoubleClicked.connect(self.open_file)

        self.setup_table()

    def setup_table(self):
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setHorizontalHeaderLabels([title_case(i) for i in self.idx.keys()])

    def _modify_row(self, row_index, code, stars, tags, maker, publisher, path):
        self.tableWidget.setItem(row_index, 0, QtWidgets.QTableWidgetItem(code))
        self.tableWidget.setItem(row_index, 1, QtWidgets.QTableWidgetItem(stars))
        self.tableWidget.setItem(row_index, 2, QtWidgets.QTableWidgetItem(tags))
        self.tableWidget.setItem(row_index, 3, QtWidgets.QTableWidgetItem(maker))
        self.tableWidget.setItem(row_index, 4, QtWidgets.QTableWidgetItem(publisher))
        self.tableWidget.setItem(row_index, 5, QtWidgets.QTableWidgetItem(path))

    def add_row(self, code, stars, tags, maker, publisher, path):
        # Create a new row
        rowcount = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowcount)
        self._modify_row(rowcount, code, stars, tags, maker, publisher, path)

    def open_file(self, row, column):
        print(f"Opening file for row {row}")

    def open_folder(self, row):
        print(f"Opening folder for row {row}")
        folder = self.tableWidget.item(row, self.idx.path)
        path = folder.text()
        directory = os.path.dirname(path)
        os.startfile(directory)


    def on_context_menu(self, point):
        print(f"CONTEXT, {point}")
        self.menu = QtWidgets.QMenu(self.tableWidget)
        open_cont_action = QtWidgets.QAction("Open Containing Folder", self.tableWidget)
        row = self.tableWidget.rowAt(point.y())
        open_cont_action.triggered.connect(lambda: self.open_folder(row))
        self.menu.addAction(open_cont_action)
        self.menu.popup(QtGui.QCursor.pos())


class App(QtWidgets.QApplication):
    def __init__(self, sys_argv, debug=False):
        super().__init__(sys_argv)
        self.mw = QtWidgets.QMainWindow()
        self.ui = MainWindowController(parent=self)
        self.ui.setupUi(self.mw)
        if debug:
            self.ui.add_row("LOVE-101", "Nanashi", "Fun", "Made", "Pub", "D:/tmp/test.txt")

        self.mw.show()


if __name__ == "__main__":
    import sys

    app = App(sys.argv, debug=True)
    app.ui.open_folder(0)
    sys.exit(app.exec_())
