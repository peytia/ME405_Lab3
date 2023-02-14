"""!
@file motor_task.py
    This file contains a class that instantiates a motor,
    encoder, and controller with 1 constructor. It also contains
    methods for other basic functionalities related to motors.

@author Peyton Archibald
@author Harrison Hirsch
@date   February 14, 2023

"""

# import gc
import pyb
import cotask
import task_share
import encoder_reader
import motor_controller
import motor_driver


class MotorTask:
    """!
    @brief                      A class for setting up a motor
    @details                    This is a class that takes in several necessary parameters for setting up a motor and
                                creates a driver, encoder, and controller.
    """

    def __init__(self, shares, motor_enable_pin_str, motor_in1_pin, motor_in2_pin, motor_timer, encoder_pinA, encoder_pinB, encoder_timer, Kp):
        """!
            @brief                          Constructs a motor-encoder object
            @details                        Upon instantiation, the motor-encoder object has all pins and timer channels
                                            defined. It notifies the user that a motor-encoder object is being created
            @param  shares                  The variables to be used between tasks
            @param  motor_enable_pin_str    The motor enable pin
            @param  motor_in1_pin           The motor input pin 1
            @param  motor_in2_pin           The motor input pin 2
            @param  motor_timer             The motor timer channel
            @param  encoder_pinA            The encoder pin A
            @param  encoder_pinB            The encoder pin B
            @param  encoder_timer           The encoder timer channel
            @param  Kp                      The proportional gain to be used
        """
        self.setpoint_share, self.setpoint_share2, self.motor1position, self.motor2position = shares
        self.motor = motor_driver.MotorDriver(motor_enable_pin_str, motor_in1_pin, motor_in2_pin, motor_timer)
        self.encoder = encoder_reader.EncoderReader(encoder_pinA, encoder_pinB, encoder_timer)
        self.controller = motor_controller.MotorController(Kp, 0)
        print("Created a motor motor-encoder object")

    def update(self):
        """!
            @brief 				Updates the motor-encoder object
            @details			This method reads the current encoder position and uses the controller to set the desired
                                duty cycle
        """
        self.encoder_position = self.encoder.read()
        # self.controller.set_setpoint(self.setpoint_share.get())
        self.motor_desiredduty = self.controller.run(self.encoder_position[0])
        # print(self.encoder_position[0],self.motor_desiredduty)
        self.motor.set_duty_cycle(self.motor_desiredduty)

    def get_position(self):
        """!
            @brief                  Gets the position of the motor in encoder ticks
            @details                This method calls the "read" method of the encoder
            @return                 Current encoder position
        """
        self.encoder_position = self.encoder.read()
        return self.encoder_position

    def set_setpoint(self, new_setpoint):
        """!
            @brief                      Changes the controller setpoint
            @details                    This method calls the "set_setpoint" method of the controller
            @param  new_setpoint        The new desired controller setpoint
        """
        self.controller.set_setpoint(new_setpoint)
        pass


if __name__ == "__main__":
    pass
