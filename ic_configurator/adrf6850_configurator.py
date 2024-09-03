# import sys
import os
import time
import fileinput

F_REF = 20 # enter reference frequency in MHz here
F_RF = 420 # enter input frequency in MHz here

# reference path settings
DBL_REF_EN = 1 # Set 0 to disable or 1 to enable reference doubler
DIV_REF = 1 # Set 5-bit Divider Value. If 1 is selected there is no division
DIV_REF_2_EN = 0 # Set 0 to disable or 1 to enable reference doubler

# IC's constrains
F_VCO_MIN = 2000
F_VCO_MAX = 4000

DIV_REF_MIN = 1
DIV_REF_MAX = 32

F_PFD_MIN = 10
F_PFD_MAX = 30

DIV_N_MIN = 23
DIV_N_MAX = 4095

DIV_QUAD_MOD = 4

PLL_REG_DAT = []
PLL_REG_ADR = []
PLL_REG = []

for i in range(31):
    PLL_REG_DAT.append(0)
    PLL_REG_ADR.append(i)
    PLL_REG.append(i)

# reserved registers
PLL_REG_DAT[4] = 0x01
PLL_REG_DAT[5] = 0x00
PLL_REG_DAT[8] = 0x00
PLL_REG_DAT[11] = 0x00
PLL_REG_DAT[13] = 0x08
PLL_REG_DAT[15] = 0x00
PLL_REG_DAT[16] = 0x00
PLL_REG_DAT[17] = 0x00
PLL_REG_DAT[18] = 0x00
PLL_REG_DAT[19] = 0x00
PLL_REG_DAT[20] = 0x00
PLL_REG_DAT[21] = 0x00
PLL_REG_DAT[22] = 0x00
PLL_REG_DAT[26] = 0x00

def write_pll_reg_to_serial(REG_DAT):

    # open serial port
    ser = serial.Serial('COM6', 115200, timeout=1)

    ser.write(REG_DAT)

    # close serial port
    if ser != None and ser.isOpen():
        ser.close()
        ser = None

def write_pll_reg_to_file():

    with open(r"D:\\Components\\Analog Devices\\ADRF6850\\ADRF6850 Registers.txt", "w") as file:
        for i in range(30, -1, -1):
            file.write(str(hex(PLL_REG[i])) + '\n')

def replace_pll_reg_in_c(REG_DAT):

    for dat in REG_DAT:
        text = str(hex(dat))   # if any line contains this text, I want to modify the whole line.

        with open("D:\Components\Analog Devices\ADRF6850\ADRF6850_BlackPill\Src\main.c", "r") as f1:
            with open("D:\Components\Analog Devices\ADRF6850\ADRF6850_BlackPill\Src\main.c.tmp", "w") as f2:
                string = " "
                while string != "":
                    string = f1.readline()
                    if text[:6] in string:
                        string = "    WriteRegSYNTH(" + text  + ");" + '\n'
                    f2.write(string)

        os.remove("D:\Components\Analog Devices\ADRF6850\ADRF6850_BlackPill\Src\main.c")
        os.rename("D:\Components\Analog Devices\ADRF6850\ADRF6850_BlackPill\Src\main.c.tmp", "D:\Components\Analog Devices\ADRF6850\ADRF6850_BlackPill\Src\main.c")

