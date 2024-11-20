from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,QGridLayout
import sys
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt


class InputPopup(QWidget):
    def __init__(self, main_window, num_fields, labels, display):
        super().__init__()
        self.setWindowTitle("Input Popup")
        self.setGeometry(200, 200, 400, 200)

        # Reference to the main window to store inputs
        self.main_window = main_window

        # Number of input fields
        self.num_fields = num_fields

        # List to store dynamically created input fields
        self.input_fields = []

        # Layout for input fields
        layout = QVBoxLayout()

        # Dynamically create input fields
        for i in range(num_fields):
            row_layout = QHBoxLayout()  # Create a horizontal layout for each row
            label = QLabel(labels[i], self)  # Label as a reminder
            input_field = QLineEdit(self)  # Input field
            my_str = "Enter your " + labels[i] + " here"
            input_field.setPlaceholderText(my_str)

            # Add the label and input field to the row layout
            row_layout.addWidget(label)
            row_layout.addWidget(input_field)

            # Add the row layout to the main layout
            layout.addLayout(row_layout)

            # Store the input field for later access
            self.input_fields.append(input_field)

        # Submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(lambda: self.submit_inputs(labels, display))  # Connect to submission method
        layout.addWidget(self.submit_button)

        # Set layout for the popup
        self.setLayout(layout)

    def submit_inputs(self, labels, display):
        # Get inputs from the fields
        inputs = [field.text() for field in self.input_fields]

        # Pass inputs to the main window
        self.main_window.store_inputs(inputs, labels, display)

        # Close the popup window
        self.close()