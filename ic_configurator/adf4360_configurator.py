import math
import sys
from colorama import Fore, Back, Style
from colorama import init

init(autoreset=True)

# ADF4360-7 PLL configurator

F_REF = 40 * 10 ** 6  # enter reference frequency in Hz here
F_OUT = 646 * 10 ** 6  # enter input frequency in Hz here
F_STEP = 5 * 10 ** 6  # enter frequency step in Hz here

MUXOUT_MODE = 'digital_lock_detect'  # available modes: three_state; digital_lock_detect; n_divider; dvdd; r_divider; analog_lock_detect; serial_data_out; dgnd
# dvdd; r_divider; analog_lock_detect; serial_data_out; dgnd

CP_CURRENT_1 = 7  # Charge pump current: 0 to 7
CP_CURRENT_2 = 7  # Charge pump current: 0 to 7
CP_GAIN = 1  # Charge pump current setting: 1; 2
CP_THREE_STATE = 'disabled'  # available modes: disabled; enabled

CORE_PWR_LVL = '5mA'  # core power level: 5mA; 10mA; 15mA; 20mA

POWER_DOWN = 'disabled'  # available modes: disabled; asynchronous; synchronous
MTLD = 'disabled'  # mute till lock detect: disabled; enabled
POUT = -14  # power at the output in dBm: -14; -11; -8; -5
PFD_POLARITY = 'positive'  # polarity of the phase-frequency detector: negative; positive
DIV2 = 'disabled'  # available modes: disabled; enabled
LD_PRECISION = '3 cycles'  # lock detect precision: 3 cycles; 5 cycles
COUNTER_RESET = 'disabled'  # n- and r- counters reset: disabled; enabled
ABPW = '3.0 ns'  # anti-backlash pulse width: 1.3 ns; 3.0 ns; 6.0 ns


def adf4360_calc_counters(f_out, f_ref, f_step):
    """ Calculates values of prescaler and R-, INT-, FRAC-, MOD- counters of ADF4350 and returns P-R-I-F-M.

    Args:
        f_out: output frequency in Hz
        f_ref: reference frequency in Hz
        f_step: frequency step in Hz

    Returns:
        List of [prescaler, R-counter, INT-counter, FRAC-counter, MOD-counter]
    Raises:
        KeyError: Raises an exception.
    """

    # ADF4650-specific constants
    F_PFD_MAX = 8 * 10 ** 6  # maximum PFD frequency
    F_VCO = (350 * 10 ** 6, 1800 * 10 ** 6)  # integrated VCO minimum and maximum frequency
    PSC = (8, 16, 32)  # available prescaler value
    F_PCS_MAX = 300 * 10 ** 6
    N_B_CNT = (3, 8191)

    if (f_out < F_VCO[0]) or (f_out > F_VCO[1]):
        print("ERROR: unable to set required output frequency")
        sys.exit(0)

    f_pfd = f_step

    if (f_ref % f_pfd != 0) or (f_pfd > F_PFD_MAX):
        r_cnt_min = int(f_ref / F_PFD_MAX) + 1
        f_step_max = f_ref / r_cnt_min
        print("ERROR: unable to set required frequency step. Maximum frequency step is", f_step_max / 10 ** 6, "MHz.")
        sys.exit(0)

    psc = 0
    for p in PSC:
        if (f_out / p <= F_PCS_MAX):
            psc = p
            break

    if (psc == 0):
        print("ERROR: prescaler is out of range")
        sys.exit(0)

    n_total = int(f_out / f_pfd)

    r_cnt = int(F_REF / f_pfd)

    n_cnt_b = int(n_total / psc)

    n_cnt_a = n_total - psc * n_cnt_b

    div_bsc = 8

    for i in (1, 2, 4, 8):
        if f_pfd / i <= 10 ** 6:
            div_bsc = i
        else:
            pass

    # print report
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'Given:')
    print('+----------------------------------------------+')
    print('VCO Frequency = ' + str(f_out / 10 ** 6) + ' MHz')
    print('Ref Frequency = ' + str(f_ref / 10 ** 6) + ' MHz')
    print('PFD Frequency = ' + str(f_pfd / 10 ** 6) + ' MHz')
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'Counters Set:')
    print('+----------------------------------------------+')
    print('R-Divider   =   ' + str(r_cnt))
    print('Prescaler   =   ' + str(psc))
    print('N-Divider   =   ' + str(n_total))
    print('  A-counter =   ' + str(n_cnt_a))
    print('  B-counter =   ' + str(n_cnt_b))

    return [psc, r_cnt, n_cnt_a, n_cnt_b, div_bsc]


