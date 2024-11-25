from screen_state_rw import ScreenStateRW
from util import *
import numpy as np

class ScreenStateHandler(object):
    def __init__(self, now_rw : ScreenStateRW, goal_rw : ScreenStateRW) -> None:
        if (now_rw.get_number_columns() != goal_rw.get_number_columns() or
            now_rw.get_number_rows() != goal_rw.get_number_rows()):
            raise ValueError
        self.now = now_rw
        self.goal = goal_rw
        self.row_count = self.now.get_number_rows()
        self.column_count = self.now.get_number_columns()

    def get_list_different_columns(self):
        columns_with_differences = []
        for i in range(self.column_count):
            if not np.array_equal(self.now.read_column(i), self.goal.read_column(i)):
                columns_with_differences.append(i)
        return columns_with_differences

if __name__ == "__main__":
    now = ScreenStateRW('screen_state_now.json')
    goal = ScreenStateRW('screen_state_goal.json')
    memory_handler = ScreenStateHandler(now, goal)

    ball_array = np.full(32, Ball.BLACK)

    for i in range(96):
        print(i)
        goal.write_column(i, ball_array)

    print(memory_handler.get_list_different_columns())
