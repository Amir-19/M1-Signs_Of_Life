from lib_robotis_hack import *
from dynamic_plotter import *
#from dynamic_plotter import *

# At this point, check your /dev/ directory for the location of the USB to Serial device; if in doubt, unplug the USB2Dynamixel, look at the /dev/ directory, then plug it back in and see which device has been added.

# For example, the upper right USB port on my computer gives the device: tty.usbserial-AI03QDFW, while the the bottom left gives /dev/tty.usbserial-AI0282TZ

# Create the USB to Serial channel
# Use the device you identified above, and baud of 1Mbps
D = USB2Dynamixel_Device(dev_name="/dev/tty.usbserial-AI03QD8V",baudrate=1000000)

s1 = Robotis_Servo(D,2)
s2 = Robotis_Servo(D,3)
#d = DynamicPlot(window_x = 30, title = 'Trigonometry', xlabel = 'X', ylabel= 'Y')
s1.disable_torque()

plotting = True
if plotting:

    d = DynamicPlot(window_x = 30, title = 'servo 1 sensorimotor data stream', xlabel = 'time_step', ylabel= 'value')
    d2 = DynamicPlot(window_x = 30, title = 'servo 2 sensorimotor data stream', xlabel = 'time_step', ylabel= 'value')
    d.add_line('s1 voltage')
    d.add_line('s1 load')
    d.add_line('s1 angle * 100')
    d.add_line('s1 temp')

    d2.add_line('s2 voltage')
    d2.add_line('s2 load')
    d2.add_line('s2 angle * 100')
    d2.add_line('s2 temp')


i=0
while (True):
    temp = s1.read_angle()
  #if not s2.is_moving():
    s2.move_angle(temp,angvel=None, blocking=False)
    if plotting:
        #d.update(i, [100*s1.read_angle(), 100*s1.read_angle(), 100*s1.read_angle(),100*s1.read_angle()])
        #d2.update(i, [100*s2.read_angle(), 100*s2.read_angle(), 100*s2.read_angle(),100*s2.read_angle()])

        read_all = [0x02, 0x24, 0x08]
        data = s1.send_instruction(read_all, s1.servo_id)
        position = sum(data[:2]) / 2.0
        speed = sum(data[2:4]) / 2.0
        load = sum(data[4:6]) / 2.0
        voltage = data[6]
        temperature = data[7]
        # print data[:2]
        # print s1.read_encoder()
        ang = (data[1]*256 +data[0] - 0x200) * math.radians(300.0) / 1024.0
        d.update(i, [voltage, load, ang*100,temperature])

        data = s2.send_instruction(read_all, s2.servo_id)
        position = sum(data[:2]) / 2.0
        speed = sum(data[2:4]) / 2.0
        load = sum(data[4:6]) / 2.0
        voltage = data[6]
        temperature = data[7]
        ang = (data[1]*256 +data[0] - 0x200) * math.radians(300.0) / 1024.0
        d2.update(i, [voltage, load, ang*100,temperature])
    i += 1
# s2.move_angle(1.0,angvel=None, blocking=False)