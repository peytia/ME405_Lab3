import time
import serial
import matplotlib.pyplot as plt

"""!
    @file                       CPython_serial_readandplot.py
    @brief                      Reads and plots data from a serial port
    @details                    This file is to be run on a computer that is reading data from a serial port. The
                                incoming data will be read, formatted, and plotted.

    @author                     Peyton Archibald
    @author                     Harrison Hirsch
    @date                       February 7, 2023
"""


def main():
    """!
        @brief                  Method that plots incoming data from a serial port
        @details                This file waits for data coming into a serial port, then reads, formats, and plots the
                                data.
    """
    with(serial.Serial('COM4', 115200) as ser):     # Set up serial port
        ser.flush()
        plt.close()         # Close any existing figures
        data_list_x = []    # Allocate memory for x values
        data_list_y = []    # Allocate memory for y values
        try:
            while True:
                if ser.inWaiting() > 0:     # Once data is read
                    data = ser.readline().strip(b'\r\n').split(b', ')   # Format incoming data
                    data_list_x.append(int(data[0]))      # Append x values to x list
                    data_list_y.append(int(data[1]))      # Append y values to y list
                    if data_list_x[len(data_list_x)-1] >= 6000:         # Once data is finished (change this to length of step response)
                        break                               # Break out of loop to plot
                else:
                    time.sleep(0.01)
        except (ValueError, IndexError) as e:       # Corrupted data handling
            print(e)
    # print('checkpoint')     # For debugging
    plt.plot(data_list_x, data_list_y, 'r-')        # Plot x and y data
    plt.xlabel('Time [ms]')                         # Label x axis
    plt.ylabel('Position [encoder counts]')         # Label y axis
    # Label steady state value
    plt.annotate(f'{int(data_list_y[len(data_list_y)-1])} Counts', xy=(data_list_x[len(data_list_x)-1]-1500, data_list_y[len(data_list_y)-1]-5000))
    plt.show()


if __name__ == '__main__':
    main()
        