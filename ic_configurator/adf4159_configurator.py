# import sys
import os
import time
import math
from colorama import Fore, Back, Style
from colorama import init
init(autoreset=True)

F_REF = 25 * 10**6 # enter reference frequency in MHz here
F_VCO = 24 * 10**9 / 16 # enter input frequency in MHz here
F_DEV_RAMP = 164.886 * 10**6 / 16 # for 1 meter resolution
#F_DEV_RAMP = 5 * 164.886 * 10**6 / 16  # for 0.2 meter resolution
T_RAMP = 2.2 * 10**(-3)
NUM_STEPS = 20000 # number of frequency steps per ONE slope
DIV_CLK2 = 1

# reference path settings
DBL_REF_EN = 0 # set 0 to disable or 1 to enable reference doubler
DIV_REF = 1 # set 5-bit Divider Value. If 1 is selected there is no division
DIV_REF_2_EN = 0 # set 0 to disable or 1 to enable reference doubler

# IC's constrains
F_VCO_MIN = 2000
F_VCO_MAX = 4000

DIV_REF_MIN = 1
DIV_REF_MAX = 32

F_PFD_MIN = 10
F_PFD_MAX = 30

DIV_N_MIN = 23
DIV_N_MAX = 4095

N_MOD = 25 # fractional modulus divider

PLL_REG_DAT = []
PLL_REG_ADR = []
PLL_REG = []

for i in range(8):
    PLL_REG_DAT.append(0)
    PLL_REG_ADR.append(i)
    PLL_REG.append(i)

