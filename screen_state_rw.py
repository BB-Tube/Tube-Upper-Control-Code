import json
from datetime import datetime
from util import *
import numpy as np

class ScreenStateRW:
    def __init__(self, filename):
        self.filename = filename
        try:
            self.load_screen()
        except FileNotFoundError:
            self.columns = 0
            self.rows = 0
            self.screen = []
            self.edit_time = None

    def load_screen(self):
        """Load the screen state from the JSON file."""
        with open(self.filename, 'r') as f:
            data = json.load(f)
        self.columns = data['columns']
        self.rows = data['rows']
        self.screen = data['screen']
        self.edit_time = data.get('edit_time')

    def save_screen(self):
        """Save the current screen state to the JSON file."""
        data = {
            'columns': self.columns,
            'rows': self.rows,
            'edit_time': datetime.now().isoformat(),
            'screen': self.screen
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def get_number_columns(self):
        """Return the number of columns."""
        return self.columns

    def get_number_rows(self):
        """Return the number of rows."""
        return self.rows

    def get_edit_time(self):
        """Return the last edit time."""
        return self.edit_time

    def read_column(self, col_index):
        """
        Return the data of a specific column as a string.
        :param col_index: Index of the column to read.
        """
        self.load_screen()
        if 0 <= col_index < self.columns:
            column_data_chars = self.screen[col_index]
        else:
            raise IndexError("Column index out of range.")
        
        column_data = np.full(self.get_number_rows(), Ball.NONE)
        
        for i in range(len(column_data_chars)):
            column_data[i] = ball_reverse_index(column_data_chars[i])

        return column_data

    def write_column(self, col_index, column_data):
        """
        Write data to a specific column.
        :param col_index: Index of the column to write.
        :param column_data: array of pixels in the column
        """

        column_data_chars = ''.join(enum.value for enum in column_data)
        
        if 0 <= col_index < self.columns:
            if len(column_data_chars) > self.rows:
                raise ValueError("Column data exceeds number of rows.")
            self.screen[col_index] = column_data_chars
            # Replace the edit time
            self.save_screen()
        else:
            raise IndexError("Column index out of range.")

    def write_empty_screen(self, columns, rows):
        """
        Initialize or reset the screen to an empty state.
        :param columns: Number of columns.
        :param rows: Number of rows.
        """
        self.columns = columns
        self.rows = rows
        empty_column = ""
        self.screen = [empty_column for _ in range(columns)]
        # Replace the edit time
        self.save_screen()

if __name__ == "__main__":
    # Initialize the screen state with a JSON file
    screen = ScreenState('screen_state_now.json')

    # Write an empty screen with specified dimensions
    # screen.write_empty_screen(columns=96, rows=32)

    # Get the number of columns and rows
    num_columns = screen.get_number_columns()
    num_rows = screen.get_number_rows()
    print(f"Columns: {num_columns}, Rows: {num_rows}")

    # Read a column
    column_data = screen.read_column(0)
    print(f"Column 0 data: '{column_data}'")

    # Write to a column
    new_column_data = [Ball.BLACK, Ball.WHITE, Ball.BLACK, Ball.WHITE]  # 'X' at bottom (row 0), 'O' above it (row 1), empty spaces above
    screen.write_column(0, new_column_data)
    print(f"Updated Column 0 data: '{screen.read_column(0)}'")

    # Get the last edit time
    last_edit = screen.get_edit_time()
    print(f"Last edit time: {last_edit}")