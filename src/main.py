"""!
    @file main.py
        This file contains a program that runs some tasks, and some
        inter-task communication variables. The tasks set up two separate
        motors, run each of them through a different step response, and
        outputs the results to a serial port.

    @author JR Ridgely
    @date   February 14, 2023; JRR Created from the remains of previous example
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


# def task1_fun(shares):
#     """!
#         @brief 				Updates the motor-encoder object
#         @details			This method reads the current encoder position and uses the controller to set the desired
#                             duty cycle
#         @param shares   A list holding the shares used by this task
#     """
#     # Get references to the share and queue which have been passed to this task
#     my_share, my_queue = shares
#
#     counter = 0
#     while True:
#         my_share.put(counter)
#         my_queue.put(counter)
#         counter += 1
#
#         yield 0
#
#
# def task2_fun(shares):
#     """!
#     Task which takes things out of a queue and share and displays them.
#     @param shares A tuple of a share and queue from which this task gets data
#     """
#     # Get references to the share and queue which have been passed to this task
#     the_share, the_queue = shares
#
#     while True:
#         # Show everything currently in the queue and the value in the share
#         print(f"Share: {the_share.get ()}, Queue: ", end='')
#         while q0.any():
#             print(f"{the_queue.get ()} ", end='')
#         print('')
#
#         yield 0


def task1_motor(shares):
    """!
        @brief 				Task that sets up and runs motor 1
        @details			This task sets up motor 1 on its first call, and runs it on every other call by setting the
                            controller setpoint, updating the motor, and adding the position the appropriate share
        @param shares       A list holding the shares used by all tasks
    """
    motor1 = motor_task.MotorTask(shares, 'A10', 'B4', 'B5', 3, 'C6', 'C7', 8, 0.1)
    setpoint_share, setpoint_share2, motor1position, motor2position = shares
    yield 0
    while True:
        motor1.set_setpoint(setpoint_share.get())
        motor1.update()
        motor1position.put(motor1.get_position()[0])
        yield 0


def task3_motor(shares):
    """!
        @brief 				Task that sets up and runs motor 2
        @details			This task sets up motor 2 on its first call, and runs it on every other call by setting the
                            controller setpoint, updating the motor, and adding the position the appropriate share
        @param shares       A list holding the shares used by all tasks
    """
    motor2 = motor_task.MotorTask(shares, 'C1', 'A0', 'A1', 5, 'B6', 'B7', 4, 0.1)
    setpoint_share, setpoint_share2, motor1position, motor2position = shares
    yield 0
    while True:
        motor2.set_setpoint(setpoint_share2.get())
        motor2.update()
        motor2position.put(motor2.get_position()[0])
        yield 0


def task2_step(shares):
    """!
        @brief 				Task that runs and stores data from a step response
        @details			This task sets creates both setpoints, runs a step response, and outputs the data to a
                            serial port
        @param shares       A list holding the shares used by all tasks
    """
    u2 = pyb.UART(2, baudrate=115200)  # Set up the second USB-serial port
    currTime = 0  # Allocate memory for current time
    storedData = []  # Allocate memory for stored data
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
    for dataPt in storedData:  # Write stored data to serial port
        u2.write(f'{dataPt[0]}, {dataPt[1]}\r\n')


if __name__ == "__main__":

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

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break
    print('Done')
