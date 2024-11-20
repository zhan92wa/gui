from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,QGridLayout
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QThread, pyqtSignal

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure

import time
from datetime import datetime
import sys
import Local
import Popup
import Interrupt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My PyQt Application")
        self.setGeometry(100, 100, 1200, 600)
        self.layout = QGridLayout()
        self.elements = {} # store the buttons and labels
        self.variables = {} # store the variables such as rm, smu, etc.
        self.inputs = {} # store the input fields such as start voltage, end voltage, etc
        self.outputs = {} # store the output fields such as current and data to plot
        self.timers ={} # store the timers for the buttons
        self.plots = {} # store the plots
        self.ani = None
         
        
        layout1 = QHBoxLayout()   
        layout2 = QHBoxLayout()    
        layout3 = QHBoxLayout()    
        layout4 = QHBoxLayout() 
        layout5 = QHBoxLayout()
        layout6 = QHBoxLayout()
        layout7 = QHBoxLayout()
        
        #-------------------------------------------------------------------#  
        
        b11 = self.add_button("import pyvisa", "import pyvisa", "import pyvisa", layout1, "green", "black")
        self.link_button("import pyvisa", lambda: self.run_my_pyvisa(b11))
              
        b12 = self.add_button("close program", "close program", "close program", layout1, "red", "black")
        self.link_button("close program", lambda: self.run_my_close(b12))
        
        b13 = self.add_button("interrupt loop", "interrupt loop", "interrupt loop", layout1, "yellow", "black")
        self.link_button("interrupt loop", lambda: self.stop_loop(b13))
        
        #-------------------------------------------------------------------#  
        
        b21 = self.add_button("import smu", "import smu", "import smu", layout2, "cyan", "black")
        self.link_button("import smu", lambda: self.run_my_smu(b21))
        
        b22 = self.add_button("set smu", "set smu", "set smu", layout2, "cyan", "black") 
        self.link_button("set smu", lambda: self.run_my_set_smu(b22))
        
        b23 = self.add_button("query smu", "query smu", "query smu", layout2, "cyan", "black")
        self.link_button("query smu", lambda: self.run_my_query_smu(b23))
        
        #-------------------------------------------------------------------#   
        
        b31 = self.add_button("import tec", "import tec", "import tec", layout3, "blue", "white")
        self.link_button("import tec", lambda: self.run_my_tec(b31))
        
        b32 = self.add_button("set tec", "set tec", "set tec", layout3, "blue", "white")
        self.link_button("set tec", lambda: self.run_my_set_tec(b32))
              
        #TODO: live data is stored in self.outputs[button_name], and returned data is stored in self.outputs[output_name], they are different in case that the loop is interrupted
        
        b33 = self.add_button("acquire photo", "acquire photo", "acquire photo", layout3, "navy", "white")
        self.link_button("acquire photo", lambda: self.run_my_acquire_current(b33, "current"))
        
        self.worker_thread = None
                     
        #-------------------------------------------------------------------#  
        b41 = self.add_button("search mode", "search mode", "search mode", layout4, "orange", "black")
        self.link_button("search mode", lambda: self.run_my_set_search(b41))
        
        b42 = self.add_button("continuous mode", "continuous mode", "continuous mode", layout4, "coral", "black")
        self.link_button("continuous mode", lambda: self.run_my_set_continuous(b42))
        
        b43 = self.add_button("switch mode", "switch mode", "switch mode", layout4, "orangered", "black")
        self.link_button("switch mode", lambda: self.run_my_set_switch(b43))
        
        
        #-------------------------------------------------------------------#  
        
        b51 = self.add_button("run search", "run search", "run search", layout5, "orange", "black")
        self.link_button("run search", lambda: self.run_my_search(b51, "search"))

        b52 = self.add_button("run continuous", "run continuous", "run continuous", layout5, "coral", "black")
        self.link_button("run continuous", lambda: self.run_my_continuous(b52, "continue"))

        b53 = self.add_button("run switch", "run switch", "run switch", layout5, "orangered", "black")
        self.link_button("run switch", lambda: self.run_my_switch(b53, "switch"))
        
        
        #-------------------------------------------------------------------#  
        #output_name = "current"
        b61 = self.add_button("check data", "check data", "check output and \n select one to plot", layout6)
        self.link_button("check data", lambda: self.run_my_check(b61))
        
        output_name = "current"
        b62 = self.add_button("plot data", "plot data", "", layout6)
        self.link_button("plot data", lambda: self.run_my_plot(b62, output_name))
        
        
        #-------------------------------------------------------------------#
        b71 = self.add_button("save data", "save data", "save data", layout7, "coral", "black")
        self.link_button("save data", lambda: self.run_my_set_save(b71))

        b72 = self.add_button("confirm save", "confirm save", "confirm save", layout7, "orangered", "black")
        self.link_button("confirm save", lambda: self.run_my_save(b72))
        
        
        
        
        
        self.layout.addLayout(layout1, 0, 0)
        self.layout.addLayout(layout2, 1, 0)
        self.layout.addLayout(layout3, 2, 0)
        self.layout.addLayout(layout4, 3, 0)
        self.layout.addLayout(layout5, 4, 0)
        self.layout.addLayout(layout6, 5, 0)
        self.layout.addLayout(layout7, 6, 0)
        
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setLayout(self.layout) 
        
        
        
    #------------------------------------------------------------------------------------------#    
    #------------------------------------------------------------------------------------------#  
    #------------------------------------------------------------------------------------------#   
    #------------------------------------------------------------------------------------------# 
    #------------------------------------------------------------------------------------------# 
    
    
    def stop_loop(self, button_name: str):
        if self.worker_thread:
            self.worker_thread.stop()  # Signal the worker thread to stop
            self.elements[button_name]["label"].setText("interrupt loop")
    
    def update_label(self, button_name: str, text:str):
        # Update the label in the main window
        self.elements[button_name]["label"].setText(text)
        
    def append_data(self, button_name: str, data):
        #print("in append data: ", data)
        if self.outputs.get(button_name):
            self.outputs[button_name].append(data) 
        else:
            self.outputs[button_name] = [data]    
        
    def loop_stopped(self, button_name: str):
        self.elements[button_name]["label"].setText("Loop stopped.")
    
            
    def add_button(self, description: str, button_name:str, label_name:str, layout, background_color = "white", text_color = "black") -> str:
        """
        add button function of the problem, the core of gui
        
        the function will add the button into the dictionary of buttons stored in self called self.elements, with key as the button name, and value as the description, button object, the label object, position of the button, and position of the label, as well as color information
        
        
        Args:
            description: str, the description of the button, for debugging purposes and referencing
            button_name: str, the display name of the button
            label_name: str, the display name of the label
            layout: QLayout, the layout to add the button and label to
            
        
        Returns:
            str, the button name
        """
        
        button = QPushButton(button_name, self)
        label = QLabel(label_name, self)
        button.setStyleSheet(f"background-color: {background_color}; color: {text_color};")
        
        layout.addWidget(button)
        layout.addWidget(label)
        
        self.elements[button_name] = {
            'description': description,
            'button': button,
            'label': label,
            'layout': layout,
            'background_color': background_color,
            'text_color': text_color
        }
        
        return button_name
    
    def link_button(self, button_name: str, callback) -> None:
        """
        link button function of the problem, the core of gui
        
        the function will link the button to the callback function, and the callback function will be called when the button is clicked
        
        Args:
            button_name: str, the name of the button to link
            callback: function, the function to call when the button is clicked
        """
        button = self.elements[button_name]['button']
        button.clicked.connect(callback)
        
    def store_inputs(self, input_vals, labels, display):
        # Store the inputs and update the display label
        """
        store values in the pop up window to the main windowin self.inputs as dictionary form
        
        Args:
            input_vals: list, the values of the input fields
            labels: list, the labels of the input fields
        """
        my_str = ""
        for i in range(len(input_vals)):
            self.inputs[labels[i]] = input_vals[i]
            my_str += labels[i] + ": " + input_vals[i] + "\n"
        display.setText(my_str)
        
    def change_label(self, button_name: str):
        self.elements[button_name]["label"].setText(Local.OUTPUT_SENTENCE)
            
        
    #------------------------------------------------------------------------------------------# 
    #------------------------------------------------------------------------------------------#    
    #------------------------------------------------------------------------------------------# 
    #------------------------------------------------------------------------------------------# 
    #------------------------------------------------------------------------------------------# 
        
    def run_my_pyvisa(self, button_name: str):
        """
        init pyvisa function of the problem,
        
        Args:
            button_name: str, the name of the button to link
            
        Semi - Returns:
            rm, the pyvisa resource manager, saved in variables for future use
        """
        rm = Local.my_pyvisa()  
        self.elements[button_name]["label"].setText("import done!")
        self.variables['rm'] = rm
        #print(rm)
        
    #------------------------------------------------------------------------------------------# 
    #------------------------------------------------------------------------------------------# 
        
           
    def run_my_close(self, button_name: str):
        """
        close function of the problem, and reset all button names and labels
        
        Args:
            button_name: str, the name of the button to link
        Semi - Args:
            rm: the pyvisa resource manager
            smu: the smu object
        """
        rm = self.variables['rm']
        smu = self.variables['smu']
        Local.my_close(rm, smu)
   
        for name in self.elements:
            self.elements[name]["label"].setText(name)

   
        
        
    #------------------------------------------------------------------------------------------# 
    #------------------------------------------------------------------------------------------# 
        
        
    def run_my_smu(self, button_name: str):
        """
        init smu function of the problem,
        
        Args:
            button_name: str, the name of the button to link
        Semi - Args
            rm: the pyvisa resource manager
            
        Semi - Returns:
            smu, the smu object, saved in variables for future use
        """
        smu = Local.my_smu(self.variables["rm"]) 
        self.elements[button_name]["label"].setText("smu done!")
        self.variables['smu'] = smu
        print(smu)
        
    #------------------------------------------------------------------------------------------# 
            
    def run_my_set_smu(self, button_name: str):
        """
        set smu function of the problem, including starting voltage, ending voltage, and step
        
        Args:
            button_name: str, the name of the button to link           

        """
        num_fields = 3  # Change this to the desired number of input fields
        self.popup = Popup.InputPopup(self, num_fields, ["start voltage", "end voltage", "step voltage"], self.elements[button_name]["label"])
        self.popup.show()      
        
        self.elements[button_name]["label"].setText("Please enter your values in the pop up window! ")
    
    #------------------------------------------------------------------------------------------# 
        
           
    def run_my_query_smu(self, button_name: str):
        """
        query smu function of the problem, including setting the smu object with the starting voltage, ending voltage, and step
        
        Args:
            button_name: str, the name of the button to link           

        """
        smu = self.variables['smu']
        start = float(self.inputs["start voltage"])
        stop = float(self.inputs["end voltage"])
        step = float(self.inputs["step voltage"])
        smu = Local.my_smu_query(smu, start, stop, step)
        self.variables['smu'] = smu
        
        now_time = datetime.now().strftime("%H:%M:%S")
        self.elements[button_name]["label"].setText(f"smu queryed at \n{now_time}!") 
        #TODO: change to print necessary info and time
        print(smu)
        
    #------------------------------------------------------------------------------------------# 
    #------------------------------------------------------------------------------------------# 
        
    
    def run_my_tec(self, button_name: str):
        """
        init tec function of the problem,
        
        Args:
            button_name: str, the name of the button to link           
        Semi - Args:
            rm: the pyvisa resource manager
            
        Semi - Returns:
            tec, the smu object, saved in variables for future use
        """
        tec = Local.my_tec(self.variables["rm"]) 
        self.elements[button_name]["label"].setText("tec done!")
        self.variables['tec'] = tec
        print(tec)
    
    #------------------------------------------------------------------------------------------# 
        
    def run_my_set_tec(self, button_name: str):
        """
        set tec function of the problem, including Baud_Rate, temperature, minute and current threshold
        
        Args:
            button_name: str, the name of the button to link           

        """
        num_fields = 4  # Change this to the desired number of input fields
        self.popup = Popup.InputPopup(self, num_fields, ["Baud_Rate", "temperature", "minutes", "current threshold"], self.elements[button_name]["label"])
        self.popup.show()      
        
        self.elements[button_name]["label"].setText("Please enter your values in the pop up window! default Baud_Rate is 38400, \n and please separate temperature with comma, e.g. 25, 30, 35")
        
    #------------------------------------------------------------------------------------------# 
    
    def run_my_acquire_current(self, button_name: str, output_name: str):
        if not self.worker_thread or not self.worker_thread.isRunning():
            
            self.elements[button_name]["label"].setText("Loop started.")
            temperature = self.inputs["temperature"]
            temp_list = [float(item) for item in temperature.split(',')]
            minutes = int(self.inputs["minutes"])
            current_threshold = float(self.inputs["current threshold"])
            tec = self.variables['tec']
            smu = self.variables['smu']
            extra_param = [button_name, temp_list, minutes, current_threshold, tec, smu, output_name, self.append_data]
            
            # Create a new worker thread with a dynamic callback
            self.worker_thread = Interrupt.WorkerThread(self.acquire_current_helper, extra_param)
            self.worker_thread.finished_signal.connect(lambda: self.loop_stopped(button_name))
            self.worker_thread.start()
            self.run_my_plot_live(button_name, output_name)
            
            
            
    def acquire_current_helper(self, thread, extra_param):
        [button_name, temp_list, minutes, current_threshold, tec, smu, output_name, self.append_data] = extra_param
        extra_param = [button_name, temp_list, minutes, current_threshold, tec, smu, self.append_data]
        # Example: A loop over a range that checks the thread's running flag
        if self.outputs.get(button_name):
            self.outputs[button_name] = []
        self.outputs[output_name] = Local.my_acquire_current(thread, self.update_label, extra_param)
        #print(self.outputs[output_name])
        Local.my_acquire_current(thread, self.update_label, extra_param)
        
        
    
    #------------------------------------------------------------------------------------------#
    #------------------------------------------------------------------------------------------#
    
    
    def run_my_set_search(self, button_name: str):
        num_fields = 4  # Change this to the desired number of input fields
        self.popup = Popup.InputPopup(self, num_fields, ["minutes", "V_search", "current", "filter_num"], self.elements[button_name]["label"])
        self.popup.show()      
        
        self.elements[button_name]["label"].setText("Please enter your values in the pop up window!")
        
    def run_my_set_continuous(self, button_name: str):
        num_fields = 2  # Change this to the desired number of input fields
        self.popup = Popup.InputPopup(self, num_fields, ["minutes", "voltage"], self.elements[button_name]["label"])
        self.popup.show()      
        
        self.elements[button_name]["label"].setText("Please enter your values in the pop up window!")
        
    def run_my_set_switch(self, button_name: str):
        num_fields = 3  # Change this to the desired number of input fields
        self.popup = Popup.InputPopup(self, num_fields, ["N", "voltage", "filter_num"], self.elements[button_name]["label"])
        self.popup.show()      
        
        self.elements[button_name]["label"].setText("Please enter your values in the pop up window!")
    
    #------------------------------------------------------------------------------------------#
    #------------------------------------------------------------------------------------------#
    
    def run_my_search(self, button_name: str, output_name: str):
        if not self.worker_thread or not self.worker_thread.isRunning():
            
            self.elements[button_name]["label"].setText("Loop started.")
            minutes = int(self.inputs["minutes"])
            V_search = float(self.inputs["V_search"])
            current_thres = float(self.inputs["current"])
            filter_num = int(self.inputs["filter_num"])
            tec = self.variables['tec']
            smu = self.variables['smu']
            extra_param = [button_name, minutes, V_search, current_thres, filter_num, tec, smu, output_name, self.append_data]
            
            # Create a new worker thread with a dynamic callback
            self.worker_thread = Interrupt.WorkerThread(self.search_helper, extra_param)
            self.worker_thread.finished_signal.connect(lambda: self.loop_stopped(button_name))
            self.worker_thread.start()
            self.run_my_plot_live(button_name, output_name)
            
    def search_helper(self, thread, extra_param):
        [button_name, minutes, V_search, current_thres, filter_num, tec, smu, output_name, self.append_data] = extra_param
        extra_param = [button_name, minutes, V_search, current_thres, filter_num, tec, smu, self.append_data]
        # Example: A loop over a range that checks the thread's running flag
        if self.outputs.get(button_name):
            self.outputs[button_name] = []
        self.outputs[output_name] = Local.my_search(thread, self.update_label, extra_param)
        print(self.outputs[output_name])
        
    #------------------------------------------------------------------------------------------#
        
    def run_my_continuous(self, button_name: str, output_name: str):
        if not self.worker_thread or not self.worker_thread.isRunning():
            
            self.elements[button_name]["label"].setText("Loop started.")
            minutes = int(self.inputs["minutes"])
            V_search = float(self.inputs["V_search"])
            tec = self.variables['tec']
            smu = self.variables['smu']
            extra_param = [button_name, minutes, V_search, tec, smu, output_name, self.append_data]
            
            # Create a new worker thread with a dynamic callback
            self.worker_thread = Interrupt.WorkerThread(self.continuous_helper, extra_param)
            self.worker_thread.finished_signal.connect(lambda: self.loop_stopped(button_name))
            self.worker_thread.start()
            self.run_my_plot_live(button_name, output_name)
            
    def continuous_helper(self, thread, extra_param):
        [button_name, minutes, V_search, tec, smu, output_name, self.append_data] = extra_param
        extra_param = [button_name, minutes, V_search, tec, smu, self.append_data]
        # Example: A loop over a range that checks the thread's running flag
        if self.outputs.get(button_name):
            self.outputs[button_name] = []
        self.outputs[output_name] = Local.my_continuous(thread, self.update_label, extra_param)
        print(self.outputs[output_name])
        
    #------------------------------------------------------------------------------------------#
        
    def run_my_switch(self, button_name: str, output_name: str):
        if not self.worker_thread or not self.worker_thread.isRunning():
            
            self.elements[button_name]["label"].setText("Loop started.")
            N = int(self.inputs["N"])
            V_search = float(self.inputs["V_search"])
            filter_num = int(self.inputs["filter_num"])
            tec = self.variables['tec']
            smu = self.variables['smu']
            extra_param = [button_name, N, V_search, filter_num, tec, smu, output_name, self.append_data]
            
            # Create a new worker thread with a dynamic callback
            self.worker_thread = Interrupt.WorkerThread(self.switch_helper, extra_param)
            self.worker_thread.finished_signal.connect(lambda: self.loop_stopped(button_name))
            self.worker_thread.start()
            self.run_my_plot_live(button_name, output_name)
            
    def switch_helper(self, thread, extra_param):
        [button_name, N, V_search, filter_num, tec, smu, output_name, self.append_data] = extra_param
        extra_param = [button_name, N, V_search, filter_num, tec, smu, self.append_data]
        # Example: A loop over a range that checks the thread's running flag
        if self.outputs.get(button_name):
            self.outputs[button_name] = []
        self.outputs[output_name] = Local.my_switch(thread, self.update_label, extra_param)
        print(self.outputs[output_name])
        
        
    
    
    
    #------------------------------------------------------------------------------------------#
    #------------------------------------------------------------------------------------------#
    
    def run_my_check(self, button_name: str):
        my_keys = self.outputs.keys()       
        my_str = ""
        for key in my_keys:
            my_str += key + "\n"
        num_fields = 1  # Change this to the desired number of input fields
        self.popup = Popup.InputPopup(self, num_fields, ["current output name"], self.elements[button_name]["label"])
        self.popup.show()  
        self.elements[button_name]["label"].setText(my_str) 
        
        
    #------------------------------------------------------------------------------------------#
    
    def run_my_plot(self, button_name: str, output_name:str):  
        
        output_name = self.inputs["current output name"]      #override the output_name

        if self.outputs.get(output_name) is None:
            self.elements[button_name]["label"].setText("No data to plot!")
            return
        
        figure = Figure(figsize=(10, 8))
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas, self)  
        
        myplot = {"figure": figure, 
                  "canvas": canvas, 
                  "toolbar": toolbar
                  }
        self.plots[output_name] = myplot
        
        self.layout.addWidget(myplot["canvas"], 0, 20, 7, 8)
        self.layout.addWidget(myplot["toolbar"], 8, 20, 1, 8)
        myplot["ax"] = myplot["figure"].add_subplot(111)
        
        print(self.outputs[output_name])
        
        myplot["x"] = np.linspace(1,len(self.outputs[output_name]),len(self.outputs[output_name])) 
        myplot["y"] =  self.outputs[output_name]
        myplot["line"], = myplot["ax"].plot(myplot["x"], myplot["y"], label="Sine Wave")
        myplot["ax"].set_title("Interactive Plot Example")
        myplot["ax"].set_xlabel("X Axis")
        myplot["ax"].set_ylabel("Y Axis")
        myplot["ax"].legend()
        myplot["ax"].grid(True) 
        myplot["canvas"].draw()
    
    #------------------------------------------------------------------------------------------#


    def run_my_plot_live(self, button_name, output_name: str):
        figure = Figure(figsize=(10, 8))
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas, self)  
        
        myplot = {
            "figure": figure, 
            "canvas": canvas, 
            "toolbar": toolbar
        }
        self.plots[output_name] = myplot
        self.layout.addWidget(myplot["canvas"], 0, 20, 7, 8)
        self.layout.addWidget(myplot["toolbar"], 8, 20, 1, 8)
        
        myplot["ax"] = myplot["figure"].add_subplot(111)
        myplot["x"] = []
        myplot["y"] = []
        myplot["line"], = myplot["ax"].plot(myplot["x"], myplot["y"], label="Dynamic Data")
        
        myplot["ax"].set_title("Interactive Plot Example")
        myplot["ax"].set_xlabel("X Axis")
        myplot["ax"].set_ylabel("Y Axis")
        myplot["ax"].legend()
        myplot["ax"].grid(True)
        myplot["canvas"].draw()
        
        self.ani = FuncAnimation(figure, self.update_plot, fargs = (myplot["x"], myplot["y"], myplot["line"], myplot["ax"], button_name), interval=1000, blit=False, cache_frame_data=False)
        

    def update_plot(self, frame, myplotx, myploty, myplotline, myplotax, button_name):
        myplotx.append(len(myplotx))
        myploty.append(self.outputs[button_name][-1])  # Replace with actual data fetching logic
        
        myplotline.set_data(myplotx, myploty)
        myplotax.set_xlim(0, max(1, len(myplotx)))
        myplotax.set_ylim(-5, max(1, max(myploty) + 1))
        
        return myplotline
    
    #------------------------------------------------------------------------------------------#
    #------------------------------------------------------------------------------------------#
    #------------------------------------------------------------------------------------------#
    
    def run_my_set_save(self, button_name: str):
        num_fields = 2
        self.popup = Popup.InputPopup(self, num_fields, ["data name", "file name"], self.elements[button_name]["label"])
        self.popup.show()      
        
        self.elements[button_name]["label"].setText("check data name using check!")
        
    def run_my_save(self, button_name: str):
        data_name = self.inputs["data name"]
        file_name = self.inputs["file name"]
        data = self.outputs[data_name]
        np.save( file_name, data)
        self.elements[button_name]["label"].setText("data saved!")
        
        
        
       

        
            
            
        
        
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())