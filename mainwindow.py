# This Python file uses the following encoding: utf-8
# Important:
# You need to run the following command to generate all needed .py files:
#     python tools\build.py
import os
import sys
import pyperclip as pc
from PySide6.QtCore import QItemSelection, Qt, QThreadPool, QFile, QTextStream
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox 
from translate import getDataFromXMLFile, getDataFromJSONFile, getDataFromRESXFile, processXMLFile, processJsonFile, processResxFile
from taskthread import TaskWorker
import webbrowser
import app_rc
from mainwindow_ui import Ui_MainWindow



excludeFromTranslation = []

class MainWindow(QMainWindow):
    linesToTranslate = None
    translatedLines = None
    selectedFilePath = None
    def __init__(self, parent=None):
        super().__init__(parent)

        # add fonts
        QFontDatabase.addApplicationFont(":/fonts/Roboto-Medium.ttf")
        QFontDatabase.addApplicationFont(":/fonts/Roboto-Regular.ttf")
        QFontDatabase.addApplicationFont(":/fonts/Roboto-Bold.ttf")
        QFontDatabase.addApplicationFont(":/fonts/MAVENPRO-REGULAR.TTF")

        # change qss
        file = QFile(":/qss/custom.qss")
        file.open(QFile.ReadOnly | QFile.Text)
        self.setStyleSheet(QTextStream(file).readAll())

        # setup ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.progressBar.setVisible(False)

        # connect signals
        self.ui.buttonSelect.clicked.connect(self._onSelectDir)
        self.ui.pushButtonCopyToClipboard.clicked.connect(self._onCopyToClipboard)
        self.ui.pushButtonOpenBrowser.clicked.connect(self._onOpenBrowser)
        self.ui.buttonSave.clicked.connect(self._onSave)
        self.ui.textEditTranslated.textChanged.connect(self._onTranslationChanged)
        self.ui.comboBoxLanguage.currentIndexChanged.connect(self._onLanguageChanged)
        self.ui.tabWidget.currentChanged.connect(self._checkTraslation)

        # it is better to load this from json file or database
        self.excludeFromTranslation = excludeFromTranslation


    def _onLanguageChanged(self):
        saveFilePath = f"{os.path.splitext(self.selectedFilePath)[0]}_{self.ui.comboBoxLanguage.currentText()}{os.path.splitext(self.selectedFilePath)[1]}"
        self.ui.labelSaveTo.setText(os.path.basename(saveFilePath))
        self.ui.labelSaveTo.setToolTip(saveFilePath)
        self._generateAutoTranslation()

    def _onAutoTranslationDone(self, translatedLines: list):
        model = QStandardItemModel(len(self.linesToTranslate), 2)
        row = 0
        for key, value in zip(self.linesToTranslate, translatedLines):
            item = QStandardItem(key)
            item.setEditable(False)
            item.setToolTip(key)
            model.setItem(row, 0, item)
            item = QStandardItem(value)
            item.setEditable(True)
            item.setToolTip(value)
            model.setItem(row, 1, item)
            row = row + 1
        self.ui.tableView.setModel(model)
        self.ui.progressBar.setVisible(False)
        self.setEnabled(True)

    def _generateAutoTranslation(self):
        if self.linesToTranslate and len(self.linesToTranslate) > 0:
            self.ui.progressBar.setVisible(True)
            self.workRunnable = TaskWorker(self.linesToTranslate, self.ui.comboBoxLanguage.currentText(), False)
            self.workRunnable.setAutoDelete(True)
            self.workRunnable.getSignalObject().processingDone.connect(self._onAutoTranslationDone)
            QThreadPool.globalInstance().start(self.workRunnable)
            self.setEnabled(False)

    def _onSave(self):
        translatedLinesToSave = self.translatedLines
        if self.ui.tabWidget.currentIndex() == 1:
            # we are in automatic mode
            translatedLinesToSave = []
            model = self.ui.tableView.model()
            for i in range(model.rowCount()):
                index = model.index( i, 1 )
                translatedLinesToSave.append(str(index.data(Qt.DisplayRole)))
    
        selectedExt = os.path.splitext(self.selectedFilePath)[1]
        saveFilePath = self.ui.labelSaveTo.toolTip()
        if selectedExt == ".resx":
            processResxFile(self.selectedFilePath, translatedLinesToSave, saveFilePath, self.excludeFromTranslation)
            QMessageBox.information(self, self.tr("Translator"), self.tr("File saved"), QMessageBox.Ok)
        elif selectedExt == ".xml":
            processXMLFile(self.selectedFilePath, translatedLinesToSave, saveFilePath, self.excludeFromTranslation)
            QMessageBox.information(self, self.tr("Translator"), self.tr("File saved"), QMessageBox.Ok)
        elif selectedExt == ".json":
            processJsonFile(self.selectedFilePath, translatedLinesToSave, saveFilePath, self.excludeFromTranslation)
            QMessageBox.information(self, self.tr("Translator"), self.tr("File saved"), QMessageBox.Ok)


    def _onTranslationChanged(self):
        translated = self.ui.textEditTranslated.toPlainText()
        self.translatedLines = translated.split('\n')
        self._checkTraslation()

    def _checkTraslation(self):
        if self.ui.tabWidget.currentIndex() == 0:
            # if we are in manual mode
            if self.linesToTranslate and self.translatedLines:
                if len(self.linesToTranslate) == len(self.translatedLines):
                    self.ui.buttonSave.setEnabled(True)
                    self.ui.buttonSave.setToolTip("Ready to save")
                else:
                    self.ui.buttonSave.setEnabled(False)
                    self.ui.buttonSave.setToolTip(f"Different len for original and translated lines {len(self.linesToTranslate)} != {len(self.translatedLines)}")
        else:
            # we are in automatic mode
            self.ui.buttonSave.setEnabled(True)
            self.ui.buttonSave.setToolTip("Ready to save")

    def _onOpenBrowser(self):
        webbrowser.open('https://translate.google.by/')

    def _onCopyToClipboard(self):
        pc.copy(self.ui.textEditOriginal.toPlainText())

    def _onSelectDir(self):
        dirToOpen = QFileDialog.getExistingDirectory(self, self.tr("Select Directory"))
        if dirToOpen:
            self.ui.labelSelectedFolder.setText(dirToOpen)
            
            # filter files and extract only supported file types
            supportedFiles = {}
            for (dirpath, _, filenames) in os.walk(dirToOpen):
                if len(filenames) != 0:
                    for filename in filenames:
                        if os.path.splitext(filename)[1] in [".resx", ".xml", ".json"]:
                            fullpath =os.path.join(dirpath, filename)
                            supportedFiles[fullpath] = filename
                break # we process only parent folder -> if you need to process all folders, then update this code

            model = QStandardItemModel(len(supportedFiles), 1)
            row = 0
            for key, value in supportedFiles.items():
                item = QStandardItem(value)
                item.setToolTip(key)
                model.setItem(row, 0, item)
                row = row + 1
            self.ui.listView.setModel(model)
            # do connection here, because untill we set model slection model is empty
            try:
                # we have no connection on first run
                self.ui.listView.selectionModel().selectionChanged.disconnect(self._onFileSelected)
            except:
                pass
            self.ui.listView.selectionModel().selectionChanged.connect(self._onFileSelected)

    def _onFileSelected(self, selected:QItemSelection, deselected:QItemSelection):
        self.selectedFilePath = selected.indexes()[0].data(Qt.ToolTipRole)

        # this will take current language and set generate filename to save
        self._onLanguageChanged()

        # check selected file and get data from it
        selectedExt = os.path.splitext(self.selectedFilePath)[1]
        if selectedExt == ".resx":
            self.linesToTranslate = getDataFromRESXFile(self.selectedFilePath, self.excludeFromTranslation)
        elif selectedExt == ".xml":
            self.linesToTranslate = getDataFromXMLFile(self.selectedFilePath, self.excludeFromTranslation)
        elif selectedExt == ".json":
            self.linesToTranslate = getDataFromJSONFile(self.selectedFilePath, self.excludeFromTranslation)
        self.ui.textEditOriginal.setPlainText('\n'.join(self.linesToTranslate))
        self.ui.textEditTranslated.setPlainText("")

        # generate auto translatiion
        self._generateAutoTranslation()

        # do check
        self._checkTraslation()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/TranslatorUI.ico"))
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
