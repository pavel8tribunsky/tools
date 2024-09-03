import math
import sys
from colorama import Fore, Back, Style
from colorama import init
init(autoreset=True)

F_REF = 40 * 10**6  # enter reference frequency in Hz here
F_VCO = 630 * 10**6  # enter input frequency in Hz here
F_PFD = 10 * 10**6  # enter frequency step in Hz here

CP_CURRENT = 7  # charge pump current
PFD_POLARITY = 'positive'
MUXOUT = 'dvdd'


def adf4106_calc_counters(f_vco, f_ref, f_pfd):
    """ Calculates values of prescaler and R-, A-, B- counters of ADF4106 and returns P-R-A-B-N.

    Args:
        f_vco: VCO frequency in Hz
        f_ref: Reference frequency in Hz
        f_pfd: Phase-frequency detector operating frequency in Hz

    Returns:
        List of [prescaler, R-counter, A-counter, B-counter, N-counter]

    Raises:
        KeyError: Raises an exception.
    """
    if f_vco < 0.5 * 10**9:
        print("ERROR: VCO frequency is out of range")
        sys.exit(0)
    elif f_vco < 2.6 * 10**9:
        prslr = 8
    elif f_vco < 5.2 * 10**9:
        prslr = 16
    elif f_vco <= 6 * 10**9:
        prslr = 32
    else:
        print("ERROR: VCO frequency is out of range")
        sys.exit(0)

    if f_pfd > 104 * 10**6:
        print("ERROR: REF frequency is too high")
        sys.exit(0)

    if (f_ref % f_pfd) != 0:
        print("ERROR: Reference to PFD frequency ratio has to be integer")
        sys.exit(0)

    r_cnt = int(f_ref / f_pfd)

    n_cnt = int(f_vco / f_pfd)

    for a_cnt in range(0, 63):
        for b_cnt in range(3, 8191):
            if (prslr*b_cnt + a_cnt) == n_cnt:
                return [prslr, r_cnt, a_cnt, b_cnt, n_cnt]


def adf4106_arrange_reg(r_cnt, prslr, a_cnt, b_cnt, cp_current=7,
                        pfd_polarity='positive', muxout='digital_lock_detect'):
    """ Arrange ADF4106 registers from counter's values.

    Args:
        r_cnt: R-counter value
        prslr: Prescaler value
        a_cnt: A-counter value
        b_cnt: B-counter value
        cp_current: CP current setting: 0 to 7 (default)
        pfd_polarity: PFD polarity: negative or positive (default)
        muxout: MUX output setting: three_state, digital_lock_detect (default), n_divider, dvdd, r_divider,
                open_drain_lock_detect, serial_data, dgnd

    Returns:
        List of PLL registers in decimal format - [R0, R1, R2, R3]

    Raises:
        KeyError: Raises an exception.
    """
    pll_reg_dat = []
    pll_reg_adr = []
    pll_reg = []

    for i in range(4):
        pll_reg_dat.append(0)
        pll_reg_adr.append(i)
        pll_reg.append(i)

    pll_reg_dat[0] |= 0x04 << 21  # reserved
    pll_reg_dat[0] |= 0x00 << 20  # lock detect precision
    pll_reg_dat[0] |= 0x00 << 16  # anti-backlash width = 6 ns
    pll_reg_dat[0] |= (r_cnt & 0x3FFF) << 2  # reference divider value

    pll_reg_dat[1] |= 0x03 << 22  # reserved
    pll_reg_dat[1] |= 0x00 << 21  # CP Gain bit. Is used in conjunction with "Fastlock Enable" in pll_reg[2]:9
    pll_reg_dat[1] |= (b_cnt & 0x1FFF) << 8 # 13-bit B-counter
    pll_reg_dat[1] |= (a_cnt & 0x3F) << 2 # 6-bit A-counter

    if prslr == 8:
        pll_reg_dat[2] |= 0x00 << 22
    elif prslr == 16:
        pll_reg_dat[2] |= 0x01 << 22
    elif prslr == 32:
        pll_reg_dat[2] |= 0x02 << 22
    elif prslr == 64:
        pll_reg_dat[2] |= 0x03 << 22
    else:
        print("ERROR: Prescaler value is out of range")
        sys.exit(0)  # if 0 - sucessfull exit, if > 0 - abnormal exit

    pll_reg_dat[2] |= 0x00 << 21  # disable power down
    pll_reg_dat[2] |= (cp_current & 0x07) << 18  # CP current setting 2 for fastlock mode
    pll_reg_dat[2] |= (cp_current & 0x07) << 15  # CP current setting 1 for static mode
    pll_reg_dat[2] |= (0x00 & 0x0F) << 11  # Timer counter for fastlock mode
    pll_reg_dat[2] |= (0x00 & 0x03) << 9  # Fastlock mode: 0x00 - disabled; 0x02 - mode 1; 0x03 - mode 2
    pll_reg_dat[2] |= 0x00 << 8  # CP output: 0x00 - normal operation; 0x01 - three-state

    if pfd_polarity == 'negative':
        pll_reg_dat[2] |= 0x00 << 7
    elif pfd_polarity == 'positive':
        pll_reg_dat[2] |= 0x01 << 7
    else:
        print("ERROR: Parameter <pfd_polarity> has error value")

    if muxout == 'three_state':
        pll_reg_dat[2] |= 0x00 << 4
    elif muxout == 'digital_lock_detect':
        pll_reg_dat[2] |= 0x01 << 4
    elif muxout == 'n_divider':
        pll_reg_dat[2] |= 0x02 << 4
    elif muxout == 'dvdd':
        pll_reg_dat[2] |= 0x03 << 4
    elif muxout == 'r_divider':
        pll_reg_dat[2] |= 0x04 << 4
    elif muxout == 'open_drain_lock_detect':
        pll_reg_dat[2] |= 0x05 << 4
    elif muxout == 'serial_data':
        pll_reg_dat[2] |= 0x06 << 4
    elif muxout == 'dgnd':
        pll_reg_dat[2] |= 0x07 << 4
    else:
        print("ERROR: Parameter <muxout> has error value")

    pll_reg_dat[2] |= 0x00 << 3  # disable power down
    pll_reg_dat[2] |= 0x00 << 2  # counter reset: 0x00 - normal operation; 0x01 - R-, A-, B- counters held in reset

    pll_reg_dat[3] = pll_reg_dat[2] # registers are identical

    for i in range(4):
        pll_reg[i] = pll_reg_dat[i] | pll_reg_adr[i]

    return pll_reg


