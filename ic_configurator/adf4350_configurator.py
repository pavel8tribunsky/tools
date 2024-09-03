import math
import sys
from colorama import Fore, Back, Style
from colorama import init
init(autoreset=True)

F_REF = 40 * 10**6  # enter reference frequency in Hz here
F_OUT = 335 * 10**6  # enter input frequency in Hz here
F_STEP = 200 * 10**3 # enter frequency step in Hz here

pll_mode = 'auto'  # PLL operation mode: auto; integer; fractional

MUXOUT_MODE = 'digital_lock_detect'  # available modes: three_state; dvdd; dgnd; r_divider; n_divider; analog_lock_detect; digital_lock_detect
LD_PIN_MODE = 'digital_lock_detect'  # lock detect pin mode: low; digital_lock_detect; high

cp_current = 5 # Charge pump current: 0 to 15
cp_three_state = 'disabled' # available modes: disabled; enabled

mode = 'low_noise'  # modes available: low_noise; low_spur
csr = 'disabled'  # cycle slip reduction: disabled; enabled
power_down = 'disabled'  # available modes: disabled; enabled
vco_mute = 'disabled'  # available modes: disabled; enabled
vco_powerdown = 'disabled'  # available modes: disabled; enabled
out_a_pout = 2  # power at the Output A in dBm: -4; -1; 2; 5
out_b_pout = 2  # power at the Output B in dBm: -4; -1; 2; 5
out_a_en = 'enabled'  # available modes: disabled; enabled
out_b_en = 'disabled'  # available modes: disabled; enabled
out_b_select = 'divided'  # AUX output mode select: divided; fundamental
pfd_polarity = 'positive'  # polarity of the phase-frequency detector: negative; positive
clk_div_mode = 'disabled'  # clock divider mode: disabled; fast_lock; resync
clk_div_value = 0  # clock divider value
ld_precision = '400ns'  # lock detect precision: 60ns; 400ns
counter_reset = 'disabled'  # n- and r- counters reset: disabled; enabled
fb_select = 'fundamental'  # Feedback mode select: divided; fundamental


def adf4350_calc_counters(f_out, f_ref, f_step, pll_mode='auto'):
    """ Calculates values of prescaler and R-, INT-, FRAC-, MOD- counters of ADF4350 and returns P-R-I-F-M.

    Args:
        f_out: output frequency in Hz
        f_ref: Reference frequency in Hz
        pll_mode: auto; integer; fractional

    Returns:
        List of [prescaler, R-counter, INT-counter, FRAC-counter, MOD-counter]
    Raises:
        KeyError: Raises an exception.
    """

    # ADF4350-specific constants
    F_PFD_MAX = 32 * 10 ** 6  # maximum PFD frequency
    F_VCO = (2200 * 10 ** 6, 4400 * 10 ** 6)  # integrated VCO minimum and maximum frequency
    DIV_OUT = (1, 2, 4, 8, 16)  # available division factor between VCO and output stage

    # define output divider value
    out_div = 0
    for output_divider in DIV_OUT:
        if (min(F_VCO))/output_divider <= f_out <= (max(F_VCO))/output_divider:
            out_div = output_divider
    if out_div == 0:
        print("ERROR: output frequency is out of range")
        sys.exit(0)

    f_vco = f_out*out_div
    # define preescaler value
    if f_vco < 3 * 10**9:
        prslr = 4
    else:
        prslr = 8

    r_dbl = 0
    r_cnt = 0
    r_hlf = 0

    f_pfd = 0

    n_int = 0
    n_frac = 0
    n_mod = 0

    if f_ref <= 30 * 10**6: # reference doubler maximum output frequency is limited by 60 MHz
        r_dbl = 1
        for r in range(1, 1023):
            f_pfd = f_ref * (1 + r_dbl) / (r * (1 + r_hlf))
            if f_pfd <= F_PFD_MAX:
                if r != 2:
                    if f_pfd > f_ref:
                        r_cnt = r
                        break
    if r_cnt == 0:
        r_dbl = 0
        for r in range(1, 1023):
            f_pfd = f_ref * (1 + r_dbl) / (r * (1 + r_hlf))
            if f_pfd <= F_PFD_MAX:
                    r_cnt = r
                    break

    if (pll_mode == 'auto') or (pll_mode == 'fractional'):
        n_cnt = f_vco / f_pfd
    elif (pll_mode == 'integer'):
        if (f_vco % f_pfd != 0):
            print("ERROR: VCO to PFD frequency ratio has to be integer")
            sys.exit(0)
        pass
    n_int = int(n_cnt)
    n_mod = int(f_pfd / (out_div * f_step))
    for i in range(3):
        if ((n_mod + i) % 2 == 0):
            pass
        elif ((n_mod + i) % 3 == 0):
            pass
        elif ((n_mod + i) % 6 == 0):
            pass
        else:
            n_mod += i
            break

    f_resolution = f_pfd / (out_div * n_mod)

    n_frac = int((n_cnt - n_int) * n_mod)

    if (n_frac > (n_mod - 1)):
        print("ERROR: FRAC value couldn't exceed MOD-1 value")
        sys.exit(0)

    f_out = (n_int + n_frac/n_mod) * f_pfd / out_div

    print('Required output frequency:  ', f_out/10**6, 'MHz')
    print('Required frequency step:    ', f_step/10**3, 'kHz')
    print('Calculated output frequency:', f_out/10**6, 'MHz')
    print('Calculated frequency step:  ', f_resolution/10**3, 'kHz')

    print('Prescaler:', prslr)
    print('Reference Doubler', r_dbl)
    print('Reference Divider:', r_cnt)
    print('Reference Div2:', r_hlf)
    print('INT:', n_int)
    print('FRAC:', n_frac)
    print('MOD:', n_mod)
    print('RF Divider:', out_div)

    return [prslr, r_dbl, r_cnt, r_hlf, n_int, n_frac, n_mod, out_div]