def adf4360_arrange_reg(psc, r_cnt, n_cnt_a, n_cnt_b, div_bsc, cp_current_1=7, cp_current_2=7,
                        pout=-14, cp_gain=1, cp_three_state='disabled', pfd_polarity='positive',
                        power_down='disabled', mtld='disabled', muxout_mode='digital_lock_detect',
                        counter_reset='disabled', core_pwr_lvl='5mA', div2='disabled',
                        ld_precision='3 cycles', abpw='3.0 ns'):
    """ Arrange ADF4360 registers from counter's values.

    Args:
        psc: prescaler value
        r_cnt: R-counter value
        n_cnt_a: A-counter value
        n_cnt_b: B-counter value
        div_bsc: band select clock divider value
        cp_current_1: CP current setting 1 (0 to 7)
        cp_current_2: CP current setting 2 (0 to 7)
        pout: RF output power in dBm (-14; -11; -8; -5)
        cp_gain: using of cp_current setting (1; 2)
        cp_three_state: CP three state ('disabled'; 'enabled')
        pfd_polarity: PFD polarity ('negative'; 'positive')
        power_down: power down mode ('disabled'; 'asynchronous'; 'synchronous')
        mtld: mute till lock detect ('disabled'; 'enabled')
        muxout_mode: MUX output setting: three_state, digital_lock_detect (default), n_divider, dvdd, r_divider,
                open_drain_lock_detect, serial_data, dgnd
        counter_reset: holding all counters R-, A-, B- in reset state ('disabled'; 'enabled')
        core_pwr_lvl: core power level (5mA; 10mA; 15mA; 20mA)
        div2: Divide-by-2 prescaler predivider setting  ('disabled'; 'enabled')
        ld_precision: Lock detector precision setting ('3 cycles'; '5 cycles')
        abpw: Anti-backlash pulse width ('1.3 ns'; '3.0 ns'; '6.0 ns')

    Returns:
        List of PLL registers in decimal format - [R0, R1, R2]

    Raises:
        KeyError: Raises an exception.
    """
    pll_reg_dat = []
    pll_reg_adr = []
    pll_reg = []

    for i in range(3):
        pll_reg_dat.append(0)
        pll_reg_adr.append(i)
        pll_reg.append(i)

    if psc == 8:
        pass
    elif psc == 16:
        pll_reg_dat[0] |= 0x01 << 22
    elif psc == 32:
        pll_reg_dat[0] |= 0x01 << 22
    else:
        print("ERROR: Prescaler value is out of range")
        sys.exit(0)

    if power_down == 'disabled':
        pass
    elif power_down == 'asynchronous':
        pll_reg_dat[0] |= 0x01 << 20
    elif power_down == 'synchronous':
        pll_reg_dat[0] |= 0x02 << 20
    else:
        print("ERROR: Prescaler value is out of range")
        sys.exit(0)

    if (cp_current_2 >= 0) and (cp_current_2 <= 7):
            pll_reg_dat[0] |= cp_current_2 << 17
    else:
        print("ERROR: CP current setting 2 is out of range")
        sys.exit(0)

    if (cp_current_1 >= 0) and (cp_current_1 <= 7):
        pll_reg_dat[0] |= cp_current_1 << 14
    else:
        print("ERROR: CP current setting 1 is out of range")
        sys.exit(0)

    if pout == -14:
        pass
    elif pout == -11:
        pll_reg_dat[0] |= 0x01 << 12
    elif pout == -8:
        pll_reg_dat[0] |= 0x02 << 12
    elif pout == -5:
        pll_reg_dat[0] |= 0x03 << 12
    else:
        print("ERROR: output power is out of range")
        sys.exit(0)

    if mtld == 'disabled':
        pass
    elif mtld == 'enabled':
        pll_reg_dat[0] |= 0x01 << 11
    else:
        print("ERROR: Mute till lock detect setting has error")
        sys.exit(0)

    if 1 <= cp_gain <= 2:
        pll_reg_dat[0] |= (cp_gain - 1) << 10
    else:
        print("ERROR: CP gain value is out of range")
        sys.exit(0)

    if cp_three_state == 'disabled':
        pass
    elif cp_three_state == 'enabled':
        pll_reg_dat[0] |= 0x01 << 9
    else:
        print("ERROR: CP three state setting has error")
        sys.exit(0)

    if pfd_polarity == 'negative':
        pass
    elif pfd_polarity == 'positive':
        pll_reg_dat[0] |= 0x01 << 8
    else:
        print("ERROR: PFD polarity setting has error")
        sys.exit(0)

    if muxout_mode == 'three_state':
        pass
    elif muxout_mode == 'digital_lock_detect':
        pll_reg_dat[0] |= 0x01 << 5
    elif muxout_mode == 'n_divider':
        pll_reg_dat[0] |= 0x02 << 5
    elif muxout_mode == 'dvdd':
        pll_reg_dat[0] |= 0x03 << 5
    elif muxout_mode == 'r_divider':
        pll_reg_dat[0] |= 0x04 << 5
    elif muxout_mode == 'analog_lock_detect':
        pll_reg_dat[0] |= 0x05 << 5
    elif muxout_mode == 'serial_data_out':
        pll_reg_dat[0] |= 0x06 << 5
    elif muxout_mode == 'dgnd':
        pll_reg_dat[0] |= 0x07 << 5
    else:
        print("ERROR: Muxout mode setting has error")
        sys.exit(0)

    if counter_reset == 'disabled':
        pass
    elif counter_reset == 'enabled':
        pll_reg_dat[0] |= 0x01 << 4
    else:
        print("ERROR: Counters reset setting has error")
        sys.exit(0)

    if core_pwr_lvl == '5mA':
        pass
    elif core_pwr_lvl == '10mA':
        pll_reg_dat[0] |= 0x01 << 2
    elif core_pwr_lvl == '15mA':
        pll_reg_dat[0] |= 0x02 << 2
    elif core_pwr_lvl == '20mA':
        pll_reg_dat[0] |= 0x03 << 2
    else:
        print("ERROR: Core power level setting has error")
        sys.exit(0)

    if div2 == 'disabled':
        pass
    elif div2 == 'enabled':
        pll_reg_dat[2] |= 0x03 << 22
    else:
        print("ERROR: Divide-by-2 prescaler predivider setting has error")
        sys.exit(0)

    # R counter latch

    if div_bsc == 1:
        pass
    elif div_bsc == 2:
        pll_reg_dat[1] |= 0x01 << 20
    elif div_bsc == 4:
        pll_reg_dat[1] |= 0x02 << 20
    elif div_bsc == 8:
        pll_reg_dat[1] |= 0x03 << 20
    else:
        print("ERROR: Band select clock divider value is out of range")
        sys.exit(0)

    if ld_precision == '3 cycles':
        pass
    elif ld_precision == '5 cycles':
        pll_reg_dat[2] |= 0x01 << 18
    else:
        print("ERROR: Lock detector precision setting has error")
        sys.exit(0)

    if abpw == '3.0 ns':
        pass
    elif abpw == '1.3 ns':
        pll_reg_dat[2] |= 0x01 << 16
    elif abpw == '6.0 ns':
        pll_reg_dat[2] |= 0x02 << 16
    else:
        print("ERROR: Anti-backlash pulse width value is out of range")
        sys.exit(0)

    pll_reg_dat[1] |= (r_cnt & 0x3FFF) << 2

    # N counter latch

    if 1 <= cp_gain <= 2:
        pll_reg_dat[2] |= (cp_gain - 1) << 21
    else:
        print("ERROR: CP gain value is out of range")
        sys.exit(0)

    pll_reg_dat[2] |= (n_cnt_b & 0x1FFF) << 8
    pll_reg_dat[2] |= (n_cnt_a & 0x1F) << 2

    for i in range(3):
        pll_reg[i] = pll_reg_dat[i] | pll_reg_adr[i]

    # print report
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'PLL Registers:')
    print('+----------------------------------------------+')
    for i in range((len(pll_reg) - 1), -1, -1):
        print("R" + str(i) + ": 0x" + f"{pll_reg[i]:06X}")

    return pll_reg


