from PyQt5 import QtCore, QtGui, QtWidgets

import pandas as pd

from simdb.databaseAPI import getEntryTable

from PandasModel import PandasModel

# Answer to: https://stackoverflow.com/questions/44603119/how-to-display-a-pandas-data-frame-with-pyqt5
# Copied from: https://github.com/eyllanesc/stackoverflow/tree/master/PandasTableView
# modified to work with our database

class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=None)
        vLayout = QtWidgets.QVBoxLayout(self)
        hLayout = QtWidgets.QHBoxLayout()
        self.pathLE = QtWidgets.QLineEdit(self)
        hLayout.addWidget(self.pathLE)
        self.loadBtn = QtWidgets.QPushButton("Select File", self)
        hLayout.addWidget(self.loadBtn)
        vLayout.addLayout(hLayout)
        self.pandasTv = QtWidgets.QTableView(self)
        vLayout.addWidget(self.pandasTv)
        self.loadBtn.clicked.connect(self.loadFile)
        self.pandasTv.setSortingEnabled(True)

    def loadFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "database files (*.db)");
        self.pathLE.setText(fileName)
        table = getEntryTable(fileName,
                              columns=["entry_id",
                                       "path",
                                       "created_on",
                                       "added_on",
                                       "updated_on",
                                       "description"],
                              load_keys=False,
                              load_tags=False,
                              )
        model = PandasModel(table)
        self.pandasTv.setModel(model)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())