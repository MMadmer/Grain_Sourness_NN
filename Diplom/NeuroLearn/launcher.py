import sys
import time

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QCheckBox)
from functools import partial
import utils
import Grain_Sourness_NN as NN
import threading


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        # Vars block
        self.PATH_BLOCK_Y = 0.05
        self.PATH_BLOCK_BASE_DISTANCE = 10
        self.pathBlockSize = None
        self.LE_PATH_BASE_WIDTH = 300
        self.BTN_CHOOSE_IMAGE_BASE_WIDTH = 100
        self.PATH_BLOCK_WIDTH = self.LE_PATH_BASE_WIDTH + \
                                self.BTN_CHOOSE_IMAGE_BASE_WIDTH + \
                                self.PATH_BLOCK_BASE_DISTANCE
        self.can_calculating = False

        # Window vars
        self.minWindowSize = [self.PATH_BLOCK_WIDTH + 20, 160]

        # Buttons
        self.btnMLP = None
        self.btnReg = None
        self.btnStopNeuralNet = None
        self.btnADC = None
        self.btnSignal = None
        self.btnFourier = None

        # Checkbox
        self.checkFilter = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Grain sourness")
        self.setGeometry(int(self.screen().size().width() / 2 - self.minWindowSize[0] / 2),
                         int((self.screen().size().height() / 2 - self.minWindowSize[1] / 2) * 0.8),
                         self.minWindowSize[0],
                         self.minWindowSize[1])
        self.setFixedSize(self.minWindowSize[0], self.minWindowSize[1])

        # -----------------
        # Buttons block
        # -----------------

        self.btnADC = QPushButton("Start ADC", self)
        self.btnADC.clicked.connect(partial(utils.launch_ADC))
        self.btnADC.move(175, 100)

        self.btnReg = QPushButton("Start regressive", self)
        self.btnReg.clicked.connect(partial(self.start_nn, 1))
        self.btnReg.move(120, 25)

        self.btnMLP = QPushButton("Start classifier", self)
        self.btnMLP.clicked.connect(partial(self.start_nn, 2))
        self.btnMLP.move(self.btnReg.x() + self.btnReg.width(), self.btnReg.y())

        self.btnStopNeuralNet = QPushButton("Stop neural network", self)
        self.btnStopNeuralNet.clicked.connect(partial(self.stop_nn))
        self.btnStopNeuralNet.move(self.btnReg.x() + 35,
                                   self.btnReg.y() + 30)

        # Checkbox
        self.checkFilter = QCheckBox("Noise filter", self)
        self.checkFilter.move(20, 50)

        # Fourier
        self.btnFourier = QPushButton("Show last fourier", self)
        self.btnFourier.clicked.connect(partial(utils.show_fourier))
        self.btnFourier.move(self.btnADC.x() + self.btnADC.width() + 5, self.btnADC.y())

        # Local Fourier
        self.btnSignal = QPushButton("Show full signal", self)
        self.btnSignal.clicked.connect(partial(utils.show_signal))
        self.btnSignal.move(self.btnADC.x() - self.btnSignal.width() - 5, self.btnADC.y())

    def start_nn(self, mode):
        # print(threading.active_count())
        # print(self.can_calculating)
        if self.can_calculating:
            return

        self.can_calculating = True
        thread = threading.Thread(target=self.neural_network, args=(mode,))
        thread.start()

    def stop_nn(self):
        self.can_calculating = False
        # print(threading.active_count())
        # print(self.can_calculating)

    def neural_network(self, mode):
        while self.can_calculating:
            thread = threading.Thread(target=NN.main, args=(mode, self.checkFilter.isChecked(),))
            thread.start()
            thread.join()
            time.sleep(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
