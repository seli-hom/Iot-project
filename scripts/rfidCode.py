import serial

# Connect to the reader
try:
    ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.1)
    print("Successfully connected to RFID Reader on /dev/ttyUSB0")
except:
    print("Error: Could not find reader. Check your USB connection.")
    exit()

buffer = bytearray()

while True:
    data = ser.read(ser.in_waiting or 1)
    if data:
        buffer.extend(data)

        while len(buffer) >= 26:
            # Search for your specific header 00 CF
            idx = buffer.find(b'\x00\xCF')

            if idx == -1:
                # No header found, clear buffer to save memory
                buffer.clear()
                break
            
            # If header is found but we don't have the full 26-byte packet yet
            if len(buffer) < idx + 26:
                break

            # Extract the packet
            packet = buffer[idx : idx + 26]

            # --- THE FIX: RELATIVE OFFSETS ---
            # Based on your last '49' output, the EPC starts at byte 11
            # We take 12 bytes for a standard 96-bit EPC
            epc_raw = packet[12:24]
            epc_hex = epc_raw.hex().upper()

            # RSSI is usually stored at byte 8 in this protocol
            rssi = packet[8] - 256

            print(f"Tag ID: {epc_hex} | RSSI: {rssi}dBm")

            # Slide the buffer forward
            del buffer[: idx + 26]