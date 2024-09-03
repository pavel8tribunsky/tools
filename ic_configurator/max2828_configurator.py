# encoding UTF-8

def main():
    frf = 5180 * 10**6
    fref = 20 * 10**6

    # Band 0: 5180 to 5320 MHz with 20 MHz step
    int_0 = (0b11001111, 0b11010000, 0b11010000, 0b11010001, 0b11010010, 0b11010011, 0b11010100, 0b11010100)
    fmsb_0 = (0x0CCC, 0x0000, 0x3333, 0x2666, 0x1999, 0x0CCC, 0x0000, 0x3333)
    flsb_0 = (0b11, 0b00, 0b00, 0b01, 0b10, 0b11, 0b00, 0b00) 

    # Band 1: 5500 to 5700 MHz with 20 MHz step
    int_1 = (0b11011100, 0b11011100, 0b11011101, 0b11011110,\
               0b11011111, 0b11100000, 0b11100000, 0b11100001,\
               0b11100010, 0b11100011, 0b11100100)
    fmsb_1 = (0x0000, 0x3333, 0x2666, 0x1999, 0x0CCC, 0x0000,\
                    0x3333, 0x2666, 0x1999, 0x0CCC, 0x0000)
    flsb_1 = (0b00, 0b00, 0b01, 0b10, 0b11, 0b00,\
                    0b00, 0b01, 0b10, 0b11, 0b00)

    # Band 2: 5745 to 5805 MHz with 20 MHz step
    int_2 = (0b11100101, 0b11100110, 0b11100111, 0b11101000)
    fmsb_2 = (0x3333, 0x2666, 0x1999, 0x0CCC)
    flsb_2 = (0b00, 0b01, 0b10, 0b11)

    fpfd = fref / max2828_calc_rdiv(fref)

    # From 5180 MHz to 5320 MHz
    print("-----")
    for i in range(8):
        f_rf = frf + i * 20 * 10**6
        n_int, frac_msb, frac_lsb = max2828_calc_ndiv(f_rf, fpfd)
        print("Freq:", f_rf, "Intg delta:", (int_0[i] - n_int),\
                             "Frac delta:", (fmsb_0[i] - frac_msb),\
                             "Frac delta:", (flsb_0[i] - frac_lsb))

    # From 5500 MHz to 5700 MHz
    print("-----")
    frf = 5500 * 10**6
    for i in range(11):
        f_rf = frf + i * 20 * 10**6
        n_int, frac_msb, frac_lsb = max2828_calc_ndiv(f_rf, fpfd)
        print("Freq:", f_rf, "Intg delta:", (int_1[i] - n_int),\
                             "Frac delta:", (fmsb_1[i] - frac_msb),\
                             "Frac delta:", (flsb_1[i] - frac_lsb))

    # From 5745 MHz to 5805 MHz
    print("-----")
    frf = 5745 * 10**6
    for i in range(4):
        f_rf = frf + i * 20 * 10**6
        n_int, frac_msb, frac_lsb = max2828_calc_ndiv(f_rf, fpfd)
        print("Freq:", f_rf, "Intg delta:", (int_2[i] - n_int),\
                             "Frac delta:", (fmsb_2[i] - frac_msb),\
                             "Frac delta:", (flsb_2[i] - frac_lsb))


def max2828_calc_ndiv(f_rf, f_pfd):
    f_vco = (f_rf << 2) / 5
    n_int = int(f_vco / f_pfd)
    n_frac = int((int(f_vco % f_pfd) << 16) / f_pfd)
    n_frac_lsb = n_frac & 0x03
    n_frac_msb = n_frac >> 2
    return  n_int, n_frac_msb, n_frac_lsb


def max2828_calc_rdiv(f_ref):
    r_div = 0
    if f_ref <= 20000000:
        r_div = 1
    else:
        r_div = 2
    print("R-counter:", r_div)
    return r_div


if __name__ == '__main__':

	main()