# Place S-parameters files (.s2p) to same folder
# with arinst_vna_delta_phase.py.
# In the command line enter
# python <Current Python File> <DUT1.s2p> <DUT2.s2p> ... <DUTn.s2p> Sxx

import csv
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FixedLocator, FormatStrFormatter, AutoMinorLocator)

# Set Figure Size
PLOT_SIZE_X = 12
PLOT_SIZE_Y = 9

# Set Plot 0 X axis
PLOT_0_X_MIN = 50000000  # frequency in MHz
PLOT_0_X_MAX = 500000000  # frequency in MHz
PLOT_0_X_MINOR_STEP = 50000000  # frequency in MHz
PLOT_0_X_MAJOR_STEP = 50000000  # frequency in MHz

# Set Plot 0 Y axis
PLOT_0_Y_MIN = -20
PLOT_0_Y_MAX = 0
PLOT_0_Y_MINOR_STEP = 1
PLOT_0_Y_MAJOR_STEP = 5

# Set Plot 0 Y axis
PLOT_1_Y_MIN = -180
PLOT_1_Y_MAX = 180
PLOT_1_Y_MINOR_STEP = 30
PLOT_1_Y_MAJOR_STEP = 60

# Number of lines of the Touchstone file to skip
NUM_SKIP_LINES = 6


def main():
    trc = []
    num_duts = len(sys.argv) - 1
    for i in range(num_duts):
        input_file_name = sys.argv[i + 1]
        print(input_file_name)
        trc.append(read_touchstone(input_file_name, NUM_SKIP_LINES))
    delta = phase_delta(trc[0][2], trc[1][2])
    spar_plot(trc[0][0], trc[0][1], trc[1][1], delta)
    

def read_touchstone(file, num_skip_lines):
    import numpy as np
    freq = []
    cpl = []
    mag = []
    ang = []

    with open(file, 'r', newline='') as data_file:
        reader = csv.reader(data_file, delimiter='\t')
        # skip the header
        for i in range(num_skip_lines):
            next(reader, None)    
        for f, re, im in reader:
            freq.append(int(f))
            cpl.append(complex((float(re)), (float(im))))
    mag = np.abs(cpl)
    sp = 20 * np.log10(mag)
    ang = np.angle(cpl, deg=True)

    return freq, sp, ang


def phase_delta(ang0, ang1):
    delta = []
    num = len(ang0)
    for i in range(num):
        d = ang0[i] - ang1[i]
        if d < -180:
            d += 360
        delta.append(d)
    return delta


def spar_plot(freq, s21db, s31db, phase_delta):
    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(PLOT_SIZE_X, PLOT_SIZE_Y))

    ax0.clear()

    ax0.grid(which="major", linestyle="--", color="gray", linewidth=0.5)
    ax0.grid(which="minor", linestyle="--", color="gray", linewidth=0.5)

    ax0.xaxis.set_minor_locator(FixedLocator([i for i in range(PLOT_0_X_MIN, PLOT_0_X_MAX, PLOT_0_X_MINOR_STEP)]))
    ax0.yaxis.set_major_locator(MultipleLocator(PLOT_0_Y_MAJOR_STEP))

    ax0.tick_params(which='major', length=0, width=0.5, labelsize='large')
    ax0.tick_params(which='minor', length=0, width=0.5)

    ax0.plot(freq, s21db, label="S21[dB]", color='#00008B', linewidth=2, alpha=0.75)  # RGB Color Deep Blue-Violet
    ax0.plot(freq, s31db, label="S31[dB]", color='#99004C', linewidth=2, alpha=0.75)  # RGB Color Deep Blue-Violet
    ax0.legend(loc='upper right', fontsize=14)
    ax0.set_xlim(PLOT_0_X_MIN, PLOT_0_X_MAX)
    ax0.set_ylim(PLOT_0_Y_MIN, PLOT_0_Y_MAX)

    ax0.axes.xaxis.set_ticks([])

    ax1.clear()

    ax1.grid(which="major", linestyle="--", color="gray", linewidth=0.5)
    ax1.grid(which="minor", linestyle="--", color="gray", linewidth=0.5)

    ax1.xaxis.set_minor_locator(FixedLocator([i for i in range(PLOT_0_X_MIN, PLOT_0_X_MAX, PLOT_0_X_MINOR_STEP)]))
    ax1.yaxis.set_minor_locator(MultipleLocator(PLOT_1_Y_MINOR_STEP))
    ax1.yaxis.set_major_locator(MultipleLocator(PLOT_1_Y_MAJOR_STEP))

    ax1.tick_params(which='major', length=0, width=0.5, labelsize='large')
    ax1.tick_params(which='minor', length=0, width=0.5)

    ax1.plot(freq, phase_delta, label="Phase[deg]", color='#00008B', linewidth=2, alpha=0.75)  # RGB Color Deep Blue-Violet
    ax1.legend(loc='upper right', fontsize=14)
    ax1.set_xlim(PLOT_0_X_MIN, PLOT_0_X_MAX)
    ax1.set_ylim(PLOT_1_Y_MIN, PLOT_1_Y_MAX)

    ax1.axes.xaxis.set_ticks([])

    plt.savefig(fname="phase_delta.png", format='png', dpi=300)

    plt.show()

if __name__ == '__main__':
    main()