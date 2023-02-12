import pyb                  # Turn off the REPL on UART2
pyb.repl_uart(None)
pyb.main(basic_task.py)