def adf4350_arrange_reg(f_ref, prslr, r_dbl, r_cnt, r_hlf, n_int, n_frac, n_mod, out_div, phase=0, cp_current=7,
                        ld_pin_mode='digital_lock_detect', ld_precision = '10ns', pfd_polarity='positive',
                        muxout='digital_lock_detect'):
    """ Arrange ADF4106 registers from counter's values.

    Args:
        f_ref: reference frequency in Hz
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

    for i in range(6):
        pll_reg_dat.append(0)
        pll_reg_adr.append(i)
        pll_reg.append(i)

    pll_reg_dat[0] &= 0x00 << 31  # reserved
    pll_reg_dat[0] |= (n_int & 0xFFFF) << 15  # 16-bit integer portion of main divider
    pll_reg_dat[0] |= (n_frac & 0xFFF) << 3  # 12-bit FRAC value of fractional portion of main divider

    pll_reg_dat[1] |= 0x00 << 28  # reserved

    if prslr == 4:
        pass
    elif prslr == 8:
        pll_reg_dat[1] |= 0x01 << 27
    else:
        print("ERROR: Prescaler value is out of range")
        sys.exit(0)

    pll_reg_dat[1] |= (phase & 0xFFF) << 15  # 12-bit phase value
    pll_reg_dat[1] |= (n_mod & 0xFFF) << 3  # 12-bit MOD value of fractional portion of main divider

    pll_reg_dat[2] &= 0x00 << 31  # reserved

    if mode == 'low_noise':
        pass
    elif muxout == 'low_spur':
        pll_reg_dat[2] |= 0x03 << 29
    else:
        print("ERROR: Parameter <mode> has error value")

    if muxout == 'three_state':
        pass
    elif muxout == 'dvdd':
        pll_reg_dat[2] |= 0x01 << 26
    elif muxout == 'dgnd':
        pll_reg_dat[2] |= 0x02 << 26
    elif muxout == 'r_divider':
        pll_reg_dat[2] |= 0x03 << 26
    elif muxout == 'n_divider':
        pll_reg_dat[2] |= 0x04 << 26
    elif muxout == 'analog_lock_detect':
        pll_reg_dat[2] |= 0x05 << 26
    elif muxout == 'digital_lock_detect':
        pll_reg_dat[2] |= 0x06 << 26
    else:
        print("ERROR: Parameter <muxout> has error value")

    pll_reg_dat[2] |= r_dbl << 25
    pll_reg_dat[2] |= r_hlf << 24
    pll_reg_dat[2] |= (r_cnt & 0xFFFF) << 14
    pll_reg_dat[2] |= 0x01 << 13 # double bufferization of R4 DB22-DB20: 0 - disable; 1 - enable
    pll_reg_dat[2] |= (cp_current & 0x0F) << 9

    if n_frac == 0:
        pll_reg_dat[2] |= 0x01 << 8

    if ld_precision == '10ns':
        pass
    elif ld_precision == '6ns':
        pll_reg_dat[2] |= 0x01 << 7
    else:
        print("ERROR: Lock detect precision has error value")
        sys.exit(0)

    if pfd_polarity == 'negative':
        pass
    elif pfd_polarity == 'positive':
        pll_reg_dat[2] |= 0x01 << 6
    else:
        print("ERROR: PFD polarity has error value")
        sys.exit(0)

    if power_down == 'disabled':
        pass
    elif power_down == 'enabled':
        pll_reg_dat[2] |= 0x01 << 5
    else:
        print("ERROR: Power down enable has error value")
        sys.exit(0)

    if cp_three_state == 'disabled':
        pass
    elif cp_three_state == 'enabled':
        pll_reg_dat[2] |= 0x01 << 4
    else:
        print("ERROR: CP 3-state enable has error value")
        sys.exit(0)

    if counter_reset == 'disabled':
        pass
    elif counter_reset == 'enabled':
        pll_reg_dat[2] |= 0x01 << 3
    else:
        print("ERROR: Counter reset has error value")
        sys.exit(0)

    pll_reg_dat[3] &= 0x00 << 19  # reserved

    if csr == 'disabled':
        pass
    elif csr == 'enabled':
        pll_reg_dat[3] |= 0x01 << 18
    else:
        print("ERROR: Cycle slip reduction has error value")
        sys.exit(0)

    pll_reg_dat[3] &= 0x00 << 17  # reserved

    if clk_div_mode == 'disabled':
        pass
    elif csr == 'fast_lock':
        pll_reg_dat[3] |= 0x01 << 15
    elif csr == 'resync':
        pll_reg_dat[3] |= 0x02 << 15
    else:
        print("ERROR: Clock divider mode has error value")
        sys.exit(0)

    pll_reg_dat[3] |= (clk_div_value & 0xFFF) << 15

    pll_reg_dat[4] &= 0x00 << 24  # reserved

    if fb_select == 'divided':
        pass
    elif fb_select == 'fundamental':
        pll_reg_dat[4] |= 0x01 << 23
    else:
        print("ERROR: Feedback select has error value")
        sys.exit(0)

    if out_div == 1:
        pass
    elif out_div == 2:
        pll_reg_dat[4] |= 0x01 << 20
    elif out_div == 4:
        pll_reg_dat[4] |= 0x02 << 20
    elif out_div == 8:
        pll_reg_dat[4] |= 0x03 << 20
    elif out_div == 16:
        pll_reg_dat[4] |= 0x04 << 20
    else:
        print("ERROR: RF divider value is out of range")
        sys.exit(0)

    F_BAND_SELECT_MAX = 125 * 10**3
    bs_div = int(f_ref * ((1 + r_dbl)/(r_cnt*(1+r_hlf))) / F_BAND_SELECT_MAX)
    pll_reg_dat[4] |= (bs_div & 0xFF) << 12

    if vco_powerdown == 'disabled':
        pass
    elif vco_powerdown == 'enabled':
        pll_reg_dat[4] |= 0x01 << 11
    else:
        print("ERROR: VCO power down has error value")
        sys.exit(0)

    if vco_mute == 'disabled':
        pass
    elif vco_mute == 'enabled':
        pll_reg_dat[4] |= 0x01 << 10
    else:
        print("ERROR: VCO mute till lock detect has error value")
        sys.exit(0)

    if out_b_select == 'divided':
        pass
    elif out_b_select == 'fundamental':
        pll_reg_dat[4] |= 0x01 << 9
    else:
        print("ERROR: AUX out mode select has error value")
        sys.exit(0)

    if out_b_en == 'disabled':
        pass
    elif out_b_en == 'enabled':
        pll_reg_dat[4] |= 0x01 << 8
    else:
        print("ERROR: AUX out mode select has error value")
        sys.exit(0)

    if out_b_pout == -4:
        pass
    elif out_b_pout == -1:
        pll_reg_dat[4] |= 0x01 << 6
    elif out_b_pout == 2:
        pll_reg_dat[4] |= 0x02 << 6
    elif out_b_pout == 5:
        pll_reg_dat[4] |= 0x03 << 6
    else:
        print("ERROR: AUX output power is out of range")
        sys.exit(0)

    if out_a_en == 'disabled':
        pass
    elif out_a_en == 'enabled':
        pll_reg_dat[4] |= 0x01 << 5
    else:
        print("ERROR: AUX out mode select has error value")
        sys.exit(0)

    if out_a_pout == -4:
        pass
    elif out_a_pout == -1:
        pll_reg_dat[4] |= 0x01 << 3
    elif out_a_pout == 2:
        pll_reg_dat[4] |= 0x02 << 3
    elif out_a_pout == 5:
        pll_reg_dat[4] |= 0x03 << 3
    else:
        print("ERROR: Output power is out of range")
        sys.exit(0)

    pll_reg_dat[5] &= 0x00 << 24  # reserved

    if ld_pin_mode == 'low':
        pass
    elif ld_pin_mode == 'digital_lock_detect':
        pll_reg_dat[5] |= 0x01 << 22
    elif ld_pin_mode == 'high':
        pll_reg_dat[5] |= 0x03 << 22
    else:
        print("ERROR: Lock detect pin mode has error value")

    pll_reg_dat[5] |= 0x03 << 19

    # TODO: last edit point

    for i in range(6):
        pll_reg[i] = pll_reg_dat[i] | pll_reg_adr[i]
        print("R" + str(i) + ": 0x" + f"{pll_reg[i]:06X}")

    return pll_reg


def adf_4350_print_report(f_vco, f_ref, f_pfd, r_cnt, prslr, a_cnt, b_cnt, pll_reg):
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
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'Given:')
    print('+----------------------------------------------+')
    print('VCO Frequency = ' + str(f_vco / 10**6) + ' MHz')
    print('Ref Frequency = ' + str(f_ref / 10**6) + ' MHz')
    print('PFD Frequency = ' + str(f_pfd / 10**6) + ' MHz')
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
        print("R" + str(i) + ": 0x" + f"{pll_reg[i]:08X}")


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
    #     prescaler, r_divider, int_divider, frac_divider, mod_divider = adf4350_calc_counters(F_OUT, F_REF)
    prslr, r_dbl, r_cnt, r_hlf, n_int, n_frac, n_mod, out_div = adf4350_calc_counters(F_OUT, F_REF, F_STEP)
    pll_registers = adf4350_arrange_reg(prslr, r_dbl, r_cnt, r_hlf, n_int, n_frac, n_mod, out_div,
                                        ld_pin_mode=LD_PIN_MODE, muxout=MUXOUT_MODE)

    #print (prescaler, r_divider, int_divider, frac_divider, mod_divider)

    # # Unpack the list of PLL register's data into pll_reg
    # pll_reg = adf4106_arrange_reg(r_divider, prescaler, a_divider, b_divider,
    #                               cp_current=7,
    #                               pfd_polarity='positive',
    #                               muxout='digital_lock_detect')
    #
    # adf_4106_print_report(F_VCO, F_REF, F_PFD, r_divider, prescaler, a_divider, b_divider, pll_reg)
    #
    # #    replace_pll_reg_in_main_c(pll_reg)
    #
    # #    write_pll_reg_to_file(pll_reg)
    #
    # write_pll_reg_to_serial(pll_reg)