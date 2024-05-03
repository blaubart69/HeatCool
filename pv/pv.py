import time
import datetime
import sys

from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import word_list_to_long,test_bit,get_2comp

def read_reg(client : ModbusClient, addr : int, nb : int, signed : bool, bits : int):
    regs = client.read_holding_registers(addr, nb)

    if not regs:
        print(f'error reading reg {addr}')
        return None
    elif nb > 2:
        print(f'ERROR: nb > 2. should be 1 or 2 ({nb})')
        return None
    elif nb == 2:
        value = word_list_to_long(regs)[0]
    elif nb == 1:
        value = regs[0]
    
    if signed and test_bit(value, offset=bits-1):
        value = get_2comp(value, val_size=bits)
    
    return value

def print_reg(value, unit, gain, desc):
    gained_value = value / gain
    print(f'{gained_value:>10} {unit}\t{desc}')

def create_influx_key_val(value : int, field : str, scale : int=1):
    if value is None:
        return []
    else:
        return [f'{field}={value / scale}']
    

# TCP auto connect on modbus request, close after it
c = ModbusClient(host="192.168.0.101", auto_open=False, auto_close=False)
c.open()
time.sleep(1.0)

try:
    i=0
    while True:
        # meter_active_power:
        #   > 0: feeding power to the power grid
        #   < 0: obtaining power from the power grid
        meter_active_power = read_reg(c, 37113, 2, signed=True, bits=32)
        meter_grid_freq    = read_reg(c, 37118, 1, signed=True, bits=16)
        inv_active_power   = read_reg(c, 32080, 2, signed=True, bits=32)

        if inv_active_power == None or meter_active_power == None:
            consumption = None
        else:
            consumption = inv_active_power - meter_active_power

        fields = []
        fields += create_influx_key_val(meter_active_power, 'meter_power')
        fields += create_influx_key_val(inv_active_power,   'inv_power')
        fields += create_influx_key_val(consumption,        'consumption')
        fields += create_influx_key_val(meter_grid_freq,    'grid_freq', scale=100)

        if len(fields) == 0:
            print('W: no datapoints')
        else:
            str_fields = ','.join(fields)
            sys.stdout.write(f'pv {str_fields}\n')
            sys.stdout.flush()
            i += 1
            sys.stderr.write(f'{datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")}'
                             f'\t{i}\t{str_fields}\n')
            sys.stderr.flush()

        time.sleep(5)

finally:
    c.close()

#print_reg( read_reg(c, 32085, 1), 'Hz',  100, 'Inverter: Grid frequency' )
#print_reg( read_reg(c, 32086, 1), '%',   100, 'Inverter: Efficiency' )
#print_reg( inv_active_power,      'kW', 1000, 'Inverter: Active power' )
#print_reg( meter_active_power,    'kW', 1000, 'Meter:    Active power' )
#print_reg( consumption,           'kW', 1000, 'Inv-Mtr:  Consumption')

