print(" hello world ")

from util_gyz.dynamixel import Dynamixel
from util_gyz.abstract_motor import *
import math

port = "/dev/ttyUSB0"
baud = 57600
mot =Dynamixel(id = 13, port=port, baudrate=baud, name="Susan")

mot.off()
mot.set_mode(Mode.VELOCITY)
# mot.oxn()
print(mot.get_model())
mot.set_goal_velocity(math.tau)