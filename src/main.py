"""!
@file main.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and a queue. The tasks don't really @b do
    anything; the example just shows how these elements are created and run.

@author JR Ridgely
@date   2021-Dec-15 JRR Created from the remains of previous example
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2. 
"""

import gc
import pyb
import cotask
import task_share
import motor_task
import utime
import array


def task1_fun(shares):
    """!
    Task which puts things into a share and a queue.
    @param shares A list holding the share and queue used by this task
    """
    # Get references to the share and queue which have been passed to this task
    my_share, my_queue = shares

    counter = 0
    while True:
        my_share.put(counter)
        my_queue.put(counter)
        counter += 1

        yield 0


def task2_fun(shares):
    """!
    Task which takes things out of a queue and share and displays them.
    @param shares A tuple of a share and queue from which this task gets data
    """
    # Get references to the share and queue which have been passed to this task
    the_share, the_queue = shares

    while True:
        # Show everything currently in the queue and the value in the share
        print(f"Share: {the_share.get ()}, Queue: ", end='')
        while q0.any():
            print(f"{the_queue.get ()} ", end='')
        print('')

        yield 0


def task1_motor(shares):
    # Kp_input = input('Enter a Kp: ')  # Prompt user to enter a proportional gain
    # if is_number(Kp_input):  # Test for valid input
    #     Kp_input = float(Kp_input)
    # else:
    #     raise ValueError('Input must be a number')
    motor1 = motor_task.MotorTask(shares, 'A10', 'B4', 'B5', 3, 'C6', 'C7', 8, 0.1)
    setpoint_share, setpoint_share2, motor1position, motor2position = shares
    yield 0
    while True:
        motor1.set_setpoint(setpoint_share.get())
        motor1.update()
        motor1position.put(motor1.get_position()[0])
        yield 0


def task3_motor(shares):
    # Kp_input = input('Enter a Kp: ')  # Prompt user to enter a proportional gain
    # if is_number(Kp_input):  # Test for valid input
    #     Kp_input = float(Kp_input)
    # else:
    #     raise ValueError('Input must be a number')
    motor2 = motor_task.MotorTask(shares, 'C1', 'A0', 'A1', 5, 'B6', 'B7', 4, 0.1)
    setpoint_share, setpoint_share2, motor1position, motor2position = shares
    yield 0
    while True:
        motor2.set_setpoint(setpoint_share2.get())
        motor2.update()
        motor2position.put(motor2.get_position()[0])
        yield 0


def task2_step(shares):
    u2 = pyb.UART(2, baudrate=115200)  # Set up the second USB-serial port
    currTime = 0  # Allocate memory for current time
    # initial_val_lst = 100 * [0]  # 1 second before step
    # final_value_lst = 500 * [24000]  # 5 seconds of about 1.5 revolutions
    # step_lst = initial_val_lst + final_value_lst  # Concatenate lists to make step response positions
    storedData = []  # Allocate memory for stored data
    # storedData = array.array('array', [])
    setpoint_share, setpoint_share2, motor1position, motor2position = shares
    setpoint_share.put(24000)
    setpoint_share2.put(16000)
    input('Press Enter to perform a step response')
    startTime = utime.ticks_ms()  # Begin start time counter
    tst_flg = True
    yield 0
    while tst_flg:
        stopTime = utime.ticks_ms()
        currTime = utime.ticks_diff(stopTime, startTime)  # Calculate current time
        storedData.append(array.array('i', [currTime, motor1position.get(), motor2position.get()]))
        print([currTime, motor1position.get(), motor2position.get()])
        if storedData[len(storedData)-1][0] > 6000:
            break
        yield 0
    # for value in step_lst:  # For each position in step response
    #     encoderPosSpeed = encoder1.read()  # Update and read encoder value
    #     controller1.set_setpoint(value)  # Set controller setpoint to current step response value
    #     desiredDuty = controller1.run(encoderPosSpeed[0])  # Run controller to calculate duty cycle
    #     motor1.set_duty_cycle(desiredDuty)  # Set calculated duty cycle
    #     stopTime = utime.ticks_ms()  # Begin stop time counter
    #     currTime = utime.ticks_diff(stopTime, startTime)  # Calculate current time
    #     currPos = encoderPosSpeed[0]  # Current encoder position
    #     controller1.store_data(storedData, currTime, currPos)  # Store motor position in a data list
    #     utime.sleep_ms(10)  # Match rate of execution
    for dataPt in storedData:  # Write stored data to serial port
        u2.write(f'{dataPt[0]}, {dataPt[1]}\r\n')


def is_number(pt):
    """!
        @brief          Helper function to test for valid user input
        @details        This is a helper function to determine if the user input a valid value for Kp. A valid Kp is a
                        floating point number.
        @param  pt      The input to be tested
        @return         A boolean True if the input can be cast to a float, and False otherwise.
    """
    try:
        float(pt)  # Return true if able to cast to a float
        return True
    except ValueError:
        return False  # Return false if not

# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.


if __name__ == "__main__":
    # gen_obj = task1_controller()
    # while True:
    #     next(gen_obj)
    # print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
    #       "Press Ctrl-C to stop and show diagnostics.")

    # Create a share and a queue to test function and diagnostic printouts
    setpoint_share = task_share.Share('h', thread_protect=False, name="setpoint")
    setpoint_share2 = task_share.Share('h', thread_protect=False, name="setpoint")
    motor1_position_share = task_share.Share('q', thread_protect=False, name="motor1position")
    motor2_position_share = task_share.Share('q', thread_protect=False, name="motor2position")

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for
    # debugging and set trace to False when it's not needed
    motor_task1 = cotask.Task(task1_motor, name="Task_1", priority=1, period=20,
                              profile=False, trace=False, shares=(setpoint_share, setpoint_share2, motor1_position_share, motor2_position_share))
    motor_task2 = cotask.Task(task3_motor, name="Task_3", priority=1, period=10,
                              profile=False, trace=False, shares=(setpoint_share, setpoint_share2, motor1_position_share, motor2_position_share))
    stepresponse_task2 = cotask.Task(task2_step, name="Task_2", priority=2, period=60,
                         profile=True, trace=False, shares=(setpoint_share, setpoint_share2, motor1_position_share, motor2_position_share))
    cotask.task_list.append(motor_task1)
    cotask.task_list.append(motor_task2)
    cotask.task_list.append(stepresponse_task2)
    #
    # # Run the memory garbage collector to ensure memory is as defragmented as
    # # possible before the real-time scheduler is started
    gc.collect()
    #
    # # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break
    #
    # # Print a table of task data and a table of shared information data
    # # print('\n' + str(cotask.task_list))
    # # print(task_share.show_all())
    # # print(task1.get_trace())
    print('Done')
