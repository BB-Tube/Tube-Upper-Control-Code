class Screen(object):    
    def __init__(self, name = "Screen", width = 96, height = 32, current, final):
        self.name = name
        self.width = width
        self.height = height
        
        self.pixel_states = []
        
        self.screen_current_state = current_state
        self.screen_desitation_state = final_state
        
    def set_column(self, column, state):
        if column < 0 or column >= self.width:
            raise ValueError("Column number must be between 0 and {}".format(self.width - 1))
        self.current_column[column] = state
        
    