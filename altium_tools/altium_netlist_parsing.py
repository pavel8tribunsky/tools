# coding:utf8


# Altium Designer netlist parser
# This Python script is using to parse the netlist form Altium Designer and creates definitions file for MCU firmware.
# It's necessary to do from Altium Designer:
# File > Export > NetList Schematic > Scope: Project > NetList Format: WireList netlist


import os
from colorama import Fore, Back, Style
from colorama import init
init(autoreset=True)


exclude_pins = []
service_pins = ('NRST', 'BOOT0', 'PB2', 'HSEI', 'HSEO', 'LSEI', 'LSEO', 'PA13', 'PA14', 'PB3')


def parse_netlist(designator='D12'):

    # Here we are copying main.c file to main.c.tmp while line begining with "WriteRegSYNTH" has to be appear
    # When the line begining with "WriteRegSYNTH" has met we replace it with own REG_DAT starting from index 7 to 0
    # Las we replace main.c file with main.c.tmp and delete the last

    pinout_tmp = []
    with open("F:\\1\\STVF.467769.001_1.NET", "r") as file:
            string = " "
            net_label = " "
            while string != "":
                string = file.readline()
                if "[" in string:
                    net_label_tmp = string.split(' ')
                    net_label = net_label_tmp[1]
                    #print(net_label[1])
                elif ("        " + designator) in string:
                    cpin = " ".join(string.split())
                    pin = cpin.split()
                    pin.insert(0, net_label)
                    pin.pop(1)
                    pin_num = pin.pop(1)
                    pin.pop()
                    pin.insert(0, pin_num)
                    pin = [p.rstrip() for p in pin]
                    pinout_tmp.append(pin)
    pinout_tmp.pop(0)
    l = len(pinout_tmp)

    pinout = []
    for i in range(l):
        pinout.append(i)

    # print(pinout_tmp)

    # for p in pinout_tmp:
    #     pin_num = int(p[0])
    #     p[0] = pin_num

    pinout_tmp.sort()

    print(pinout_tmp)

    return pinout_tmp


def clear_pinout(pinout, service_pins, clear_power_nets='yes', clear_passive_nets='yes', exclude=exclude_pins):
    pinout_clr = []
    for pin in pinout:
        if pin[3] == 'POWER' and clear_power_nets == 'yes':
            pass
        elif pin[3] == 'PASSIVE' and clear_passive_nets == 'yes':
            pass
        else:
            pinout_clr.append(pin)

    pname = []
    for pin in pinout_clr:
        pname.append(pin[2])

    service_pin_index = []
    for p in service_pins:
        try:
            idx = pname.index(p)
            service_pin_index.append(idx)
        except ValueError:
            pass

    service_pin_index.sort()

    i = 0
    for idx in service_pin_index:
        idx -= i
        pinout_clr.pop(idx)
        i += 1

    return pinout_clr


def compose_definitions(pinout):
    with open("F:\\1\\STVF.467769.001_1.DEF", "w") as file:
        for pin in pinout:

            pin_num = pin[2]
            pin_num = pin_num[2:]
            pin_name = pin[1]
            pin_name = pin_name[4:]
            string = '#define ' + pin_name + '_Pin' + ' GPIO_PIN_' + pin_num + '\n'
            file.write(string)
            print(string)

            pin_port = pin[2]
            pin_port = pin_port[1]
            string = '#define ' + pin_name + '_GPIO_Port' + ' GPIO' + pin_port + '\n'
            file.write(string)
            print(string)

            string = '\n'
            file.write(string)
            print(string)


if __name__ == '__main__':

    pinout = parse_netlist('D12')
    pinout = clear_pinout(pinout, service_pins)
    print(pinout)
    compose_definitions(pinout)

    # print(' ')
    # print(Fore.CYAN + Style.BRIGHT + 'Given:')
    # print('+----------------------------------------------+')
    # print('VCO Frequency = ' + str(F_VCO / pow(10, 6)) + ' MHz')
    # print('Reference Frequency = ' + str(F_REF / pow(10, 6)) + ' MHz')
    # print('PFD Frequency = ' + str(F_PFD / pow(10, 6)) + ' MHz')
    # print(' ')
    # print(Fore.CYAN + Style.BRIGHT + 'N-Divider:')
    # print('+----------------------------------------------+')
    # print('Total = ' + str(N_TOT))
    # print('INT =   ' + str(N_INT) + ' (decimal) or ' '%x' % N_INT + ' (HEX)')
    # print('FRAC =   ' + str(N_FRAC) + ' (decimal) or  ' '%x' % N_FRAC + ' (HEX)')
    # print(' ')
    # print(Fore.CYAN + Style.BRIGHT + 'Ramp:')
    # print('+----------------------------------------------+')
    # print('Number of Frequency Steps per Slope = ' + str(NUM_STEPS))
    # print(Fore.RED + Style.NORMAL + 'Frequency Deviation at Ka-band = ' + str(F_DEV_RAMP * 16 / pow(10, 6)) + ' MHz')
    # print(Fore.GREEN + Style.NORMAL + 'Frequency Deviation per Ramp = ' + str(F_DEV_RAMP / pow(10, 6)) + ' MHz')
    # print('Frequency Deviation per Step = ' + str(F_DEV_STEP / pow(10, 3)) + ' kHz')
    # print('Frequency Deviation Resolution = ' + str(F_DEV_RES) + ' Hz')
    # print(Fore.GREEN + Style.NORMAL + 'Time per Ramp = ' + str(T_RAMP / pow(10, -3)) + ' msec')
    # print('Time per Step = ' + str(T_STEP / pow(10, -6)) + ' usec')
    # print('CLK1 Divider = ' + str(DIV_CLK1))
    # print('CLK2 Divider = ' + str(DIV_CLK2))
    # print('Deviation Word 16-bit = ' + str(DEV_WORD))
    # print('Deviation Offset Word 4-bit = ' + str(DEV_OFFSET_WORD))
    # print(' ')
    # print(Fore.CYAN + Style.BRIGHT + 'PLL Registers:')
    # print('+----------------------------------------------+')
