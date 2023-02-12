"""!
@file motor_task.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and a queue. The tasks don't really @b do
    anything; the example just shows how these elements are created and run.

@author Peyton Archibald
@author Harrison Hirsch
@date   2021-Dec-15 JRR Created from the remains of previous example

"""

#import gc
import pyb
import cotask
import task_share
import encoder_reader
import motor_controller
import motor_driver



class MotorTask:
    """!
    @brief                      A class for
    @details                    This is a class that implements
    """

    def __init__(self, motor_enable_pin_str, motor_in1_pin, motor_in2_pin, motor_timer, encoder_pinA, encoder_pinB, encoder_timer):
        """!
            @brief                      Constructs a controller object
            @details                    Upon instantiation, the controller object has a defined proportional gain and
                                        initial setpoint. It notifies the user that a motor controller is being created
            @param  initial_Kp          The proportional gain to be used
            @param  initial_set_point   The initial setpoint to aim for
        """

        self.motor = motor_driver.MotorDriver(motor_enable_pin_str, motor_in1_pin, motor_in2_pin, motor_timer)
        self.encoder = encoder_reader.EncoderReader(encoder_pinA, encoder_pinB, encoder_timer)
        self.controller = motor_controller.MotorController(0.01, 0)
        print("Creating a motor motor-encoder object")


# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":