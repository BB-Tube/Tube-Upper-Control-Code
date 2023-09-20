import os
import time

invOpModes = {
    0:"Current",
    1:"Velocity",
    3:"Position",
    4:"Extended_Position",
    5:"Current-based_Position",
    16:"PWM"
}

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
from dynamixel_sdk import * # Uses Dynamixel SDK library

# Control table address
ONE_BYTE                    = int("FF", 16)
TWO_BYTE                    = int("FFFF", 16)
FOUR_BYTE                   = int("FFFFFFFF", 16)
ADDR_OPERATING_MODE         = 11
ADDR_TORQUE_ENABLE          = 64
ADDR_GOAL_PWM               = 100
ADDR_GOAL_CURRENT           = 102
ADDR_GOAL_VELOCITY          = 104
ADDR_PROFILE_ACCELERATION   = 108
MINIMUM_PROFILE_ACCELERATION= 0
MAXIMUM_PROFILE_ACCELERATION= 32767
REV_SQUARED_PER_TICK        = 214.577
ADDR_PROFILE_VELOCITY       = 112
MINIMUM_PROFILE_VELOCITY    = 0
MAXIMUM_PROFILE_VELOCITY    = 32767
ADDR_PROFILE_VELOCITY       = 112
ADDR_GOAL_POSITION          = 116
ADDR_PRESENT_PWM            = 124
ADDR_PRESENT_CURRENT        = 126
ADDR_PRESENT_VELOCITY       = 128
ADDR_PRESENT_POSITION       = 132
ADDR_PRESENT_TEMPERATURE    = 146
MINIMUM_POSITION_VALUE      = 0         # Refer to the Minimum Position Limit of product eManual
MAXIMUM_POSITION_VALUE      = 4095      # Refer to the Maximum Position Limit of product eManual
TICK_PER_DEGREE             = 4096 / 360
MINIMUM_VELOCITY_VALUE      = -1624
MAXIMUM_VELOCITY_VALUE      = 1624
RPM_PER_TICK                = 0.229
MINIMUM_CURRENT_VALUE       = -1188
MAXIMUM_CURRENT_VALUE       = 1188
MILLI_AMP_PER_TICK          = 2.69
MINIMUM_PWM_VALUE           = -885
MAXIMUM_PWM_VALUE           = 885
PWM_PER_TICK                = 0.113

MAXIMUM_MILLI_AMPS          = MAXIMUM_CURRENT_VALUE * MILLI_AMP_PER_TICK
MAXIMUM_RPM                 = MAXIMUM_VELOCITY_VALUE * RPM_PER_TICK
MAXIMUM_ACCELERATION        = MAXIMUM_PROFILE_ACCELERATION * REV_SQUARED_PER_TICK

BAUDRATE                    = 57600

# DYNAMIXEL Protocol Version (1.0 / 2.0)
# https://emanual.robotis.com/docs/en/dxl/protocol2/
PROTOCOL_VERSION            = 2.0

# Use the actual port assigned to the U2D2.
# ex) Windows: "COM*", Linux: "/dev/ttyUSB*", Mac: "/dev/tty.usbserial-*"
DEVICENAME                  = '/dev/ttyUSB0'

TORQUE_ENABLE               = 1     # Value for enabling the torque
TORQUE_DISABLE              = 0     # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD = 20    # Dynamixel moving status threshold

# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

OpModes = {v: k for k, v in invOpModes.items()}

class DynamixelCommunicationError(Exception):
    pass
class DynamixelModeError(Exception):
    pass
class DynamizelInputRangeError(Exception):
    pass    