def adf_4360_print_report(f_vco, f_ref, f_pfd, r_cnt, prslr, a_cnt, b_cnt, pll_reg):
    """ Print ADF4350 specific report.

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
    # print(' ')
    # print(Fore.CYAN + Style.BRIGHT + 'Given:')
    # print('+----------------------------------------------+')
    # print('VCO Frequency = ' + str(F_VCO / 10**6) + ' MHz')
    # print('Ref Frequency = ' + str(F_REF / 10**6) + ' MHz')
    # print('PFD Frequency = ' + str(F_PFD / 10**6) + ' MHz')
    # print(' ')
    # print(Fore.CYAN + Style.BRIGHT + 'Counters Set:')
    # print('+----------------------------------------------+')
    # print('R-Divider   =   ' + str(r_divider))
    # print('Prescaler   =   ' + str(prescaler))
    # print('N-Divider   =   ' + str(n_divider))
    # print('  A-counter =   ' + str(a_divider))
    # print('  B-counter =   ' + str(b_divider))
    # print(' ')
    # print(Fore.CYAN + Style.BRIGHT + 'PLL Registers:')
    # print('+----------------------------------------------+')
    #
    # for i in range((len(pll_reg) - 1), -1, -1):
    #     print("R" + str(i) + ": 0x" + f"{pll_reg[i]:06X}")


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
            cnt = len(registers_data) - 1
            string = " "
            while string != "":
                string = f1.readline()
                if "    WriteRegSYNTH(" in string:
                    string = "    WriteRegSYNTH(0x" + (f"{registers_data[cnt]:08X}") + ");" + '\n'
                    cnt -= 1
                f2.write(string)

    os.remove("D:\SYNTEIRA\GitHub\STS_108_STM32_PYTHON_1\Src\main.c")
    os.rename(r"D:\SYNTEIRA\GitHub\STS_108_STM32_PYTHON_1\Src\main.c.tmp",
              "D:\SYNTEIRA\GitHub\STS_108_STM32_PYTHON_1\Src\main.c")


if __name__ == '__main__':
    # Unpack the list of counters values into prescaler, r_divider etc.
    psc, r_cnt, n_cnt_a, n_cnt_b, div_bsc = adf4360_calc_counters(F_OUT, F_REF, F_STEP)

    # Unpack the list of PLL register's data into pll_reg
    pll_reg = adf4360_arrange_reg(psc, r_cnt, n_cnt_a, n_cnt_b, div_bsc,
                                  cp_current_1=CP_CURRENT_1,
                                  cp_current_2=CP_CURRENT_2,
                                  pout=POUT,
                                  cp_gain=CP_GAIN,
                                  cp_three_state=CP_THREE_STATE,
                                  pfd_polarity=PFD_POLARITY,
                                  power_down=POWER_DOWN,
                                  mtld=MTLD,
                                  muxout_mode=MUXOUT_MODE,
                                  counter_reset=COUNTER_RESET,
                                  core_pwr_lvl=CORE_PWR_LVL,
                                  div2=DIV2,
                                  ld_precision=LD_PRECISION,
                                  abpw=ABPW)
    #
    # adf_4106_print_report(F_VCO, F_REF, F_PFD, r_divider, prescaler, a_divider, b_divider, pll_reg)
    #
    # #    replace_pll_reg_in_main_c(pll_reg)
    #
    # #    write_pll_reg_to_file(pll_reg)
    #
    # write_pll_reg_to_serial(pll_reg)
