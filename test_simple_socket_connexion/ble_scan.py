import asyncio
from bleak import BleakScanner

async def main():
	print("Scanning for BLE devices...")
	devices = await BleakScanner.discover(return_adv=True)
	for d,ad in devices.values():
		print(f"Device: {d.name}| Address: {d.address}| RSSI:{ad.rssi}|UUID:{ad.service_uuids}")
asyncio.run(main())

