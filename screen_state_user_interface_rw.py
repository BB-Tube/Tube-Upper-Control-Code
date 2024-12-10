import json
from datetime import datetime
from util import *
import numpy as np

class ScreenStateUserIntefaceRW:
    def __init__(self, columns:int, rows :int, filename):
        self.filename = filename
        self.state_counter = None
        self.screen = None
        
        self.load_state_counter()
        self.load_screen()

        self.logged_state_counter = self.state_counter

        self.columns = columns
        self.rows = rows

        # self.write_empty_screen()

    def load_state_counter(self):
        """Load the screen state from the JSON file."""
        with open(self.filename, 'r') as f:
            data = json.load(f)
        self.state_counter = data.get('state_counter')

    def load_screen(self):
        """Load the screen state from the JSON file."""
        with open(self.filename, 'r') as f:
            data = json.load(f)
        self.screen = np.array(data['state'])
        self.state_counter = data.get('state_counter')

    def save_screen(self):
        """Save the current screen state to the JSON file."""
        data = {
            'state_counter': self.state_counter,
            'state': self.screen.tolist(),
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def should_update(self):
        "check if the state counter has been changed"
        self.load_state_counter()
        return self.state_counter != self.logged_state_counter

    def did_update(self):
        "after updating the target for the screen, update the state counter so that it can be noted that the update was transferred"
        self.logged_state_counter = self.state_counter

    def read_column(self, col_index):
        """
        Return the data of a specific column as a string.
        :param col_index: Index of the column to read.
        """
        self.load_screen()
        # print(col_index)
        if 0 <= col_index < self.columns:
            column_data_chars = self.screen[col_index]
        else:
            raise IndexError("Column index out of range.")
        
        column_data = np.full(self.rows, Ball.NONE)
        
        for i in range(len(column_data_chars)):
            column_data[i] = ball_reverse_index(column_data_chars[i])

        return column_data

    def read_screen(self):
        screen = np.full(self.columns, None)
        for i in range(self.columns):
            screen[i] = self.read_column(i)
        return screen

    def write_screen(self, screen_data):
        for i in range(self.columns):
            self.write_column(i, screen[i])

    def write_column(self, col_index, column_data):
        """
        Write data to a specific column.
        :param col_index: Index of the column to write.
        :param column_data: array of pixels in the column
        """

        column_data_chars = np.full((self.rows), "")
        # print("column_data_chars")
        # print(column_data_chars)
        for i in range(len(column_data)):
            column_data_chars[i] = column_data[i].value
            # print()
            # print(i)
            # print(column_data_chars[i])
            # print(column_data[i])

        self.screen[col_index] = column_data_chars
        print()
        print("column_data")
        print(column_data)
        print()
        print("column_data_chars")
        print(column_data_chars)
        self.save_screen()

    def write_empty_screen(self):
        """
        Initialize or reset the screen to an empty state.
        :param columns: Number of columns.
        :param rows: Number of rows.
        """
        self.screen = np.full((self.columns, self.rows), " ")
        self.save_screen()

if __name__ == "__main__":
    # Initialize the screen state with a JSON file
    
    screen = ScreenStateUserIntefaceRW(96, 32, '/home/balltube2/Documents/Tube-UI/public/state.json')
    # print(screen.state_counter)
    # print(screen.read_column(0))
    np_list_black_balls = np.full(32, [Ball.BLACK])
    list_black_balls = np_list_black_balls.tolist()
    print("np :     ", type(np_list_black_balls))
    print("list :   ", type(list_black_balls))
    screen.write_column(2, list_black_balls)
    print("read column")
    print(screen.read_column(0))

    while(True):
        time.sleep(.1)
        print(screen.state_counter)
        if screen.should_update():
            print("farts")
            print("state_counter :  ", screen.logged_state_counter)
            screen.did_update()
            print("state_counter :  ", screen.logged_state_counter)