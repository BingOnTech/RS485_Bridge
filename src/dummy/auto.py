from serial.rs485 import RS485
import serial

ser = RS485(port="/dev/ttyUSB0", baudrate=9600, timeout=1)
ser.rs485_mode = serial.rs485.RS485Settings(delay_before_tx=0, delay_before_rx=0)
