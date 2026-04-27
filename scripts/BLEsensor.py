import asyncio
from bleak import BleakClient
from services import email_service

# Configuration
DEVICE_ADDRESS = "XX:XX:XX:XX:XX:XX"
CHARACTERISTIC_UUID = "your-uuid-here"
CHECK_INTERVAL = 10  # Seconds between reads
latest_value = None

async def read_at_intervals():
    global latest_value
    
    async with BleakClient(DEVICE_ADDRESS) as client:
        while True:
            if client.is_connected:
                # 1. Read the raw bytes
                raw_data = await client.read_gatt_char(CHARACTERISTIC_UUID)
                
                # 2. Store in your variable (adjust conversion as needed)
                latest_value = float(raw_data.decode('utf-8'))
                
                # 3. Perform your threshold check here
                if latest_value > 22:
                    print(f"Threshold exceeded: {latest_value}")
                    email_service.send_fan_toggle_email(latest_value)
                    # Trigger your email/alert logic here
                
                print(f"Logged value: {latest_value}")
                
            # 4. Wait for the next interval
            await asyncio.sleep(CHECK_INTERVAL)

# To run it:
# asyncio.run(read_at_intervals())