def compile_pll_reg():

    PLL_REG_DAT[0] |= ((N_FRAC >> 13) & 0x0FFF) << 3 # FRAC MSB
    PLL_REG_DAT[0] |= (N_INT & 0x0FFF) << 15 # INT
    PLL_REG_DAT[0] |= 0x78000000 # Muxout: 0x30000000 - Digital Lock Detect; 0x78000000 - Ramp Complete;
    PLL_REG_DAT[0] |= 0x80000000 # Ramp Enable: 0x00000000 - disable; 0x80000000 - enable

    PLL_REG_DAT[1] |= (0x000000 & 0x0FFFFF) << 3 # 12-bit phase value: 0x000000 to 0x0FFFFF where MSB is phase sign
    PLL_REG_DAT[1] |= (N_FRAC & 0x1FFF) << 15 # FRAC LSB
    PLL_REG_DAT[1] |= 0x00000000 # Phase Adjust Enable: 0x00000000 - disable; 0x10000000 - enable

    PLL_REG_DAT[2] |= (DIV_CLK1 & 0x0FFF) << 3 # 12-bit CLK1 divider
    PLL_REG_DAT[2] |= (DIV_REF & 0x1F) << 15 # 5-bit reference divider
    PLL_REG_DAT[2] |= DBL_REF_EN  << 20 # reference doubler
    PLL_REG_DAT[2] |= DIV_REF_2_EN  << 21 # 5-bit reference divider
    PLL_REG_DAT[2] |= 0x00  << 22 # prescaler: 0x00 - 4/5; 0x01 - 8/9
    PLL_REG_DAT[2] |= 0x0F  << 24 # CP Current: 0x00 (min) to 0x0F (max)
    PLL_REG_DAT[2] |= 0x00  << 28 # Cycle Sleep Reduction: 0x00 - disabled; 0x01 - enabled

    PLL_REG_DAT[3] |= 0x00 << 3 # counter reset: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[3] |= 0x00 << 4 # CP three-state: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[3] |= 0x00 << 5 # power down: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[3] |= 0x01 << 6 # CP polarity: 0x00 - negative; 0x01 - positive
    PLL_REG_DAT[3] |= 0x01 << 7 # Lock Detector Precision: 0x00 - low (14 nsec); 0x01 - high (6 nsec)
    PLL_REG_DAT[3] |= 0x00 << 8 # FSK: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[3] |= 0x00 << 9 # PSK: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[3] |= 0x00 << 10 # Ramp Mode: 0x00 - continuous sawtooth; 0x01 - continuous triangular; 0x02 - single sawtooth burst; 0x03 - single triangular burst
    PLL_REG_DAT[3] |= 0x00 << 14 # Sigma-Delta Reset: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[3] |= 0x00 << 15 # N Divider Load Select: 0x00 - on Sigma-Delta Clock; 0x01 - delayed 4 cycles
    PLL_REG_DAT[3] |= 0x01 << 16 # LOL: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[3] |= 0x01 << 17 # Reserved
    PLL_REG_DAT[3] |= 0x00 << 21 # Negative Bleed Enable: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[3] |= NEG_BLEED_CURRENT << 22 # Negative Bleed Current: 0x00 (min) to 0x07 (max)

    PLL_REG_DAT[4] |= 0x00 << 6 # Clock Divider Select: 0x00 - Load CLK1; 0x01 - Load CLK2
    PLL_REG_DAT[4] |= (DIV_CLK2 & 0x0FFF) << 7 # 12-bit CLK2 divider
    PLL_REG_DAT[4] |= 0x03 << 19 # Clock Divider Mode: 0x00 - Off; 0x01 - fast lock divider; 0x02 - reserved; 0x03 - ramp divider
    PLL_REG_DAT[4] |= 0x03 << 21 # Ramp Status: 0x00 - normal operation; 0x03 - ramp complete to muxout
    PLL_REG_DAT[4] |= 0x00 << 26 # Sigma-Delta Mode: 0x00 - normal operation; 0x0E - disabled when FRAC=0
    PLL_REG_DAT[4] |= 0x00 << 31 # LE Select: 0x00 - LE from pin; 0x01 - LE synch with nREFIN

    PLL_REG_DAT[5] |= (DEV_WORD & 0xFFFF) << 3 # 16-bit Deviation Word
    PLL_REG_DAT[5] |= (DEV_OFFSET_WORD & 0x000F) << 19 # 4-bit Deviation Offset Word
    PLL_REG_DAT[5] |= 0x00 << 23 # Deviation Word Select: 0x00 - Deviation Word 1; 0x01 - Deviation Word 2
    PLL_REG_DAT[5] |= 0x00 << 24 # Dual Ramp Enable: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[5] |= 0x00 << 25 # FSK Enable: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[5] |= 0x00 << 26 # Interrupt: 0x00 - interrupt off; 0x01 - load channel continue sweep; 0x02 - not used; 0x03 - load channel stop sweep
    PLL_REG_DAT[5] |= 0x00 << 28 # Parabolic Ramp Enable: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[5] |= 0x00 << 29 # TX_data Ramp CLK: 0x00 - CLK DIV; 0x01 - TX_data
    PLL_REG_DAT[5] |= 0x00 << 30 # TX_data Invert: 0x00 - disabled; 0x01 - enabled

    PLL_REG_DAT[6] |= (NUM_STEPS & 0x0FFFFF) << 3 # 16-bit Deviation Word
    PLL_REG_DAT[6] |= 0x00 << 23 # Step Select: 0x00 - Step Word 1; 0x01 - Step Word 2

    PLL_REG_DAT[7] |= 0x0000 << 3 # 12-bit Delay Start Word: 0x0000 (0) to 0x0FFF (4095)
    PLL_REG_DAT[7] |= 0x00 << 15 # Delay Start Enable: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[7] |= 0x00 << 16 # Delay CLK Select: 0x00 - PFD CLK; 0x01 - PFD CLK * CLK1
    PLL_REG_DAT[7] |= 0x00 << 17 # Ramp Delay Enable: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[7] |= 0x00 << 18 # Ramp Delay FL: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[7] |= 0x00 << 19 # Fast Ramp Enable: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[7] |= 0x00 << 20 # TX_data Trigger: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[7] |= 0x00 << 21 # Single Full Triangle: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[7] |= 0x00 << 22 # Triangular Delay: 0x00 - disabled; 0x01 - enabled
    PLL_REG_DAT[7] |= 0x00 << 23 # TX_data Trigger Delay: 0x00 - disabled; 0x01 - enabled


    for i in range(8):
        PLL_REG[i] = PLL_REG_DAT[i] | PLL_REG_ADR[i]


