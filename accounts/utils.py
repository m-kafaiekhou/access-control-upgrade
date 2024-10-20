import serial.tools.list_ports


def find_usb_port(port_description):
    # List all available COM ports
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        # Check if the desired description is in the port's description
        if port_description in port.description:
            return port.device  # Return the COM port (e.g., 'COM3')
    
    return 'COM8'