if __name__ == '__main__':

    DIV_REF_TOTAL = pow(2, DBL_REF_EN)/(DIV_REF * pow(2, DIV_REF_2_EN))
    F_PFD = F_REF * DIV_REF_TOTAL

    F_VCO = DIV_QUAD_MOD * F_RF
    N_INT = int(F_VCO // F_PFD) # // returns integer division

    if F_RF < 125:
        RFDIV = 0b011
    elif F_RF < 250:
        RFDIV = 0b010
    elif F_RF < 500:
        RFDIV = 0b001
    elif F_RF < 1000:
        RFDIV = 0b000
    elif F_RF >= 1000:
        print('RF Frequency is too large')

    N = (pow(2, RFDIV) * 2 * F_RF) / F_PFD

    if N % 1 == 0:
        N_FRAC = 0
    else:
        N_FRAC = int(round(((N % 1) * pow(2, 25)), 0))

    print('RF Frequency = ' + str(F_RF) + ' MHz')
    print('Reference Frequency = ' + str(F_REF) + ' MHz')
    print('PFD Frequency = ' + str(F_PFD) + ' MHz')

    print('Reference Multiplication Factor = ' + str(DIV_REF_TOTAL))
    print('N Divider = ' + str(N))    
    print('Integer N Divider = ' + str(N_INT))    
    print('Integer N Divider in HEX Format ' + '%x' % N_INT)
    print('Fractional N Divider = ' + str(N_FRAC))
    print('Fractional N Divider in HEX Format ' + '%x' % N_FRAC)
    print('RFDIV = ' + str(RFDIV))

    PLL_REG_DAT[0] = N_FRAC & 0xFF
    PLL_REG_DAT[1] = (N_FRAC & 0xFF00) >> 8
    PLL_REG_DAT[2] = (N_FRAC & 0xFF0000) >> 16
    PLL_REG_DAT[3] = (N_FRAC & 0x01000000) >> 24

    if DIV_REF == 1:
        PLL_REG_DAT[5] &= ~0x10 # reset bit 5
    else:
        PLL_REG_DAT[5] |= 0x10 # set bit 5

    PLL_REG_DAT[6] = N_INT & 0xFF

    PLL_REG_DAT[7] = (N_INT & 0x0F00) >> 8
    PLL_REG_DAT[7] |= 0xE0 # MUXOUT control: 0x00 - tristate; 0x10 - logic high; 0x20 - logic low; 0xD0 - RCLK/2; 0xE0 - NCLK/2

    PLL_REG_DAT[9] |= 0xF0 # CP current: 0x00 - lowest; 0xF0 - highest

    PLL_REG_DAT[10] |= (DIV_REF & 0b11111) # 5 bit reference divider value: 0x00 - lowest; 0xF0 - highest
    PLL_REG_DAT[10] |= (DBL_REF_EN << 5) # reference doubler enable
    PLL_REG_DAT[10] |= (DIV_REF_2_EN << 6) # reference divide by 2 divider enable

    PLL_REG_DAT[12] |= 0x00 # PLL power down: 0x00 - power up; 0x04 - power down

    PLL_REG_DAT[14] |= 0x00 # PLL lock detect count 2: 0x00 - 2048/3072 pulses; 0x80 - 4096 pulses

    PLL_REG_DAT[23] |= 0x04 # PLL lock detect precision: 0x00 - low (16 nsec); 0x40 - high (6 nsec)
    PLL_REG_DAT[23] |= 0x08 # PLL lock detect count 1: 0x00 - 3072 pulses; 0x80 - 2048 pulses
    PLL_REG_DAT[23] |= 0x10 # PLL lock detect enable: 0x00 - disable; 0x10 - enable

    PLL_REG_DAT[24] |= 0x00 # Disable VCO autocalibration: 0x00 - enable autocalibration; 0x01 - disable

    BCDIV = int(100 * F_PFD / 24) # see eq. 3 in datasheet
    PLL_REG_DAT[25] |= (BCDIV & 0xFF) # Autocalibration timer

    PLL_REG_DAT[27] |= 0x03 # LO Monitor output power: 0x00 - minimum (-24 dBm) to 0x03 - maximum (-6 dBm)
    PLL_REG_DAT[27] |= 0x04 # LO Monitor enable: 0x00 - disable; 0x04 - enable

    PLL_REG_DAT[28] |= (RFDIV & 0x0F) # Autocalibration timer
    PLL_REG_DAT[28] |= 0x08 # Set Reserved bit 3

    PLL_REG_DAT[29] |= 0x01 # Demodulator power up: 0x00 - power down; 0x01 - power up
    PLL_REG_DAT[29] |= 0x00 # Narrowband and wideband mode selection: 0x00 - narrowband mode; 0x08 - wideband mode
    PLL_REG_DAT[29] |= 0x30 # Narrowband filter cut off selection: 0x00 - 50 MHz; 0x10 - 43 MHz, 0x20 - 37 MHz; 0x30 - 30 MHz
    PLL_REG_DAT[29] |= 0x40 # Vocm reference: 0x00 - external; 0x40 - internal

    PLL_REG_DAT[30] |= 0x01 # VGA power up: 0x00 - power down; 0x01 - power up
    PLL_REG_DAT[30] |= 0x00 # VGA gain mode polarity: 0x00 - positive gain slope; 0x04 - negative gain slope

    CMD = 0xD4 # write command prefix to each data transaction

    for i in range(31):
        PLL_REG[i] = (CMD << 16) | (PLL_REG_ADR[i] << 8) | PLL_REG_DAT[i]
        print('%x' % PLL_REG[i])

    write_pll_reg_to_file()

#    for i in range(31):
    replace_pll_reg_in_c(PLL_REG)

#    CR[30] |= 0x00 # VGA power off in 
#    for reg_data in CR:
#        write_pll_reg_to_serial(reg_data)
#    time.sleep(1)
#    CR[30] |= 0x01
#    write_pll_reg_to_serial(CR[30])

