# Encoding UTF-8

def main():
    
    F_REF = 32 * 10**6
    R_DIV = 1
    for freq in range(2390 * 10**6, 2511 * 10**6, 10**6):
        n_int, n_frac = max2831_calc(freq, F_REF/R_DIV)
        print("FREQ:", int(freq/1000000), "N-INT:", n_int, " N-FRAC:", n_frac, "N-FRAC-MSB:", n_frac >> 6, " N-FRAC-LSB:", n_frac & 0x3F)


def max2831_calc(frf, fpfd):
    nint = int(frf/fpfd)
#    nfrac = int((int(frf - fpfd * nint) << 20) / fpfd)
    nfrac = int((int(frf % fpfd) << 20) / fpfd)
#    nfrac = int((frf/fref - int(frf/fref)) * 2**20)
    return nint, nfrac

if __name__ == '__main__':

	main()