#!/usr/bin/env python3

import argparse
from pymodbus.client import ModbusTcpClient
import struct

typemap = {
    'int8': {
        'size': 1,
    },
    'uint8': {
        'size': 1
    },
    'int16': {
        'size': 2
    },
    'uint16': {
        'size': 2
    },
    'int32': {
        'size': 4,
        'unpack': 'i',
    },
    'uint32': {
        'size': 4,
        'unapck': 'I'
    },
    'int64': {
        'size': 8,
        'unpack': 'l'
    },
    'uint64': {
        'size': 8,
        'unpack': 'L'
    },
    'bool': {
        'size': 1
    },
    'string': {
        'size': -1,
        'unpack': 's'
    },
    'float32': {
        'size': 4,
        'unpack': 'f'
    },
    'float64': {
        'size': 8,
        'unpack': 'd'
    }
}

parser = argparse.ArgumentParser()
parser.add_argument('--terminal', type=int, required=True, help="Terminal index to read from")
parser.add_argument('--param', type=str, required=True, help="Parameter to read, in the format INDEX:SUBINDEX")
parser.add_argument('--ip', type=str, required=True, help="IP of the coupler")
parser.add_argument('--port', type=int, default=502, help="Port")
parser.add_argument('--type', type=str, required=True, choices=typemap.keys(), help="Parameter type")
args = parser.parse_args()


def get_param():
    s = args.param.split(':')
    return [int(s[0].replace('0x',''), 16),int(s[1].replace('0x',''), 16)]


def print_generic(type: str, regs: list):
    if not 'unpack' in typemap[type]:
        print(int(regs[0]))
        return
    s = '='
    for i in range(0, len(regs)):
        s += 'H'
    print(struct.unpack(typemap[type]['unpack'], regs))


def main():
    client = ModbusTcpClient(args.ip, args.port)
    if not client.connect():
        print('Could not connect to coupler :(')
        exit(1)

    trans = []
    trans.append(1) # 1 = execute
    trans.append(args.terminal)
    trans.append(get_param()[0])
    trans.append(get_param()[1])
    trans.append(0) # Length not needed for this

    client.write_registers(0x1400, trans)

    tl = 120
    if typemap[args.type]['size'] >= 0:
        tl = typemap[args.type]['size'] + 6

    r = client.read_holding_registers(0x1400, tl)
    while r.registers[0] == 0x201:
        r = client.read_holding_registers(0x1400, tl)

    if r.registers[5] != 0:
        print(f'Read failed with code {r.registers[5]}')
        exit(1)

    regs = r.registers[6:]

    if args.type.startswith('int') or args.type.startswith('uint'):
        print_generic(args.type, regs)
    elif args.type == 'bool':
        print('true' if regs[0] else 'false')
    elif args.type == 'string':
        print_generic(args.type, regs)
    else:
        raise KeyError()
    
if __name__ == '__main__':
    main()