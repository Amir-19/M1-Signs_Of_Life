# simple policy for Robot Module 1
# author: amir samani
# code to "read all data" for plotting and saving at once was based on the code shared by niko on slacks ;)

from lib_robotis_hack import *
from dynamic_plotter import *
import thread
import time
import numpy as np
import signal


# we could have only one function for this but if we want different bhv we need to have different controllers
# servo (with id 2) controller

servo1_data = None
servo2_data = None
flag_stop = False
def servo1_policy( threadName, D):
    global  flag_stop
    servo = Robotis_Servo(D,2)

    ang_to_go = 0.0
    dir = 1
    while (True):
        servo.move_angle(ang_to_go,angvel=None, blocking=False)
        ang_to_go += dir * 0.1
        if ang_to_go >= 1.0 or ang_to_go <= -1.0:
            dir *= -1
        time.sleep(0.05)
        if flag_stop:
            thread.exit_thread()

# servo (with id 2) controller
def servo2_policy( threadName, D):
    global  flag_stop
    servo = Robotis_Servo(D,3)
    ang_to_go = 0.0
    dir = 1
    while (True):
        servo.move_angle(ang_to_go,angvel=None, blocking=False)
        ang_to_go += dir * 0.1
        if ang_to_go >= 1.0 or ang_to_go <= -1.0:
            dir *= -1
        time.sleep(0.05)
        if flag_stop:
            thread.exit_thread()

def main():

    global servo1_data, servo2_data, flag_stop
    servo1_data = []
    servo2_data = []
    D = USB2Dynamixel_Device(dev_name="/dev/tty.usbserial-AI03QD8V",baudrate=1000000)
    s1 = Robotis_Servo(D,2)
    s2 = Robotis_Servo(D,3)
    try:
       thread.start_new_thread( servo1_policy, ("Servo2 Controller", D, ) )
       thread.start_new_thread( servo2_policy, ("Servo3 Controller", D, ) )
    except:
       print "Error: unable to start thread"

    d1 = DynamicPlot(window_x = 100, title = 'sensorimotor datastream servo 1', xlabel = 'time_step', ylabel= 'value')
    d2 = DynamicPlot(window_x = 100, title = 'sensorimotor datastream servo 2', xlabel = 'time_step', ylabel= 'value')

    d1.add_line('s1 Voltage')
    d1.add_line('s1 Load')
    d1.add_line('s1 Angle * 100')
    d1.add_line('s1 Temp')

    d2.add_line('s2 Voltage')
    d2.add_line('s2 Load')
    d2.add_line('s2 Angle * 100')
    d2.add_line('s2 Temp')

    i = 0
    while True:

        #reading data for servo 1
        read_all = [0x02, 0x24, 0x08]
        data = s1.send_instruction(read_all, s1.servo_id)
        voltage = data[6] / 10.0
        temperature = data[7]
        load = sum(data[4:6]) / 2.0

        # calculate the angle for servo 1
        ang = (data[1]*256 +data[0] - 0x200) * math.radians(300.0) / 1024.0

        # update the plot for servo 1
        d1.update(i, [voltage, load, ang*100,temperature])
        servo1_data.append([i, voltage, load, ang*100,temperature])

        #reading data for servo 2
        data = s2.send_instruction(read_all, s2.servo_id)
        load = sum(data[4:6]) / 2.0
        voltage = data[6] / 10.0
        temperature = data[7]

        # calculate the angle for servo 2
        ang = (data[1]*256 +data[0] - 0x200) * math.radians(300.0) / 1024.0

        # update the plot for servo 2
        d2.update(i, [voltage, load, ang*100,temperature])
        servo2_data.append([i, voltage, load, ang*100,temperature])
        # go to the next time step
        i += 1
        if flag_stop:
            thread.exit_thread()


#write plotting data to file before ending by ctrl+c
def signal_handler(signal, frame):

    global flag_stop, servo1_data,servo2_data

    #stop threads
    flag_stop = True

    # now we need to dump the sensorimotor datastream to disk
    np_servo1_data = np.asarray(servo1_data)
    np_servo2_data = np.asarray(servo2_data)

    np.savetxt('servo1_ds_dump.txt',np_servo1_data)
    np.savetxt('servo2_ds_dump.txt',np_servo2_data)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()