class dynamixel(object): 
    def __init__(self, ID, op = 3):
        self.ID = ID
        self.set_mode(op)
   
    def get_id(self):
        return self.ID 

    # Exception Handlers
    def __comm_check(self, dxl_comm_result, dxl_error) -> None:
        if dxl_comm_result != COMM_SUCCESS:
            error_msg = "Dynamixel communication failed: %s" % packetHandler.getTxRxResult(dxl_comm_result)
            raise DynamixelCommunicationError(error_msg)

        elif dxl_error != 0:
            error_msg = "Dynamixel received an error packet: %s" % packetHandler.getRxPacketError(dxl_error)
            raise DynamixelCommunicationError(error_msg)
        
    def __mode_check(self, modes = [0, 1, 3, 4, 5, 16]):
        modeIsValid = False
        for m in modes:
            if self.OperatingMode == m:
                modeIsValid = True
        if not modeIsValid:
            error_msg = "DynamixelModeError: Dynamixel assigned invalid mode: %i" % self.OperatingMode
            raise DynamixelModeError(error_msg)

    # Operating Mode Changing
    def set_mode(self, mode):
        if isinstance(mode, str):
            self.OperatingMode = OpModes[mode]
        elif isinstance(mode, int):
            self.OperatingMode = mode
        self.__update_mode()
    def __update_mode(self): 
        try:
            self.__mode_check()
            wasEnabled = self.get_enabled()
            self.set_enable(False)
            # print("Operating Mode: ", self.get_operating_mode())        
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, self.ID, ADDR_OPERATING_MODE, self.OperatingMode)
            self.__comm_check(dxl_comm_result, dxl_error)
            self.set_enable(wasEnabled)
            # print("OperatingMode is now", invOpModes[self.OperatingMode])
        except DynamixelCommunicationError as e:
            pass
        except DynamixelModeError as e:
            print("DynamixelModeError: __update_mode() tried to update to invalid mode ", self.OperatingMode)
    def get_mode(self, asString = True):
        try:
            mode, dxl_comm_result, dxl_error=packetHandler.read1ByteTxRx(portHandler, self.ID, ADDR_OPERATING_MODE)
            self.__comm_check(dxl_comm_result, dxl_error)
            # print("Mode:",(invOpModes[mode]))
            if True:
                return invOpModes[mode]
            else:
                return mode
        except DynamixelCommunicationError as e:
            pass
    
    # Torque Enable & Disable
    def set_enable(self, doEnable):
        try:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, self.ID, ADDR_TORQUE_ENABLE, doEnable)
            self.__comm_check(dxl_comm_result, dxl_error)
        except DynamixelCommunicationError as e:
            pass
    def get_enabled(self):
        try: 
            enabled, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, self.ID, ADDR_TORQUE_ENABLE)
            self.__comm_check(dxl_comm_result, dxl_error)
            return bool(enabled)
        except DynamixelCommunicationError as e:
            pass

    # Set Acceleration Profiles # Tick or Revolutions / min^2
    def __profile_acceleration_range_check(self, acceleration_profile_to_check):
        if (acceleration_profile_to_check < MINIMUM_PROFILE_ACCELERATION) or acceleration_profile_to_check > MAXIMUM_PROFILE_ACCELERATION:
            error_msg = "DynamizelInputRangeError: Dynamixel {} acceleration_profile input invalid, {} not between {} and {}".format(self.ID, acceleration_profile_to_check, MINIMUM_PROFILE_ACCELERATION, MAXIMUM_PROFILE_ACCELERATION) 
            print(error_msg)
            raise DynamizelInputRangeError(error_msg)  
    def set_profile_acceleration(self, rpm_pm, inTicks = False):
        try:
            if not inTicks:
                dxl_profile_acceleration = round(rpm_pm / REV_SQUARED_PER_TICK)
            else: 
                dxl_profile_acceleration = rpm_pm
            self.__profile_acceleration_range_check(dxl_profile_acceleration)
            dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, self.ID, ADDR_PROFILE_ACCELERATION, dxl_profile_acceleration)
            self.__comm_check(dxl_comm_result, dxl_error)
        except DynamizelInputRangeError as e:
            pass
        except DynamixelCommunicationError as e:
            pass    
    def get_profile_acceleration(self, inTicks = False):
        try:
            dxl_profile_acceleration, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, self.ID, ADDR_PROFILE_ACCELERATION)
            if not inTicks:
                return round(dxl_profile_acceleration * REV_SQUARED_PER_TICK,2)
            else:
                return dxl_profile_acceleration
        except DynamixelCommunicationError as e:
            pass

    # Set Velocity Profile # Tick or rpm  
    def __profile_velocity_range_check(self, velocity_profile_to_check):
        if (velocity_profile_to_check < MINIMUM_PROFILE_VELOCITY) or velocity_profile_to_check > MAXIMUM_PROFILE_VELOCITY:
            error_msg = "DynamizelInputRangeError: Dynamixel {} velocity_profile input invalid, {} not between {} and {}".format(self.ID, velocity_profile_to_check, MINIMUM_PROFILE_VELOCITY, MAXIMUM_PROFILE_VELOCITY) 
            print(error_msg)
            raise DynamizelInputRangeError(error_msg)
    def set_profile_velocity(self, rpm, inTicks = False):
        try:
            if not inTicks:
                dxl_profile_velocity = round(rpm / RPM_PER_TICK)
            else: 
                dxl_profile_velocity = rpm
            self.__profile_velocity_range_check(dxl_profile_velocity)
            dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, self.ID, ADDR_PROFILE_VELOCITY, dxl_profile_velocity)
            self.__comm_check(dxl_comm_result, dxl_error)
        except DynamizelInputRangeError as e:
            pass
        except DynamixelCommunicationError as e:
            pass
    def get_profile_velocity(self, inTicks = False):
        try:
            dxl_profile_velocity, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, self.ID, ADDR_PROFILE_VELOCITY)
            if not inTicks:
                return round(dxl_profile_velocity * RPM_PER_TICK,2)
            else:
                return dxl_profile_velocity
        except DynamixelCommunicationError as e:
            pass

    # 0 : Current Control Mode   
    def __current_range_check(self, current_to_check):
        if (current_to_check < MINIMUM_CURRENT_VALUE) or current_to_check > MAXIMUM_CURRENT_VALUE:
            error_msg = "DynamizelInputRangeError: Dynamixel current input invalid, {} not between {} and {}".format(current_to_check, MINIMUM_CURRENT_VALUE, MAXIMUM_CURRENT_VALUE) 
            raise DynamizelInputRangeError(error_msg)    
    def set_current(self, goal_current, inTick = False, doModeCheck = True):
        try:
            if doModeCheck:
                self.__mode_check([0])
            if not inTick:
                dxl_goal_current = round(goal_current / MILLI_AMP_PER_TICK)
                # print("dxl_goal_current : ", dxl_goal_current)
            else:
                dxl_goal_current = goal_current
            self.__current_range_check(dxl_goal_current)
            dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, self.ID, ADDR_GOAL_CURRENT, dxl_goal_current)
            self.__comm_check(dxl_comm_result, dxl_error)
        except DynamixelModeError as e:
            print("DynamixelModeError: set_current() motor {} ID in mode {}".format(self.ID, self.get_mode()))
        except DynamizelInputRangeError as e:
            print("DynamizelInputRangeError: Dynamixel current input invalid, {} not between {} and {}".format(dxl_goal_current, MINIMUM_CURRENT_VALUE, MAXIMUM_CURRENT_VALUE))
        except DynamixelCommunicationError as e:
            pass      
    def get_current(self, inTick = False):
        try:
            dxl_present_current, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, self.ID, ADDR_PRESENT_CURRENT)
            self.__comm_check(dxl_comm_result, dxl_error)
            # print("[ID:%03d] PresCur:%03d" % (self.ID, dxl_present_current))
            if not inTick:
                tickRange = int("FFFF", 16)
                if not dxl_present_current > tickRange / 2:
                    # Positive PWM
                    return round(dxl_present_current * MILLI_AMP_PER_TICK, 2)
                else:
                    # Negative PWM
                    return round(-(tickRange - dxl_present_current) * MILLI_AMP_PER_TICK, 2)
            else:
                return dxl_present_current
        except DynamixelCommunicationError as e:
            pass

    # 1 : Velocity Control Mode     
    def __velocity__range_check(self, velocity_to_check):
        if (velocity_to_check < MINIMUM_VELOCITY_VALUE) or velocity_to_check > MAXIMUM_VELOCITY_VALUE:
            error_msg = "DynamizelInputRangeError: Dynamixel velocity input invalid, {} not between {} and {}".format(velocity_to_check, MINIMUM_VELOCITY_VALUE, MAXIMUM_VELOCITY_VALUE) 
            raise DynamizelInputRangeError(error_msg)        
    def set_velocity(self, goal_velocity, inTicks = False):
        try:
            self.__mode_check([1])
            if not inTicks:
                dxl_goal_velocity = round(goal_velocity / RPM_PER_TICK)
            else:
                dxl_goal_velocity = goal_velocity
            self.__velocity__range_check(dxl_goal_velocity)
            dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, self.ID, ADDR_GOAL_VELOCITY, dxl_goal_velocity)
            self.__comm_check(dxl_comm_result, dxl_error)
        except DynamixelModeError as e:
            print("DynamixelModeError: set_velocity() motor {} ID in mode {}".format(self.ID, self.get_mode()))
        except DynamizelInputRangeError as e:
            print("Position must be in the range of ", MINIMUM_VELOCITY_VALUE, "-", MAXIMUM_VELOCITY_VALUE, " not ", dxl_goal_velocity)
        except DynamixelCommunicationError as e:
            pass      
    def get_velocity(self, inTicks = False):
        try:
            dxl_present_velocity, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, self.ID, ADDR_PRESENT_VELOCITY)
            self.__comm_check(dxl_comm_result, dxl_error)
            # print("[ID:%03d] PresVel:%03d" % (self.ID, dxl_present_velocity))
            if not inTicks:
                if not dxl_present_velocity > FOUR_BYTE / 2:
                    return round(dxl_present_velocity * RPM_PER_TICK, 2)
                else:
                    return round(-(FOUR_BYTE - dxl_present_velocity) * RPM_PER_TICK, 2)
            else:
                return dxl_present_velocity
        except DynamixelCommunicationError as e:
            pass

    # 3 :  Position Control Mode
    def __position_range_check(self, ticks):
        if (ticks < MINIMUM_POSITION_VALUE) or ticks > MAXIMUM_POSITION_VALUE:
            error_msg = "DynamizelInputRangeError: Dynamixel current input invalid, {} not between {} and {}".format(ticks, MINIMUM_POSITION_VALUE, MAXIMUM_POSITION_VALUE) 
            raise DynamizelInputRangeError(error_msg)
    def set_position(self, goal_position, inTicks = False):
        # need to implement current position control and extended poisition control
        try:
            self.__mode_check([3])
            if not inTicks:
                dxl_goal_position = round(goal_position * TICK_PER_DEGREE)
            else:
                dxl_goal_position = goal_position
            self.__position_range_check(dxl_goal_position)
            dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, self.ID, ADDR_GOAL_POSITION, dxl_goal_position)
            self.__comm_check(dxl_comm_result, dxl_error)
        except DynamixelCommunicationError as e:
            pass
        except DynamixelModeError as e:
            print("DynamixelModeError: Dynamixel not in position mode, [PresMode:%01d]" % self.OperatingMode)
        except DynamizelInputRangeError as e:
            print("DynamizelInputRangeError: Position out of range requested, dxl_goal_position: ", dxl_goal_position) 
    def get_position(self, inTick = False):
        try:
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, self.ID, ADDR_PRESENT_POSITION)
            self.__comm_check(dxl_comm_result, dxl_error)
            # print("[ID:%03d] PresPos:%03d" % (self.ID, dxl_present_position))
            if not inTick:
                return round((dxl_present_position % 4096) / TICK_PER_DEGREE, 2)
            else:
                return dxl_present_position % 4096
        except DynamixelCommunicationError as e:
            pass

    # 4: Extended Position Control Mode
    def set_extended_position(self, goal_position, inTicks = False, doModeCheck = True):
        try:
            if doModeCheck:
                self.__mode_check([4])
            if not inTicks:
                dxl_goal_position = round(goal_position * TICK_PER_DEGREE)
            else:
                dxl_goal_position = goal_position
            # self.__extended_position_range_check(dxl_goal_position)
            dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, self.ID, ADDR_GOAL_POSITION, dxl_goal_position)
            self.__comm_check(dxl_comm_result, dxl_error)
        except DynamixelModeError as e:
            print("DynamixelModeError: Dynamixel not in position mode, [PresMode:%01d]" % self.OperatingMode)
        except DynamixelCommunicationError as e:
            print("DynamixelCommunicationError : Motor ID {} , set_extended_position ".format(self.ID))
        except DynamizelInputRangeError as e:
            print("DynamizelInputRangeError: Position out of range requested, dxl_goal_position: ", dxl_goal_position) 
    def get_extended_position(self, inTick = False):
        try:
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, self.ID, ADDR_PRESENT_POSITION)
            self.__comm_check(dxl_comm_result, dxl_error)
            # print("[ID:%03d] PresPos:%03d" % (self.ID, dxl_present_position))
            if not inTick:
                if not dxl_present_position > FOUR_BYTE / 2:
                    # Positive PWM
                    return round(dxl_present_position / TICK_PER_DEGREE, 2)
                else:
                    # Negative PWM
                    return round(-(FOUR_BYTE - dxl_present_position) / TICK_PER_DEGREE, 2)
            else:
                return dxl_present_position
        except DynamixelCommunicationError as e:
            print("DynamixelCommunicationError : Motor ID {} , get_extended_position ".format(self.ID))
    
    # 5: Current-based Positiion Control Mode
    def set_position_current(self, goal_position, goal_current, inTick = False):
        try:
            self.__mode_check([5])
            self.set_current(goal_current, inTick, doModeCheck = False)
            self.set_extended_position(goal_position, inTick, doModeCheck = False)
        except DynamixelModeError as e:
            print("DynamixelModeError: Dynamixel not in Current-based_Position mode, [PresMode:%01d]" % self.OperatingMode)
        except DynamixelCommunicationError as e:
            print("DynamixelCommunicationError : Motor ID {} , set_position_and_current ".format(self.ID))

    # 16: PWM Control Mode (Voltage Control Mode)   
    def __pwm_range_check(self, value):
        if (value < MINIMUM_PWM_VALUE) or value > MAXIMUM_PWM_VALUE:
            error_msg = "DynamizelInputRangeError: Dynamixel PWM input invalid, {} not between {} and {}".format(value, MINIMUM_PWM_VALUE, MAXIMUM_PWM_VALUE) 
            raise DynamizelInputRangeError(error_msg) 
    def set_pwm(self, goal_PWM, inTick = False):
        try:
            self.__mode_check([16])
            if not inTick:
                dxl_goal_PWM = round(goal_PWM / PWM_PER_TICK)
                print(dxl_goal_PWM)
            else:
                dxl_goal_PWM = goal_PWM
            self.__pwm_range_check(dxl_goal_PWM)
            dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, self.ID, ADDR_GOAL_PWM, dxl_goal_PWM)
            self.__comm_check(dxl_comm_result, dxl_error)  
        except DynamixelModeError as e:
            print("Motor must be in one of these OperatingModes:",invOpModes[16])
        except DynamizelInputRangeError as e:
            print("Position must be in the range of ", MINIMUM_PWM_VALUE, "-", MAXIMUM_PWM_VALUE)
        except DynamixelCommunicationError as e:
            pass   
    def get_pwm(self, inTick = False):
        try:
            dxl_present_PWM, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, self.ID, ADDR_PRESENT_PWM)
            self.__comm_check(dxl_comm_result, dxl_error) 
            # print("[ID:%03d] PresPMW:%03d" % (self.ID, dxl_present_PWM))
            if not inTick:
                if not dxl_present_PWM > TWO_BYTE / 2:
                    # Positive PWM
                    return round(dxl_present_PWM * PWM_PER_TICK, 2)
                else:
                    # Negative PWM
                    return round(-(TWO_BYTE - dxl_present_PWM) * PWM_PER_TICK, 2)
            else:
                return dxl_present_PWM
        except DynamixelCommunicationError as e:
            pass

    # Temperature  
    def get_temp(self):
        try:
            dxl_present_temp, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, self.ID, ADDR_PRESENT_TEMPERATURE)
            self.__comm_check(dxl_comm_result, dxl_error) 
            # print("[ID:%03d] PresPMW:%03d" % (self.ID, dxl_present_PWM))
            return round(dxl_present_temp, 2)
        except DynamixelCommunicationError as e:
            pass

    # Misc 
    def print(self):
        a = self.get_current()
        b = self.get_velocity()
        c = self.get_position()
        d = self.get_extended_position()
        e = self.get_pwm()
        f = self.get_id()
        g = self.get_mode()
        h = self.get_temp()
        
        print("ID           ", f )
        print("Mode:        ", g)
        print("Current:     ", a, " milliAmps")
        print("Velocity:    ", b, " rpm")
        print("Postion:     ", c, " degrees")
        print("Extended:    ", d, " degrees")
        print("PWM:         ", e, " %")
        print("Temperature  ", h, " C")
        print()

