import serial
import time
from models import database as db
from .checkout_service import CheckoutManager

class RFIDService:
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.manager = CheckoutManager(db)

    def perform_basket_scan(self, scan_duration=2.0):
            ser = None # Local variable instead of self.ser
            try:
                # Open port ONLY for the duration of this function
                ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
                buffer = bytearray()
                found_tags = set()
                
                start_time = time.time()
                while time.time() - start_time < scan_duration:
                    if ser.in_waiting > 0:
                        data = ser.read(ser.in_waiting)
                        buffer.extend(data)
                        # ... (keep your existing while len(buffer) >= 26 logic) ...
                
                return list(found_tags)
            except Exception as e:
                print(f"Scan Error: {e}")
                return []
            finally:
                if ser and ser.is_open:
                    ser.close() # Port is now free for the next poll

    def get_checkout_data(self, scan_duration=2.0):
        """
        Combines the physical scan with database lookup.
        This is what your Flask route will call.
        """
        tags = self.perform_basket_scan(scan_duration)
        if not tags:
            return {"error": "No tags detected"}
            
        return self.manager.process_simultaneous_scan(tags)

# This allows you to still test the file by running it directly:
if __name__ == "__main__":
    service = RFIDService()
    input("Press Enter to test a scan...")
    result = service.get_checkout_data()
    print(result)