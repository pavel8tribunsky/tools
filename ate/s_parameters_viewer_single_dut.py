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
PLOT_SIZE_X = 12
PLOT_SIZE_Y = 4

# Set Plot 0 X axis
PLOT_0_X_MIN = 100  # frequency in MHz
PLOT_0_X_MAX = 3000  # frequency in MHz
PLOT_0_X_MINOR_STEP = 50  # frequency in MHz
PLOT_0_X_MAJOR_STEP = 100  # frequency in MHz

# Set Plot 0 Y axis
PLOT_0_Y_MIN = -40
PLOT_0_Y_MAX = 40
PLOT_0_Y_MINOR_STEP = 5
PLOT_0_Y_MAJOR_STEP = 10

# Number of lines of the Touchstone file to skip
NUM_SKIP_LINES = 5

# Variables statement
x = []
fig, (ax0) = plt.subplots(1, 1,
                          figsize=(PLOT_SIZE_X, PLOT_SIZE_Y),
                          constrained_layout=True)

frequency_mhz = []
s11_db = []
s11_ang = []
s21_db = []
s21_ang = []
s12_db = []
s12_ang = []
s22_db = []
s22_ang = []


def read_touchstone():

    # open reference data file for reading
    input_file = open(INPUT_FILE_NAME, 'r', newline='')
    reader = csv.reader(input_file, delimiter=' ')

    # skip the header
    for i in range(NUM_SKIP_LINES):
        next(reader, None)

    # S-parameters data acquisition
    for frequency_hz_,\
        s11_db_, s11_ang_, \
        s21_db_, s21_ang_, \
        s12_db_, s12_ang_, \
        s22_db_, s22_ang_, \
            in reader:
        frequency_mhz.append(int((float(frequency_hz_) / 10 ** 6)))
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


def plot_data(y1, y2, y3, y4):

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

    # Trace "y1" has Deep Blue-Violet color
    ax0.plot(x, y1, label="S11", color='#00805C', linewidth=2, alpha=0.75)
    # Trace "y2" has Deep Coral Red color
    ax0.plot(x, y2, label="S21", color='#99004C', linewidth=2, alpha=0.75)
    # Trace "y3" has Deep Blue color
    ax0.plot(x, y3, label="S12", color='#00008B', linewidth=2, alpha=0.75)
    # Trace "y4" has Deep Red color
    ax0.plot(x, y4, label="S22", color='#DAA520', linewidth=2, alpha=0.75)

    ax0.legend(loc='upper right', fontsize=14)
    ax0.set_xlim(PLOT_0_X_MIN, PLOT_0_X_MAX)
    ax0.set_ylim(PLOT_0_Y_MIN, PLOT_0_Y_MAX)

    # For output png-file naming we delete extension from INPUT_FILE_NAME.sXp
    plt.savefig(fname=INPUT_FILE_NAME[:-3], fmt='png', dpi=300)

    plt.show()


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: ", os.path.basename(sys.argv[0]), "<Touchstone Model File>")
        sys.exit(1)

    INPUT_FILE_NAME = sys.argv[1]

    read_touchstone()

    #    for i in range(len(frequency_hz)):
    #        x.append(frequency_hz(i))
    #        x.append(frequency_hz(i) / 10**6)
    x = frequency_mhz

    plot_data(s11_db, s21_db, s12_db, s22_db)
