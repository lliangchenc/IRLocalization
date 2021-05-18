from pyfirmata import Arduino
import time

board = Arduino('/dev/cu.usbmodem142401')
pin = board.get_pin('a:3:i')
while True:
    print(board.analog[3].read())
    # board.digital[13].write(0)
    # time.sleep(1)
    # board.digital[13].write(1)
    # time.sleep(1)
