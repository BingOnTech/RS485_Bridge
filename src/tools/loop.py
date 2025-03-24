import serial
import serial.rs485

ser = serial.Serial("", baudrate=38400, timeout=1)
ser.rs485_mode = serial.rs485.RS485Settings()

command = ""

if __name__ == "__main__":
    command = "$0110\r"
    command_bytes = command.encode("ASCII")

    while True:
        ser.write(command_bytes)
        sleep(1)
        
    response = ser.readline().decode()
    print(response)
    ser.close()