def adf_4106_print_report(f_vco, f_ref, f_pfd, r_cnt, prslr, a_cnt, b_cnt, pll_reg):
    """ Print ADF4106 specific report.

    Args:
        f_vco: VCO frequency in Hz
        f_ref: Reference frequency in Hz
        f_pfd: Phase-frequency detector operating frequency in Hz
        r_cnt: R-counter value
        prslr: Prescaler value
        a_cnt: A-counter value
        b_cnt: B-counter value
        pll_reg: List of PLL registers [R0, R1, R2, R3]

    Returns:
        List of PLL registers [R0, R1, R2, R3]

    Raises:
        KeyError: Raises an exception.
    """
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'Given:')
    print('+----------------------------------------------+')
    print('VCO Frequency = ' + str(F_VCO / 10**6) + ' MHz')
    print('Ref Frequency = ' + str(F_REF / 10**6) + ' MHz')
    print('PFD Frequency = ' + str(F_PFD / 10**6) + ' MHz')
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'Counters Set:')
    print('+----------------------------------------------+')
    print('R-Divider   =   ' + str(r_divider))
    print('Prescaler   =   ' + str(prescaler))
    print('N-Divider   =   ' + str(n_divider))
    print('  A-counter =   ' + str(a_divider))
    print('  B-counter =   ' + str(b_divider))
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'PLL Registers:')
    print('+----------------------------------------------+')

    for i in range((len(pll_reg) - 1), -1, -1):
        print("R" + str(i) + ": 0x" + f"{pll_reg[i]:06X}")


# TODO
def write_pll_reg_to_serial(data):
    import serial
    import time
    # open serial port
    ser = serial.Serial('COM10', 9600, timeout=0.1)

    for i in range(3, -1, -1):
        ser_data = "$PLL 0x" + f"{data[i]:08X}"
        ser.write(ser_data.encode('utf-8'))
        print(ser_data.encode('utf-8'))
        ser_data = ser.read(32)
        print(len(ser_data))
        print(ser_data.decode('utf-8'))

    # close serial port
    if ser is not None and ser.isOpen():
        ser.close()
        ser = None


def write_pll_reg_to_file(data):

    with open(r"D:\SYNTEIRA\GitHub\STS_109_STM32_PYTHON_1\Src\ADF4159 Registers.txt", "w") as file:
        for i in range(7, -1, -1):
            file.write("0x" + f"{data[i]:08X}" + '\n')


def replace_pll_reg_in_main_c(registers_data):
    import sys
    import os
    # Here we are copying main.c file to main.c.tmp while line begining with "WriteRegSYNTH" has to be appear
    # When the line begining with "WriteRegSYNTH" has met we replace it with own REG_DAT starting from index 7 to 0
    # Las we replace main.c file with main.c.tmp and delete the last
    with open("D:\SYNTEIRA\GitHub\STS_108_STM32_PYTHON_1\Src\main.c", "r") as f1:
        with open("D:\SYNTEIRA\GitHub\STS_108_STM32_PYTHON_1\Src\main.c.tmp", "w") as f2:
            cnt = len(registers_data) -1
            string = " "
            while string != "":
                string = f1.readline()
                if "    WriteRegSYNTH(" in string:
                    string = "    WriteRegSYNTH(0x" + (f"{registers_data[cnt]:08X}")  + ");" + '\n'
                    cnt -= 1
                f2.write(string)

    os.remove("D:\SYNTEIRA\GitHub\STS_108_STM32_PYTHON_1\Src\main.c")
    os.rename(r"D:\SYNTEIRA\GitHub\STS_108_STM32_PYTHON_1\Src\main.c.tmp",
              "D:\SYNTEIRA\GitHub\STS_108_STM32_PYTHON_1\Src\main.c")


if __name__ == '__main__':

    # Unpack the list of counters values into prescaler, r_divider etc.
    prescaler, r_divider, a_divider, b_divider, n_divider = adf4106_calc_counters(F_VCO, F_REF, F_PFD)

    # Unpack the list of PLL register's data into pll_reg
    pll_reg = adf4106_arrange_reg(r_divider, prescaler, a_divider, b_divider,
                                  cp_current=CP_CURRENT,
                                  pfd_polarity=PFD_POLARITY,
                                  muxout=MUXOUT)

    adf_4106_print_report(F_VCO, F_REF, F_PFD, r_divider, prescaler, a_divider, b_divider, pll_reg)

    #    replace_pll_reg_in_main_c(pll_reg)

    #    write_pll_reg_to_file(pll_reg)

    write_pll_reg_to_serial(pll_reg)