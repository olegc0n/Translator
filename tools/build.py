# coding: utf-8
import os
import subprocess
import sys
from multiprocessing import Pool

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# In a virtualenv, python.exe is in the Scripts folder
if os.environ.get("VIRTUAL_ENV"):
    SCRIPTS_PATH = os.path.join(os.path.dirname(sys.executable))
else:
    SCRIPTS_PATH = os.path.join(os.path.dirname(sys.executable), r"Scripts")


    

def buildFile(filePath: str, outFilePath: str) -> None:
    """Dispatcher for the process pool."""
    def _checkFile(filePath: str, expectedExt: str) -> None:
        if not os.path.splitext(filePath)[1] == expectedExt:
            raise IOError(f"Expected a {expectedExt} file, received {os.path.splitext(filePath)[1]}")
        if not os.path.exists(filePath):
            raise FileNotFoundError(f"Cannot find {expectedExt} file at: {filePath}")
            
    def _runCmd(cmd:list) -> bytes:
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate(timeout=60)
            return out
        except FileNotFoundError as ex:
            print(subprocess.list2cmdline(cmd))
            raise FileNotFoundError(
                "Cannot find pyside6-xxx.exe, is PySide6 installed and Python/Scripts on your PATH env var?"
            ) from ex
    
    if os.path.splitext(filePath)[1] == ".ui":
        """Call pyside6-uic to build a .py file from a .ui file."""
        _checkFile(filePath, ".ui")
        cmd = [os.path.join(SCRIPTS_PATH, r"pyside6-uic.exe"), filePath]
        out = _runCmd(cmd)
        with open(outFilePath, "wb") as f:
            f.write(out)
    elif os.path.splitext(filePath)[1] == ".qrc":
        """Call pyside6-rcc to build a .py file from a .qrc file."""
        _checkFile(filePath, ".qrc")
        cmd = [
            os.path.join(SCRIPTS_PATH, r"pyside6-rcc.exe"),
            filePath,
            "-o",
            outFilePath,
        ]
        _runCmd(cmd)


class Build:
    """Class wrapping the building and compressing of Qt projects."""

    def __init__(self) -> None:
        pass
        
    def _listAllFilesWithExt(self, rootPath: str, ext) -> list:
        """List all files with the given extension in the given root."""
        allMatchingPaths = []
        for root, _, files in os.walk(rootPath):
            for f in files:
                if os.path.splitext(f)[1] == ext:
                    allMatchingPaths.append(os.path.join(root, f))
        return allMatchingPaths


    @staticmethod
    def _poolProcess(func, argsList) -> None:
        """Open up a multiprocessing pool with the default number of workers,
        each assigned func(args).
        """
        pool = Pool()
        processList = []
        for args in argsList:
            processList.append(pool.apply_async(func, args))
        pool.close()
        for res in processList:
            res.get()
            res.wait()
        pool.join()

    def Process(self, buildUI = True, buildRC = True) -> None:
        filesToProcess = []
        if buildUI:
            print("--- Building UI files ---")
            uiFilePaths = self._listAllFilesWithExt(ROOT_PATH, ".ui")
            for f in uiFilePaths:
                uiOutFilePath = os.path.join(
                    os.path.dirname(f),
                    f"{os.path.splitext(os.path.basename(f))[0]}_ui.py",
                )
                print(f"{f} -> {uiOutFilePath}")
                filesToProcess.append((f, uiOutFilePath))
        # QRC files are built to the root
        if buildRC:
            print("--- Building Qt resources files ---")
            rcFilePaths = self._listAllFilesWithExt(ROOT_PATH, ".qrc")
            for f in rcFilePaths:
                resOutFilePath = os.path.join(ROOT_PATH, f"{os.path.splitext(os.path.basename(f))[0]}_rc.py")
                print(f"{f} -> {resOutFilePath}")
                filesToProcess.append((f, resOutFilePath))

        # Use a process pool to build all files simultaneously
        Build._poolProcess(buildFile, filesToProcess)

if __name__ == "__main__":
    obj = Build()
    obj.Process()
