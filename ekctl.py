#!/usr/bin/env python3
from pymodbus.client import ModbusTcpClient
import argparse

WATCHDOG_TYPE = ['write-telegram', 'telegram', 'disable']
FALLBACK_MODE = ['set-zero', 'freeze', 'stop-ebus']
EBUS_MODE = ['init', 'op']

parser = argparse.ArgumentParser(description='Query info about an ek9000 bus coupler')
parser.add_argument('--ip', required=True, type=str, help='IP address of the coupler')
parser.add_argument('--port', required=False, type=int, default=502, help='Port number of the device')
parser.add_argument('--version', action='store_true', help='Display summary of device version')
parser.add_argument('--layout', action='store_true', help='Display layout of the rail')
parser.add_argument('--summary', action='store_true', help='Display summary of the rail, including hardware version info and current state')
parser.add_argument('--watchdog-type', dest='WATCHDOG_TYPE', type=str, choices=WATCHDOG_TYPE, help='Set the watchdog type for the device. Default="Write Telegram"')
parser.add_argument('--watchdog-time', dest='WATCHDOG_TIME', type=int, help='Set the watchdog time to this, in ms. Default=1000')
parser.add_argument('--watchdog-reset', dest='WATCHDOG_RESET', action='store_true', help='Reset watchdog timer')
parser.add_argument('--fallback-mode', dest='FALLBACK_MODE', type=str, choices=FALLBACK_MODE, help='Set the fallback mode for the device. Default="Set to Zero')
parser.add_argument('--writelock', dest='WRITELOCK', type=int, choices=[0,1], help='Enable or disable writelock')
parser.add_argument('--ebus-mode', dest='EBUS_MODE', type=str, choices=EBUS_MODE, help='Set the E-Bus to the requested state')



def print_version(client: ModbusTcpClient) -> None:
    hardwareVer = client.read_input_registers(0x1030, 1)
    print(f'Hardware version: {hardwareVer.registers[0]}')
    vers = client.read_input_registers(0x1031, 7)
    print(f'Software version: {vers.registers[0]}.{vers.registers[1]}.{vers.registers[2]}')
    print(f'Serial number: {vers.registers[3]}')
    print(f'Production date (DD/MM/YYYY): {vers.registers[4]}/{vers.registers[5]}/{vers.registers[6]}')


def print_layout(client: ModbusTcpClient) -> None:
    terms = client.read_input_registers(0x6001, 120)
    for t in terms.registers:
        if t == 0:
            break
        print(f'EL{t}')


def print_summary(client: ModbusTcpClient) -> None:
    print_version(client)
    image = client.read_input_registers(0x1010, 4)
    labels = ['Analog out (bytes)', 'Analog in (bytes)', 'Digital out (bits)', 'Digital in (bits)']
    for i in range(0, len(image.registers)):
        print(f'{labels[i]}: {image.registers[i]}')
    image = client.read_input_registers(0x1021, 2)
    print(f'Triggered fallbacks: {image.registers[0]}')
    print(f'Active TCP connections: {image.registers[1]}')
    image = client.read_input_registers(0x1040, 1)
    print(f'E-Bus status: {"OK" if image.registers[0] else "ERROR"}')
    image = client.read_input_registers(0x1120, 5)
    print(f'Watchdog time (ms): {image.registers[0]}')
    print(f'Watchdog type: {WATCHDOG_TYPE[image.registers[2]]}')
    print(f'Fallback mode: {FALLBACK_MODE[image.registers[3]]}')
    print(f'Writelock: {"Yes" if image.registers[4] else "No"}')


def set_wd_time(time: int, client: ModbusTcpClient) -> None:
    client.write_register(0x1120, time)


def set_wd_type(type: str, client: ModbusTcpClient) -> None:
    client.write_register(0x1122, WATCHDOG_TYPE.index(type))


def reset_wdt(client: ModbusTcpClient) -> None:
    client.write_register(0x1121, 1)


def set_fallback_mode(type: str, client: ModbusTcpClient) -> None:
    client.write_register(0x1123, FALLBACK_MODE.index(type))


def set_writelock(wr: bool, client: ModbusTcpClient) -> None:
    client.write_register(0x1124, 1 if wr else 0)


def set_ebus_mode(mode: str, client: ModbusTcpClient) -> None:
    client.write_register(0x1140, EBUS_MODE.index(mode))


def main():
    args = parser.parse_args()
    client = ModbusTcpClient(args.ip, args.port)
    if not client.connect():
        print(f'Could not connect to {args.ip}:{args.port}')
        exit(1)

    if args.version:
        print_version(client)
        exit(0)
    if args.layout:
        print_layout(client)
        exit(0)
    if args.summary:
        print_summary(client)
        exit(0)
        
    if args.WATCHDOG_TIME is not None:
        set_wd_time(args.WATCHDOG_TIME, client)
    if args.WATCHDOG_TYPE is not None:
        set_wd_type(args.WATCHDOG_TYPE, client)
    if args.WATCHDOG_RESET:
        reset_wdt(client)
    if args.FALLBACK_MODE is not None:
        set_fallback_mode(args.FALLBACK_MODE, client)
    if args.WRITELOCK is not None:
        set_writelock(args.WRITELOCK, client)
    if args.EBUS_MODE is not None:
        set_ebus_mode(args.EBUS_MODE, client)



if __name__ == '__main__':
    main()