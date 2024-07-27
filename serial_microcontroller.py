import serial
import time
from util import *
from collections import Counter

class Default():
    PORT = '/dev/ttyACM0'
    BAUD = 9600
    
    COLOR_SENSOR_ASK_KEY = '-'
    SUSAN_HALL_ASK_KEY = 's'
    SUSAN_HALL_PASS_KEY = '1'
    ASK_WHITE =         'e'
    ASK_BLACK =         'n'
    ANSWER_LOADED =     '1'
    ANSWER_UNLOADED =   '0'
    SORTER_LIGHT_OFF_KEY = 'l'
    SORTER_LIGHT_ON_KEY = 'k'

class SerialMicrocontroller(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SerialMicrocontroller, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, port=Default.PORT, baudrate=Default.BAUD):
        if not hasattr(self, 'cereal'):
            self.cereal = serial.Serial(port, baudrate)

    def __sendMessage(self, stringg):
        timeout = 0.01  # Timeout value in seconds
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.cereal.write(stringg.encode())
            echo_message = self.cereal.readline().decode(errors='ignore').strip()
            if echo_message:
                return echo_message
        return None

    def read_sensor(self, message):
        while(True):
            reading = self.__sendMessage(message)
            if reading is None:
                pass
            else:
                return reading
            
    def sorter_light_on(self):
        self.__sendMessage(Default.SORTER_LIGHT_ON_KEY)

    def sorter_light_off(self):
        self.__sendMessage(Default.SORTER_LIGHT_OFF_KEY)

    def get_color_sensor(self):        
        return ball_reverse_index(self.read_sensor(Default.COLOR_SENSOR_ASK_KEY))

    def get_susan_hall(self):
        return not self.read_sensor(Default.SUSAN_HALL_ASK_KEY) == Default.SUSAN_HALL_PASS_KEY

    def get_white_dispo_sensor(self):
        reading = self.read_sensor(Default.ASK_WHITE)
        if reading == Default.ANSWER_LOADED:
            return True
        elif reading == Default.ANSWER_UNLOADED:
            return False
        else: 
            return None

    def get_black_dispo_sensor(self):
        reading = self.read_sensor(Default.ASK_BLACK)
        if reading == Default.ANSWER_LOADED:
            return True
        elif reading == Default.ANSWER_UNLOADED:
            return False
        else: 
            return None

if __name__ == "__main__":
    serial = SerialMicrocontroller()
    light_state = False
    while(True):
        print()
        time.sleep(0.2)
        light_state = not light_state
        if light_state:
            serial.sorter_light_on()
        else:
            serial.sorter_light_on()
        print(serial.get_color_sensor())
        print(serial.get_susan_hall())
        print("White : ", serial.get_white_dispo_sensor())
        print("Black : ", serial.get_black_dispo_sensor())
