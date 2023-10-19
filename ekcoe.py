#!/usr/bin/env python3

import argparse
from pymodbus.client import ModbusTcpClient
import struct

typemap = {
    'int8': 1,
    'uint8': 1,
    'int16': 2,
    'uint16': 2,
    'int32': 4,
    'uint32': 4,
    'int64': 8,
    'uint64': 8,
    'bool': 1
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

tl = typemap[args.type] + 6
r = client.read_holding_registers(0x1400, tl)
while r.registers[0] == 0x201:
    r = client.read_holding_registers(0x1400, tl)

if r.registers[5] != 0:
    print(f'Read failed with code {r.registers[5]}')
    exit(1)

a = r.registers[6]
b = r.registers[7]
c = r.registers[8] if len(r.registers) > 8 else 0
c = r.registers[9] if len(r.registers) > 9 else 0
if args.type == 'int32':
    print(struct.unpack('i', struct.pack('=HH', a,b)))
elif args.type == 'uint32':    
    print(struct.unpack('i', struct.pack('=HH', a,b)))
elif args.type == 'int64':
    print(struct.unpack('l', struct.pack('=HHHH', a,b,c,d)))
elif args.type == 'uint64':
    print(struct.unpack('L', struct.pack('=HHHH', a,b,c,d)))
elif args.type == 'int16' or args.type == 'uint16':
    print(int(a))
