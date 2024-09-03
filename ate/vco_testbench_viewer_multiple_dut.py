# Place VCO parameters files (.csv) to same folder
# with vco_testbench_viewer_multiple_dut.py.
# In the command line enter
# python <Current Python File> <DUT1.csv> <DUT2.csv> ... <DUTn.csv> frequency/power

import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator)
import sys

# TODO:
# 1. Add autoscale function if "auto" key is entered in command line.

# Set Figure Size
PLOT_SIZE_X = 12
PLOT_SIZE_Y = 4

# Set Plot 0 X axis
PLOT_0_X_MIN = 0  # Minimum VCO control voltage in Volts
PLOT_0_X_MAX = 6  # Maximum VCO control voltage in Volts
PLOT_0_X_MINOR_STEP = 0.1  # VCO control voltage minor step
PLOT_0_X_MAJOR_STEP = 0.5  # VCO control voltage major step

# Set Plot 0 Y axis for Frequency Plot
PLOT_0_F_MIN = 5.10
PLOT_0_F_MAX = 5.35
PLOT_0_F_MINOR_STEP = 0.01
PLOT_0_F_MAJOR_STEP = 0.05

# Set Plot 0 Y axis for Power Plot
PLOT_0_P_MIN = -22
PLOT_0_P_MAX = -12
PLOT_0_P_MINOR_STEP = 0.25
PLOT_0_P_MAJOR_STEP = 1

# Number of lines of the Touchstone file to skip
NUM_SKIP_LINES = 1


def read_vco_parameters(file_name, num_skip_lines):

    # open data file for reading
    input_file = open(file_name, 'r', newline='')
    reader = csv.reader(input_file, delimiter='\t')

    # skip the header
    for i in range(num_skip_lines):
        next(reader, None)

    vctrl_v_ = []
    freq_ghz_ = []
    pwr_dbm_ = []
    curr_ = []

    # data acquisition
    for row_0, row_1, row_2, row_3 in reader:
        vctrl_v_.append(float(row_0))
        freq_ghz_.append(float(row_1) / 10**9)
        pwr_dbm_.append(float(row_2))
        curr_.append(float(row_3))

    # close csv-file
    input_file.close()

    return [vctrl_v_, freq_ghz_, pwr_dbm_]


def plot_data(data, x_axis_name, x_axis_set, y0_axis_name, y0_axis_set, y1_axis_name, y1_axis_set):

    trace_color = ('#0000CC', '#C00000', '#00805C', '#DAA520', '#99004C', '#00008B')

    trace_label = ('TX_1 @ 3.3V 6mA', 'TX_1 @ 5.0V 10mA', 'TX_1 @ 3.3V 9mA', 'TX_1 @ 5.0V 14mA', 'TX_2', 'TX_3')

    fig, (ax0, ax1) = plt.subplots(1, 2,
                                   figsize=(PLOT_SIZE_X, PLOT_SIZE_Y),
                                   constrained_layout=True)
    ax0.set_xlabel(x_axis_name, fontsize=14)
    ax0.set_ylabel(y0_axis_name, fontsize=14)
    ax0.grid(which="major", linewidth=1.2)
    ax0.grid(which="minor", linestyle="--", color="gray", linewidth=0.5)
    ax0.xaxis.set_minor_locator(MultipleLocator(x_axis_set[2]))
    ax0.xaxis.set_major_locator(MultipleLocator(x_axis_set[3]))
    ax0.yaxis.set_minor_locator(MultipleLocator(y0_axis_set[2]))
    ax0.yaxis.set_major_locator(MultipleLocator(y0_axis_set[3]))
    ax0.tick_params(which='major', length=10, width=2)
    ax0.tick_params(which='minor', length=5, width=1)

    for i in range(len(data)):

        vctl_v, freq, pwr = data[i]
        ax0.plot(vctl_v, freq, label=trace_label[i], color=trace_color[i], linewidth=2, alpha=0.75)

    ax0.legend(loc='lower right', fontsize=12)
    ax0.set_xlim(x_axis_set[0], x_axis_set[1])
    ax0.set_ylim(y0_axis_set[0], y0_axis_set[1])

    ax1.set_xlabel(x_axis_name, fontsize=14)
    ax1.set_ylabel(y1_axis_name, fontsize=14)
    ax1.grid(which="major", linewidth=1.2)
    ax1.grid(which="minor", linestyle="--", color="gray", linewidth=0.5)
    ax1.xaxis.set_minor_locator(MultipleLocator(x_axis_set[2]))
    ax1.xaxis.set_major_locator(MultipleLocator(x_axis_set[3]))
    ax1.yaxis.set_minor_locator(MultipleLocator(y1_axis_set[2]))
    ax1.yaxis.set_major_locator(MultipleLocator(y1_axis_set[3]))
    ax1.tick_params(which='major', length=10, width=2)
    ax1.tick_params(which='minor', length=5, width=1)

    for i in range(len(data)):

        vctl_v, freq, pwr = data[i]
        ax1.plot(vctl_v, pwr, label=trace_label[i], color=trace_color[i], linewidth=2, alpha=0.75)

    ax1.legend(loc='lower right', fontsize=12)
    ax1.set_xlim(x_axis_set[0], x_axis_set[1])
    ax1.set_ylim(y1_axis_set[0], y1_axis_set[1])

    plt.savefig(fname='Multiple_DUTs_VCO_parameters', fmt='png', dpi=300)

    plt.show()


if __name__ == '__main__':

    # relate number of DUT's to the number of command line arguments
    num_duts = len(sys.argv) - 1

    dut = []
    for i in range(num_duts):
        input_file_name = sys.argv[i + 1]
        dut.append(read_vco_parameters(input_file_name, NUM_SKIP_LINES))

    x_axis_label = 'Control Voltage [V]'
    x_axis_limits = [PLOT_0_X_MIN, PLOT_0_X_MAX, PLOT_0_X_MINOR_STEP, PLOT_0_X_MAJOR_STEP]
    y0_axis_label = 'Frequency [GHz]'
    y0_axis_limits = [PLOT_0_F_MIN, PLOT_0_F_MAX, PLOT_0_F_MINOR_STEP, PLOT_0_F_MAJOR_STEP]
    y1_axis_label = 'Power [dBm]'
    y1_axis_limits = [PLOT_0_P_MIN, PLOT_0_P_MAX, PLOT_0_P_MINOR_STEP, PLOT_0_P_MAJOR_STEP]

    plot_data(dut, x_axis_label, x_axis_limits, y0_axis_label, y0_axis_limits, y1_axis_label, y1_axis_limits)
