# coding: utf-8
# Qt
from PySide6.QtCore import Qt, QRunnable, QObject, Signal
from translate import doTranslation

"""
QRunnable is not a QObject so it not allows you to emit signal
This class is used to be able to emit signal from QRunnable
"""
class TaskWorkerSignal(QObject):
    processingDone = Signal(list)

    def __init__(self) -> None:
        super().__init__()

"""
This is QRunnable which will do a video processing in additional thread
"""

class TaskWorker(QRunnable):
    """Worker thread for running background tasks."""

    def __init__(self, initialStrings: list, language: str, verbose: bool = False) -> None:
        super(TaskWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.initialStrings = initialStrings
        self.language = language
        self.verbose = verbose
        self.signalObject = TaskWorkerSignal()

    def __del__(self) -> None:
        self.signalObject.deleteLater()

    def getSignalObject(self) -> None:
        return self.signalObject

    def run(self) -> None:
        self.res = doTranslation(
            self.initialStrings,
            self.language,
            self.verbose,
        )
        self.signalObject.processingDone.emit(self.res)

    def results(self) -> dict:
        return self.res
