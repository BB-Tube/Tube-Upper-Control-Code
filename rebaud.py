from util_gyz.dynamixel import Dynamixel, Mode
import math

### Variables
BAUD_DYNAMIXELS = 1000000
PORT_DYNAMIXELS = "/dev/ttyACM0"
ID_EMPTIER = 12
ID_SUSAN = 13
ID_SORTER_REVOLVER = 14
ID_SORTER_ARM = 15
ID_DISPO_INSERTER = 16
ID_DISPO_WHITE = 17
ID_DISPO_BLACK = 18
ID_ELEVATOR = 20

emptier = Dynamixel(
    id = ID_EMPTIER,
    port = PORT_DYNAMIXELS,
    baudrate = BAUD_DYNAMIXELS)
susan = Dynamixel(
    id = ID_SUSAN,
    port = PORT_DYNAMIXELS,
    baudrate = BAUD_DYNAMIXELS)
sorter_revolver = Dynamixel(
    id = ID_SORTER_REVOLVER,
    port = PORT_DYNAMIXELS,
    baudrate = BAUD_DYNAMIXELS)
sorter_arm = Dynamixel(
    id = ID_SORTER_ARM,
    port = PORT_DYNAMIXELS,
    baudrate = BAUD_DYNAMIXELS)
dispo_inserter = Dynamixel(
    id = ID_DISPO_INSERTER,
    port = PORT_DYNAMIXELS,
    baudrate = BAUD_DYNAMIXELS)
dispo_white = Dynamixel(
    id = ID_DISPO_WHITE,
    port = PORT_DYNAMIXELS,
    baudrate = BAUD_DYNAMIXELS)
dispo_black = Dynamixel(
    id = ID_DISPO_BLACK,
    port = PORT_DYNAMIXELS,
    baudrate = BAUD_DYNAMIXELS)
elevator = Dynamixel(
    id = ID_ELEVATOR,
    port = PORT_DYNAMIXELS,
    baudrate = BAUD_DYNAMIXELS)

motors = [emptier, susan, sorter_revolver, sorter_arm, dispo_inserter, dispo_white, dispo_black, elevator]
for motor in motors:
    motor.off()
    print()
    print(motor.name)
    print(motor.get_model())
    print(motor.get_baud_rate())

sorter_revolver.set_mode(Mode.VELOCITY)
sorter_revolver.on()
sorter_revolver.set_goal_velocity(-math.tau)