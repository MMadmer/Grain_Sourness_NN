import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QFileDialog,
                             QLineEdit)
from functools import partial
import viewer


def tryConvert(default_value, le):
    try:
        value = float(le.text())
        return value
    except ValueError:
        le.setText(str(default_value))
        return default_value


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        # Vars block
        self.localFourierPath = None
        self.PATH_BLOCK_Y = 0.05
        self.PATH_BLOCK_BASE_DISTANCE = 10
        self.pathBlockSize = None
        self.lePath = None
        self.LE_PATH_BASE_WIDTH = 300
        self.btnChooseFile = None
        self.BTN_CHOOSE_IMAGE_BASE_WIDTH = 100
        self.PATH_BLOCK_WIDTH = self.LE_PATH_BASE_WIDTH + \
                                self.BTN_CHOOSE_IMAGE_BASE_WIDTH + \
                                self.PATH_BLOCK_BASE_DISTANCE

        # Window vars
        self.minWindowSize = [self.PATH_BLOCK_WIDTH + 20, 160]

        # Buttons
        self.btnOriginal = None
        self.btnFourier = None
        self.btnLocalFourier = None
        self.leDownBorder = None
        self.leUpBorder = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Signal viewer")
        self.setGeometry(int(self.screen().size().width() / 2 - self.minWindowSize[0] / 2),
                         int((self.screen().size().height() / 2 - self.minWindowSize[1] / 2) * 0.8),
                         self.minWindowSize[0],
                         self.minWindowSize[1])
        self.setFixedSize(self.minWindowSize[0], self.minWindowSize[1])

        # Txt block
        self.btnChooseFile = QPushButton("Browse file", self)
        self.lePath = QLineEdit(self)
        self.lePath.setGeometry(int(self.minWindowSize[0] / 2 - self.PATH_BLOCK_WIDTH / 2),
                                int(self.minWindowSize[1] * self.PATH_BLOCK_Y),
                                self.LE_PATH_BASE_WIDTH,
                                25)
        self.btnChooseFile.clicked.connect(partial(self.onClicked, 0))

        # -----------------
        # Buttons block
        # -----------------

        # Original
        self.btnOriginal = QPushButton("Show original", self)
        self.btnOriginal.clicked.connect(partial(self.onClicked, 1))
        self.btnOriginal.move(170, 50)

        # Fourier
        self.btnFourier = QPushButton("Fourier", self)
        self.btnFourier.clicked.connect(partial(self.onClicked, 2))
        self.btnFourier.move(100, 90)

        # Local Fourier
        self.btnLocalFourier = QPushButton("Local Fourier", self)
        self.btnLocalFourier.clicked.connect(partial(self.onClicked, 3))
        self.btnLocalFourier.move(int(self.btnFourier.x() + self.btnFourier.width()) + 42, self.btnFourier.y())
        self.localFourierPath = ''

        self.leDownBorder = QLineEdit(self)
        self.leDownBorder.setGeometry(self.btnLocalFourier.x() - 10, self.btnLocalFourier.y() + 27,
                                      40, 20)
        self.leUpBorder = QLineEdit(self)
        self.leUpBorder.setGeometry(self.btnLocalFourier.x() + 45, self.btnLocalFourier.y() + 27,
                                    40, 20)

    def onClicked(self, index):
        filePath = self.lePath.text()
        pol_sig = [tryConvert(0, self.leDownBorder), tryConvert(1, self.leUpBorder)]

        btnFinder = {
            0: self.onBrowseClick,
            1: viewer.original,
            2: viewer.fourier,
            3: viewer.local_fourier
        }

        if index == 0:
            func = btnFinder.get(index)
            func(index)
        elif filePath:
            if index == 3:
                func = btnFinder.get(index)
                func(filePath, pol_sig)
            else:
                func = btnFinder.get(index)
                func(filePath)
        else:
            pass

    def browse(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Browse file", "",
                                                  "txt files (*.txt)",
                                                  options=options)
        return filePath

    def onBrowseClick(self, index):
        if index == 0:
            filePath = self.browse()
        else:
            filePath = self.lePath.text()

        if filePath:
            self.lePath.setText(f"{filePath}")

    def resizeEvent(self, event):
        new_width = event.size().width()
        new_height = event.size().height()

        if new_width < self.minWindowSize[0]:
            self.resize(self.minWindowSize[0], new_height)
            new_width = self.minWindowSize[0]
        if new_height < self.minWindowSize[1]:
            self.resize(new_width, self.minWindowSize[1])
            new_height = self.minWindowSize[1]

        new_pathBlockX = int(new_width / 2 - self.PATH_BLOCK_WIDTH / 2)
        new_pathBlockY = int(new_height * self.PATH_BLOCK_Y)
        self.lePath.move(new_pathBlockX, new_pathBlockY)
        self.btnChooseFile.move(int(new_pathBlockX + self.lePath.width() + self.PATH_BLOCK_BASE_DISTANCE),
                                new_pathBlockY)

        QWidget.resizeEvent(self, event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
