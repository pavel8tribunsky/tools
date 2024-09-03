# Place S-parameters files (.s2p) to same folder
# as s_parameters_viewer_multiple_dut.py.
# In the command line enter
# python <Current Python File> <DUT1.s2p> <DUT2.s2p> ... <DUTn.s2p> Sxx

import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator)
import os.path
import sys

# To-Do list
# 1. read and decode Touchstone preamble
# for frequency units, and number of model ports
# 2. for *.s1p plot 2 traces only
# 3. make able to read plot limits from command line sys.args 
# 4. make able to read command line sys.args for s-parameters to plot

# Settings
NUM_SAMPLES = 256
NUM_AVG = 16

# Set Figure Size
PLOT_SIZE_X = 6
PLOT_SIZE_Y = 4

# Set Plot 0 X axis
PLOT_0_X_MIN = 0  # frequency in MHz
PLOT_0_X_MAX = 500  # frequency in MHz
PLOT_0_X_MINOR_STEP = 25  # frequency in MHz
PLOT_0_X_MAJOR_STEP = 100  # frequency in MHz

# Set Plot 0 Y axis
PLOT_0_Y_MIN = -50
PLOT_0_Y_MAX = 0
PLOT_0_Y_MINOR_STEP = 5
PLOT_0_Y_MAJOR_STEP = 10

# Number of lines of the Touchstone file to skip
NUM_SKIP_LINES = 5

# Variables statement
num_duts = 0
x = []
fig, (ax0) = plt.subplots(1, 1,
                          figsize=(PLOT_SIZE_X, PLOT_SIZE_Y),
                          constrained_layout=True)

frequency = []
s11_db = []
s11_ang = []
s21_db = []
s21_ang = []
s12_db = []
s12_ang = []
s22_db = []
s22_ang = []


def read_touchstone(input_file_name):

    # open reference data file for reading
    input_file = open(input_file_name, 'r', newline='')
    reader = csv.reader(input_file, delimiter=' ')

    # skip the header
    for i in range(NUM_SKIP_LINES):
        next(reader, None)

    # S-parameters data acquisition
    for frequency_,\
        s11_db_, s11_ang_, \
        s21_db_, s21_ang_, \
        s12_db_, s12_ang_, \
        s22_db_, s22_ang_, \
            in reader:
        frequency.append(int((float(frequency_)/10**6)))
        s11_db.append(float(s11_db_))
        s11_ang.append(float(s11_ang_))
        s21_db.append(float(s21_db_))
        s21_ang.append(float(s21_ang_))
        s12_db.append(float(s12_db_))
        s12_ang.append(float(s12_ang_))
        s22_db.append(float(s22_db_))
        s22_ang.append(float(s22_ang_))

    # close csv-file
    input_file.close()


def clear_variables():
    frequency.clear()
    s11_db.clear()
    s11_ang.clear()
    s21_db.clear()
    s21_ang.clear()
    s12_db.clear()
    s12_ang.clear()
    s22_db.clear()
    s22_ang.clear()


def plot_data(num_duts):

    # Plot FFT Spectrum
    ax0.clear()
    ax0.set_xlabel("Frequency [MHz]", fontsize=14)
    ax0.set_ylabel("Amplitude [dB]", fontsize=14)
    ax0.grid(which="major", linewidth=1.2)
    ax0.grid(which="minor", linestyle="--", color="gray", linewidth=0.5)
    ax0.xaxis.set_minor_locator(MultipleLocator(PLOT_0_X_MINOR_STEP))
    ax0.xaxis.set_major_locator(MultipleLocator(PLOT_0_X_MAJOR_STEP))
    ax0.yaxis.set_minor_locator(MultipleLocator(PLOT_0_Y_MINOR_STEP))
    ax0.yaxis.set_major_locator(MultipleLocator(PLOT_0_Y_MAJOR_STEP))
    ax0.tick_params(which='major', length=10, width=2)
    ax0.tick_params(which='minor', length=5, width=1)

    for i in range(num_duts):

        input_file_name = sys.argv[i + 1]

        read_touchstone(input_file_name)

        trace_color = ('#0000CC', '#C00000', '#00805C', '#DAA520', '#99004C', '#00008B')

        trace_label = ('Pin = -40 dBm', 'Pin = -30 dBm', 'Pin = -20 dBm', 'Pin = -10 dBm', 'Pin = 0 dBm')

        if sys.argv[len(sys.argv) - 1] == 'S11':
            ax0.plot(frequency, s11_db, label=('DUT' + str([i + 1]) + ' ' + str(sys.argv[len(sys.argv) - 1])),
                     color=trace_color[i], linewidth=2, alpha=0.75)
        elif sys.argv[len(sys.argv) - 1] == 'S21':
            ax0.plot(frequency, s21_db, label=('DUT' + str([i + 1]) + ' ' + str(sys.argv[len(sys.argv) - 1])),
                     color=trace_color[i], linewidth=2, alpha=0.75)
        elif sys.argv[len(sys.argv) - 1] == 'S12':
            ax0.plot(frequency, s12_db, label=('DUT' + str([i + 1]) + ' ' + str(sys.argv[len(sys.argv) - 1])),
                     color=trace_color[i], linewidth=2, alpha=0.75)
        elif sys.argv[len(sys.argv) - 1] == 'S22':
            ax0.plot(frequency, s22_db, label=('DUT' + str([i + 1]) + ' ' + str(sys.argv[len(sys.argv) - 1])),
                     color=trace_color[i], linewidth=2, alpha=0.75)
        else:
            print('Specified scattering parameter does not exist')
            sys.exit(1)

        clear_variables()

    ax0.legend(loc='upper right', fontsize=14)
    ax0.set_xlim(PLOT_0_X_MIN, PLOT_0_X_MAX)
    ax0.set_ylim(PLOT_0_Y_MIN, PLOT_0_Y_MAX)

    # For output png-file naming we delete extension from INPUT_FILE_NAME.sXp
    plt.savefig(fname='Multiple_DUTs_S_parameters', fmt='png', dpi=300)

    plt.show()


if __name__ == '__main__':

    # relate number of DUT's to the number of command line arguments
    num_duts = len(sys.argv) - 2

    plot_data(num_duts)
