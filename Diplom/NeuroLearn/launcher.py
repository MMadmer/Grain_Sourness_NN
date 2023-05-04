import tkinter
import customtkinter
import os
import time
from functools import partial

import utils
import Grain_Sourness_NN as NN
import threading


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Vars block
        self.can_calculating = False

        # Buttons
        self.btnMLP = None
        self.btnReg = None
        self.btnStopNeuralNet = None
        self.btnADC = None
        self.btnSignal = None
        self.btnFourier = None
        self.btnResults = None
        self.btnCompileSignal = None
        self.leDownBorder = None

        # Checkbox
        self.checkFilter = None

        self.initUI()

    def initUI(self):
        # Theme
        customtkinter.set_appearance_mode("Dark")

        # Main window
        self.geometry("600x500")
        self.title("Grain sourness")

        # -----------------
        # Buttons block
        # -----------------

        # Local NN
        self.leDownBorder = customtkinter.CTkEntry(self, placeholder_text="-1")
        self.leDownBorder.place(relx=0.5, rely=0.1, anchor=tkinter.CENTER)

        self.btnReg = customtkinter.CTkButton(self, text="Start regressive", command=partial(self.start_nn, 1))
        self.btnReg.place(relx=0.35, rely=0.2, anchor=tkinter.CENTER)

        self.btnMLP = customtkinter.CTkButton(self, text="Start classifier", command=partial(self.start_nn, 2))
        self.btnMLP.place(relx=0.65, rely=0.2, anchor=tkinter.CENTER)

        self.btnStopNeuralNet = customtkinter.CTkButton(self, text="Stop neural network", command=self.stop_nn)
        self.btnStopNeuralNet.place(relx=0.5, rely=0.35, anchor=tkinter.CENTER)

        # Checkbox
        self.checkFilter = customtkinter.CTkCheckBox(self, text="Noise filter", onvalue=True, offvalue=False)
        self.checkFilter.select()
        self.checkFilter.place(relx=0.3, rely=0.35, anchor=tkinter.CENTER)

        # Full signal
        self.btnSignal = customtkinter.CTkButton(self, text="Show full signal", command=utils.show_signal)
        self.btnSignal.place(relx=0.2, rely=0.7, anchor=tkinter.CENTER)

        # Compile signal
        self.btnCompileSignal = customtkinter.CTkButton(self, text="Compile signal", command=utils.compile_signal)
        self.btnCompileSignal.place(relx=0.5, rely=0.7, anchor=tkinter.CENTER)

        # Fourier
        self.btnFourier = customtkinter.CTkButton(self, text="Show last fourier", command=utils.show_fourier)
        self.btnFourier.place(relx=0.8, rely=0.7, anchor=tkinter.CENTER)

        # Results
        self.btnResults = customtkinter.CTkButton(self, text="Show results", command=utils.show_results)
        self.btnResults.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    def start_nn(self, mode):
        # print(threading.active_count())
        # print(self.can_calculating)
        if self.can_calculating:
            return

        if os.path.exists("result.txt"):
            os.remove("result.txt")

        self.can_calculating = True
        thread = threading.Thread(target=self.neural_network, args=(mode,))
        thread.start()

    def stop_nn(self):
        self.can_calculating = False
        # print(threading.active_count())
        # print(self.can_calculating)

    def neural_network(self, mode):
        while self.can_calculating:
            thread = threading.Thread(target=NN.main,
                                      args=(mode, self.checkFilter.get(), self.leDownBorder.get(),))
            thread.start()
            thread.join()
            time.sleep(1)


if __name__ == "__main__":
    app = App()
    app.mainloop()
