import asyncio
from bleak import BleakScanner

def detection_callback(device, advertisement_data):
    # This triggers every time a device is found or updates its advertisement data
    print(f"Device: {device.address} | Name: {device.name} | RSSI: {advertisement_data.rssi}")

async def main():
    # Create the scanner with a callback
    scanner = BleakScanner(detection_callback)
    
    # 1. Start the periodic background scan
    await scanner.start()
    print("Scanning... Press Ctrl+C to stop.")
    
    # 2. Run the scan for a specific duration or until an event finishes
    await asyncio.sleep(3.0) # Scan for 20 seconds
    
    # 3. Stop the scan cleanly
    await scanner.stop()
    print("Scan stopped.")
    print(scanner.discovered_devices_and_advertisement_data)
    for addr, (dev, adv) in scanner.discovered_devices_and_advertisement_data.items():
        print(addr, dev, adv)
        print(f'addr:{addr}|dev:{dev}|rssi:{adv.rssi}|tx_power:{adv.tx_power}')
       
# Run the event loop
asyncio.run(main())
