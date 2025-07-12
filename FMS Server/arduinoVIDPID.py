import serial.tools.list_ports

for port in serial.tools.list_ports.comports():
    if port.vid is not None and port.pid is not None:
        print(f"{port.device} - VID: {hex(port.vid)} PID: {hex(port.pid)}")
    else:
        print(f"{port.device} - No VID/PID")
