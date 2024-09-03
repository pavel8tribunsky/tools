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

# Set Figure Size
PLOT_SIZE_X = 12
PLOT_SIZE_Y = 9

# Set Plot 0 X axis
PLOT_0_X_MIN = 0  # Minimum VCO control voltage in Volts
PLOT_0_X_MAX = 5  # Maximum VCO control voltage in Volts
PLOT_0_X_MINOR_STEP = 0.5  # VCO control voltage minor step
PLOT_0_X_MAJOR_STEP = 1  # VCO control voltage major step

# Set Plot 0 Y axis
PLOT_0_Y_MIN = 4.8
PLOT_0_Y_MAX = 5.3
PLOT_0_Y_MINOR_STEP = 0.05
PLOT_0_Y_MAJOR_STEP = 0.1

# Set Plot 1 X axis
PLOT_1_X_MIN = 0  # frequency in MHz
PLOT_1_X_MAX = 5  # frequency in MHz
PLOT_1_X_MINOR_STEP = 0.5  # frequency in MHz
PLOT_1_X_MAJOR_STEP = 1  # frequency in MHz

# Set Plot 1 Y axis
PLOT_1_Y_MIN = -50
PLOT_1_Y_MAX = 0
PLOT_1_Y_MINOR_STEP = 5
PLOT_1_Y_MAJOR_STEP = 10

# Number of lines of the Touchstone file to skip
NUM_SKIP_LINES = 1


def read_vco_parameters(file_name, num_skip_lines):

    freq_hz_ = []
    vctl_v_ = []
    pwr_dbm_ = []

    # open data file for reading
    input_file = open(file_name, 'r', newline='')
    reader = csv.reader(input_file, delimiter='\t')

    # skip the header
    for i in range(num_skip_lines):
        next(reader, None)

    # S-parameters data acquisition
    for row_0, row_1, row_2 in reader:
        vctl_v_.append(float(row_0))
        freq_hz_.append(float(row_1))
        pwr_dbm_.append(float(row_2))

    # close csv-file
    input_file.close()
    return [vctl_v_, freq_hz_, pwr_dbm_]


def plot_data(x, y1, y2, file_name):

    fig, (ax0, ax1) = plt.subplots(2, 1,
                                   figsize=(PLOT_SIZE_X, PLOT_SIZE_Y),
                                   constrained_layout=True)
    # Plot Frequency vs Control Voltage
    ax0.clear()
    ax0.set_xlabel("Control Voltage [V]", fontsize=14)
    ax0.set_ylabel("Frequency [GHz]", fontsize=14)
    ax0.grid(which="major", linewidth=1.2)
    ax0.grid(which="minor", linestyle="--", color="gray", linewidth=0.5)
    ax0.xaxis.set_minor_locator(MultipleLocator(PLOT_0_X_MINOR_STEP))
    ax0.xaxis.set_major_locator(MultipleLocator(PLOT_0_X_MAJOR_STEP))
    ax0.yaxis.set_minor_locator(MultipleLocator(PLOT_0_Y_MINOR_STEP))
    ax0.yaxis.set_major_locator(MultipleLocator(PLOT_0_Y_MAJOR_STEP))
    ax0.tick_params(which='major', length=10, width=2)
    ax0.tick_params(which='minor', length=5, width=1)

    # Trace "y1" has Deep Blue-Violet color
    ax0.plot(x, y1, label="DUT Frequency", color='#00805C', linewidth=2, alpha=0.75)
    # Trace "y2" has Deep Coral Red color
#    ax0.plot(x, y2, label="S21", color='#99004C', linewidth=2, alpha=0.75)
    # Trace "y3" has Deep Blue color
#    ax0.plot(x, y3, label="S12", color='#00008B', linewidth=2, alpha=0.75)
    # Trace "y4" has Deep Red color
#    ax0.plot(x, y4, label="S22", color='#DAA520', linewidth=2, alpha=0.75)

    ax0.legend(loc='upper right', fontsize=14)
    ax0.set_xlim(PLOT_0_X_MIN, PLOT_0_X_MAX)
    ax0.set_ylim(PLOT_0_Y_MIN, PLOT_0_Y_MAX)

    # Plot Power vs Control Voltage
    ax1.clear()
    ax1.set_xlabel("Control Voltage [V]", fontsize=14)
    ax1.set_ylabel("Power [dBm]", fontsize=14)
    ax1.grid(which="major", linewidth=1.2)
    ax1.grid(which="minor", linestyle="--", color="gray", linewidth=0.5)
    ax1.xaxis.set_minor_locator(MultipleLocator(PLOT_1_X_MINOR_STEP))
    ax1.xaxis.set_major_locator(MultipleLocator(PLOT_1_X_MAJOR_STEP))
    ax1.yaxis.set_minor_locator(MultipleLocator(PLOT_1_Y_MINOR_STEP))
    ax1.yaxis.set_major_locator(MultipleLocator(PLOT_1_Y_MAJOR_STEP))
    ax1.tick_params(which='major', length=10, width=2)
    ax1.tick_params(which='minor', length=5, width=1)

    # Trace "y1" has Deep Blue-Violet color
    ax1.plot(x, y2, label="DUT Power", color='#00805C', linewidth=2, alpha=0.75)
    # Trace "y2" has Deep Coral Red color
    #    ax0.plot(x, y2, label="S21", color='#99004C', linewidth=2, alpha=0.75)
    # Trace "y3" has Deep Blue color
    #    ax0.plot(x, y3, label="S12", color='#00008B', linewidth=2, alpha=0.75)
    # Trace "y4" has Deep Red color
    #    ax0.plot(x, y4, label="S22", color='#DAA520', linewidth=2, alpha=0.75)

    ax1.legend(loc='upper right', fontsize=14)
    ax1.set_xlim(PLOT_1_X_MIN, PLOT_1_X_MAX)
    ax1.set_ylim(PLOT_1_Y_MIN, PLOT_1_Y_MAX)

    # For output png-file naming we delete extension from INPUT_FILE_NAME.sXp
    plt.savefig(fname=file_name[:-3], fmt='png', dpi=300)

    plt.show()


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: ", os.path.basename(sys.argv[0]), "<VCO Parameters File>")
        sys.exit(1)

    input_file_name = sys.argv[1]

    vctl_v, freq_hz, pwr_dbm = read_vco_parameters(input_file_name, NUM_SKIP_LINES)

    freq_ghz = []

    for i in range(len(freq_hz)):
        freq_ghz.append(freq_hz[i] / 10**9)

    print(vctl_v)
    plot_data(vctl_v, freq_ghz, pwr_dbm, input_file_name)
