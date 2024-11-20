from PyQt5.QtCore import QThread, pyqtSignal
import sys
import time


class WorkerThread(QThread):
    finished_signal = pyqtSignal()  # Signal to indicate the loop has stopped

    def __init__(self, callback, *args):
        super().__init__()
        self.callback = callback  # Callback function
        self.args = args          # Additional arguments for the callback
        self.running = True       # Control flag for the loop

    def run(self):
        # Call the callback function with the control flag and additional arguments
        if self.callback:
            self.callback(self, *self.args)  # Pass the thread and additional arguments
        self.finished_signal.emit()

    def stop(self):
        self.running = False  # Set flag to False to stop the loop