# TODO
def write_pll_reg_to_serial(data):
    import serial
    import time
    # open serial port
    ser = serial.Serial('COM3', 115200, timeout=0.5)

    for i in range(7, -1, -1):
        ser_data = "$PLL 0x" + f"{data[i]:08X}"
        ser.write(ser_data.encode('utf-8'))
#        ser_data = ser.read(32)
#        print(ser_data.decode('utf-8'))

    # close serial port
    if ser != None and ser.isOpen():
        ser.close()
        ser = None


def write_pll_reg_to_file(REG_DAT):

    with open(r"ADF4159 Registers.txt", "w") as file:
        for i in range(7, -1, -1):
            file.write("0x" + (f"{REG_DAT[i]:08X}") + '\n')

def replace_pll_reg_in_main_c(REG_DAT):

    # Here we are copying main.c file to main.c.tmp while line begining with "WriteRegSYNTH" has to be appear
    # When the line begining with "WriteRegSYNTH" has met we replace it with own REG_DAT starting from index 7 to 0
    # Las we replace main.c file with main.c.tmp and delete the last

    with open("D:\SYNTEIRA\GitHub\STS_109_STM32_PYTHON_1\Src\main.c", "r") as f1:
        with open("D:\SYNTEIRA\GitHub\STS_109_STM32_PYTHON_1\Src\main.c.tmp", "w") as f2:
            cnt = 7
            string = " "
            while string != "":
                string = f1.readline()
                if "    WriteRegSYNTH(" in string:
                    string = "    WriteRegSYNTH(0x" + (f"{REG_DAT[cnt]:08X}")  + ");" + '\n'
                    cnt -= 1
                f2.write(string)

    os.remove("D:\SYNTEIRA\GitHub\STS_109_STM32_PYTHON_1\Src\main.c")
    os.rename("D:\SYNTEIRA\GitHub\STS_109_STM32_PYTHON_1\Src\main.c.tmp", "D:\SYNTEIRA\GitHub\STS_109_STM32_PYTHON_1\Src\main.c")
 