if __name__  == '__main__':
    id_to_test = 1
    test_op = 1
    if test_op == 0:  # 0      # Test Current
        motor3 = dynamixel(ID = id_to_test, op = 0)
        # motor3.set_profile_acceleration(rpm_pm=50)
        motor3.set_enable(True)
        val = 50
        
        while True:
            motor3.set_current(val)
            val *= -1
            time.sleep(.1)
            print()
            motor3.print()
            time.sleep(2)
   
    if test_op == 1:  # 1      # Test Velocity
        motor3 = dynamixel(ID = id_to_test, op = "Velocity")
        # motor3.set_profile_acceleration(rpm_pm=50)
        motor3.set_profile_velocity(rpm=120)
        motor3.set_enable(True)
        motor3.set_velocity(goal_velocity = -300)
        val = 50
        while True:
            print(motor3.get_current())
            # val *= -1
            # time.sleep(.1)
            # motor3.print()
            # time.sleep(2)  
                      
    if test_op == 3:  # 3      # Test Position
        motor3 = dynamixel(ID = id_to_test, op = "Position")
        motor3.set_profile_acceleration(rpm_pm=5000)
        print("profile acceleration is ", motor3.get_profile_acceleration(), " rpmpm")
        motor3.set_profile_velocity(rpm=40, inTicks=False)
        print("profile velocity is ", motor3.get_profile_velocity(), " rpm")
        motor3.set_enable(True)
        print("Motor ", motor3.get_id(), " enabled state is ", motor3.get_enabled())
        val = 90
        while True:
            motor3.set_position(goal_position = 135 + val)
            time.sleep(.2)
            val *= -1
            motor3.print()
            time.sleep(1)        
   
    if test_op == 4:  # 4      # Test Extended Position
        motor3 = dynamixel(ID = id_to_test, op = "Extended_Position")
        motor3.set_profile_acceleration(rpm_pm=20000)
        print("profile acceleration is ", motor3.get_profile_acceleration(), " rpmpm")
        motor3.set_profile_velocity(rpm=400, inTicks=False)
        print("profile velocity is ", motor3.get_profile_velocity(), " rpm")
        motor3.set_enable(True)
        print("Motor ", motor3.get_id(), " enabled state is ", motor3.get_enabled())
        goTo = 360
        while True:
            motor3.set_extended_position(goal_position = goTo)
            goTo *= -1
            motor3.print()
            time.sleep(3)
   
    if test_op == 5:  # 5      # Test Extended Position Current
        motor3 = dynamixel(ID = id_to_test, op = 5)
        motor3.set_profile_acceleration(rpm_pm=2000)
        motor3.set_enable(True)
        print("Motor ", motor3.get_id(), " enabled state is ", motor3.get_enabled())
        val = 180
        while True:
            motor3.set_position_current(goal_position = val + 180, goal_current = 150)
            print("Motor Velocity:  ", motor3.get_velocity(), " rpm")
            val *= -1
            print()
            wait = 3
            hz = 10
            for i in range(wait * hz):
                motor3.print()
                time.sleep(1/hz)
   
    if test_op == 16:  # 16     # Test PWM
        motor3 = dynamixel(ID = id_to_test, op = "PWM")
        # motor3.set_profile_acceleration(rpm_pm=50)
        motor3.set_enable(True)
        val = 10
        while True:
            motor3.set_pwm(val)
            val *= -1
            time.sleep(.1)
            motor3.print()
            time.sleep(2)