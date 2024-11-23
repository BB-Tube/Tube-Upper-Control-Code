from util import *

class Screen_Memory(object):
    def __init__(self, width = 96, height = 32, colors = [Ball.WHITE, Ball.BLACK]):
        self.width = width
        self.height = height
        self.colors = colors
        if not self.colors.contains(Ball.NONE):
            self.colors.append(Ball.NONE)
    
    def get_goal_column(self, column):
        pass
        
    def get_current_column(self, column):
        pass

    def set_goal_screen(self, goal):
        ### takes an 2d array of goal state of the screen
        ### the first dimension corresponds to the indexes of the columns
        ### the second dimension is the content of each of those columns
        ### the first dimension must match and the second dimension must 
        # never exceed the height of the screen
        if len(goal) != self.width:
            return
        pass

    def get_columns_different(self):
        return []