if __name__ == '__main__':

    DIV_REF_TOTAL = pow(2, DBL_REF_EN)/(DIV_REF * pow(2, DIV_REF_2_EN))

    F_PFD = F_REF * DIV_REF_TOTAL

    WFM_FACT = 1 # ramp waveform factor: 1 for sawtooth; 2 for triangular

    # precalculate frequency deviation step
    F_DEV_STEP = F_DEV_RAMP / NUM_STEPS

    F_RES = F_PFD / (pow(2, N_MOD)) # frequency resolution

    DEV_WORD_NUM_BIT = 16

    DEV_WORD_MAX = pow(2, DEV_WORD_NUM_BIT - 1)

    DEV_OFFSET_WORD = int(math.ceil((math.log(F_DEV_STEP / (F_RES * DEV_WORD_MAX)) / math.log(2)))) # 4-bit deviation offset word. math.log(x) returns ln(x) so there is used the rule log2(x) = ln(x)/ln(2)

    if DEV_OFFSET_WORD < 0:
        DEV_OFFSET_WORD = 0

    # recalculate frequency deviation step in accordance with DEV_OFFSET_WORD
    F_DEV_RES = F_RES * (pow(2, DEV_OFFSET_WORD))
    
    DEV_WORD = int(math.ceil(F_DEV_STEP / (F_DEV_RES))) # 16-bit deviation word

    # recalculate frequency deviation step
    F_DEV_STEP = WFM_FACT * (F_PFD/pow(2, N_MOD)) * DEV_WORD * pow(2, DEV_OFFSET_WORD)

    T_STEP = T_RAMP / NUM_STEPS # smallest step

    DIV_CLK1 = int(math.ceil(T_STEP * F_PFD / DIV_CLK2))

    # recalculate step time
    T_STEP = DIV_CLK1 * DIV_CLK2 / F_PFD

    # recalculate ramp frequency deviation
    F_DEV_RAMP = F_DEV_STEP * NUM_STEPS

    # recalculate ramp time
    T_RAMP = WFM_FACT * T_STEP * NUM_STEPS

    N_TOT = F_VCO / F_PFD

    N_INT = int(F_VCO // F_PFD) # // returns integer division

    if N_TOT % 1 == 0:
        N_FRAC = 0
    else:
        N_FRAC = int(round(((N_TOT % 1) * pow(2, 25)), 0))

    # calculate negative current bleed
    I_BLEED = 4 * 5000 / N_TOT # 5000 - is Icp in uA
    if I_BLEED < 7.38:
        NEG_BLEED_CURRENT = 0b000
    elif I_BLEED < 18.14:
        NEG_BLEED_CURRENT = 0b001
    elif I_BLEED < 39.18:
        NEG_BLEED_CURRENT = 0b010
    elif I_BLEED < 81.4:
        NEG_BLEED_CURRENT = 0b011
    elif I_BLEED < 167.2:
        NEG_BLEED_CURRENT = 0b100
    elif I_BLEED < 339.7:
        NEG_BLEED_CURRENT = 0b101
    elif I_BLEED < 685.5:
        NEG_BLEED_CURRENT = 0b110
    elif I_BLEED >= 685.5:
        NEG_BLEED_CURRENT = 0b111
 
    compile_pll_reg()

    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'Given:')
    print('+----------------------------------------------+')
    print('VCO Frequency = ' + str(F_VCO / pow(10, 6)) + ' MHz')
    print('Reference Frequency = ' + str(F_REF / pow(10, 6)) + ' MHz')
    print('PFD Frequency = ' + str(F_PFD / pow(10, 6)) + ' MHz')
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'N-Divider:')
    print('+----------------------------------------------+')
    print('Total = ' + str(N_TOT))    
    print('INT =   ' + str(N_INT) + ' (decimal) or ' '%x' % N_INT + ' (HEX)')    
    print('FRAC =   ' + str(N_FRAC) + ' (decimal) or  ' '%x' % N_FRAC + ' (HEX)')
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'Ramp:')
    print('+----------------------------------------------+')
    print('Number of Frequency Steps per Slope = ' + str(NUM_STEPS))
    print(Fore.RED + Style.NORMAL + 'Frequency Deviation at Ka-band = ' + str(F_DEV_RAMP * 16 / pow(10, 6)) + ' MHz')
    print(Fore.GREEN + Style.NORMAL + 'Frequency Deviation per Ramp = ' + str(F_DEV_RAMP / pow(10, 6)) + ' MHz')
    print('Frequency Deviation per Step = ' + str(F_DEV_STEP / pow(10, 3)) + ' kHz')
    print('Frequency Deviation Resolution = ' + str(F_DEV_RES) + ' Hz')
    print(Fore.GREEN + Style.NORMAL + 'Time per Ramp = ' + str(T_RAMP / pow(10, -3)) + ' msec')
    print('Time per Step = ' + str(T_STEP / pow(10, -6)) + ' usec')
    print('CLK1 Divider = ' + str(DIV_CLK1))
    print('CLK2 Divider = ' + str(DIV_CLK2))
    print('Deviation Word 16-bit = ' + str(DEV_WORD))
    print('Deviation Offset Word 4-bit = ' + str(DEV_OFFSET_WORD))
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'PLL Registers:')
    print('+----------------------------------------------+')

    for i in range(8):
        PLL_REG[i] = PLL_REG_DAT[i] | PLL_REG_ADR[i]
        print('R' + str(i) + ' = ' '%x' % PLL_REG[i])

#    write_pll_reg_to_file(PLL_REG)

#    replace_pll_reg_in_main_c(PLL_REG)
    write_pll_reg_to_serial(PLL_REG)