# Before using this script install packages:
# - VXI-11          pip install python-vxi11
# - Matplotlib      pip install matplotlib

# TODO:
#
# 1. реализовать преобразование единиц измерения текстовых меток:
# на текущий момент текстовые метки выводятся в формате "RBW 10.0 kHz",
# необходимо убрать из надписи дробную часть, и выполнить преобразование
# единиц измерения до целочисленных значений вида "RBW 100 Hz", "RBW 3 kHz",
# "RBW 10 kHz", "RBW 1 MHz". Это же касается меток VBW, Span, Sweep Time
#
# 2. реализовать нормальным образом режим MAXHOLD:
# сейчас режим maxhold включается из скрипта, копит данные, пока анализатор
# спектра зависает на несколько секунд. Повторный запуск скрипта сбрасывает
# накопленную информацию.
#
# 3. реализовать режим виртуального анализатора спектра:
# пока скрипт активен, он запрашивает данные у анализатора спектра, и
# динамически обновляет график.

import sys
import vxi11
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FixedLocator, FormatStrFormatter, AutoMinorLocator)
from datetime import datetime

# Define spectrum plot settings

FREQ = 21.4 * 10 ** 6  # center frequency [Hz]
SPAN = 10 * 10 ** 6  # frequency span [Hz]

RBW = 10 * 10 ** 3  # resolution bandwidth [Hz]: 'auto' or 100 Hz to 1 MHz in 1-3-10 sequence
VBW = 10 * 10 ** 3  # video bandwidth [Hz]: 'auto' or 1 Hz to 3 MHz with 1-3-10 sequence

REF_LVL = -20  # reference level [dBm]
ATTEN = 0  # attenuator level [dB]: 0 dB to 30 dB with 1 dB step
LNA_MODE = 'OFF'  # low noise preamp control: ON or OFF

SWT = 37.5 * 10 ** -3

TRACE_MODE = 'normal'  # trace mode: normal, maxhold


def main():
    device_ip = "10.0.21.57"
    device_tp = vxi11.Instrument(device_ip)
    device_id = device_tp.ask("*IDN?")
    device_id = device_id.split(',')
    if device_id[1] == 'DG4102':
        print("Device is Rigol DG4102")
        sys.exit(0)
        pass
    elif device_id[1] == 'DP832':
        print("Device is Rigol DP832")
        sys.exit(0)
        pass
    elif device_id[1] == 'DSA815':
        device_id = ' '.join(device_id[:2])
        print("Device ID :", device_id)
        dsa815 = device_tp

    try:
        # cmd = ' '.join((':SENSE:FREQUENCY:CENTER', str(int(FREQ))))
        # print(cmd)
        # ret = dsa815.ask(cmd)
        # print(ret)

        freq, span, rbw, vbw, atten, ref_lvl, lna_mode, trace_mode, swt = dsa815_set_settings(dsa815,
                                                                                              FREQ, SPAN,
                                                                                              RBW, VBW,
                                                                                              ATTEN, REF_LVL, LNA_MODE,
                                                                                              TRACE_MODE)

        trace = dsa815.ask(":TRACE:DATA? TRACE1")
        trace = dsa815.ask(":TRACE:DATA? TRACE1")

        trace = trace.split(', ')

        # Remove "#900000914" at first element
        trace_0 = trace[0]
        trace[0] = trace_0[12:]

        trc = []
        for i in trace:
            trc.append(float(i))
        # trace = float(trace)

        plot_spectrum(trc, freq, span, rbw, vbw, atten, REF_LVL, lna_mode, trace_mode, swt)

    except KeyboardInterrupt:
        pass


def plot_spectrum(trace, fcenter, fspan, rbw, vbw, atten, ref_lvl, lna_mode, trc_mode, sw_time):
    PLOT_SIZE_X = 12
    PLOT_SIZE_Y = 9

    PLOT_NUM_PTS = 601

    # plot_0_x_min = (fcenter - fspan/2) / 10**6
    # plot_0_x_max = (fcenter + fspan/2) / 10**6
    # plot_0_x_minor_step = fspan / (10 * 10**6)
    # plot_0_x_major_step = fspan / (10 * 10**6)

    plot_0_x_min = int(fcenter - fspan / 2)
    plot_0_x_max = int(fcenter + fspan / 2)
    plot_0_x_minor_step = int(fspan / 10)
    plot_0_x_major_step = int(fspan / 10)

    # plot_0_x_min = 20
    # plot_0_x_max = 30
    # plot_0_x_minor_step = 1
    # plot_0_x_major_step = 1

    plot_0_y_min = int(ref_lvl - 100)
    plot_0_y_max = int(ref_lvl)
    PLOT_0_Y_MINOR_STEP = 5
    PLOT_0_Y_MAJOR_STEP = 10

    label_trc = ' '.join(('T1', trc_mode))
    label_fcnt = ' '.join(('Center Freq   ', str(fcenter / 10 ** 6), 'MHz'))
    label_span = ' '.join(('Span', str(fspan / 1000), 'kHz'))
    label_rbw = ' '.join(('RBW', str(rbw / 1000), 'kHz'))
    label_vbw = ' '.join(('VBW', str(vbw / 1000), 'kHz'))
    label_att = ' '.join(('Att', str(atten), 'dB'))
    label_ref = ' '.join(('Ref', str(ref_lvl), 'dBm'))
    label_lna = ' '.join(('Preamp:', lna_mode))
    label_swt = ' '.join(('Sweep Time', str(sw_time * 1000), 'ms'))

    x = []
    freq_delta = (plot_0_x_max - plot_0_x_min) / (len(trace) - 1)
    for i in range(len(trace)):
        x.append(plot_0_x_min + i * freq_delta)

    # fig, (ax0) = plt.subplots(1, 1, figsize=(PLOT_SIZE_X, PLOT_SIZE_Y), constrained_layout=true)
    fig, (ax0) = plt.subplots(1, 1, figsize=(PLOT_SIZE_X, PLOT_SIZE_Y))

    # Plot FFT Spectrum
    ax0.clear()

    # ax0.set_xlabel("Freq [MHz]", fontsize=14)
    # ax0.set_ylabel("Amplitude [dBm]", fontsize=14)

    ax0.grid(which="major", linestyle="--", color="gray", linewidth=0.5)
    ax0.grid(which="minor", linestyle="--", color="gray", linewidth=0.5)

    # ax0.xaxis.set_minor_locator(MultipleLocator(plot_0_x_minor_step))
    ax0.xaxis.set_minor_locator(FixedLocator([i for i in range(plot_0_x_min, plot_0_x_max, plot_0_x_minor_step)]))
    # ax0.xaxis.set_major_locator(MultipleLocator(plot_0_x_major_step))
    # ax0.yaxis.set_minor_locator(MultipleLocator(PLOT_0_Y_MINOR_STEP))
    ax0.yaxis.set_major_locator(MultipleLocator(PLOT_0_Y_MAJOR_STEP))

    ax0.tick_params(which='major', length=0, width=0.5, labelsize='large')
    ax0.tick_params(which='minor', length=0, width=0.5)

    ax0.plot(x, trace, label=label_trc, color='#00008B', linewidth=2, alpha=0.75)  # RGB Color Deep Blue-Violet
    # ax0.plot(x, y2, label="ADC2", color='#99004C', linewidth=2, alpha=0.75) # RGB Color Coral Red
    ax0.legend(loc='upper right', fontsize=14)
    ax0.set_xlim(plot_0_x_min, plot_0_x_max)
    ax0.set_ylim(plot_0_y_min, plot_0_y_max)

    ax0.axes.xaxis.set_ticks([])

    print(label_ref)

    plt.figtext(0.125, 0.9, label_ref, fontsize='large')
    plt.figtext(0.48, 0.9, label_att, fontsize='large')
    plt.figtext(0.8, 0.9, label_lna, fontsize='large')
    plt.figtext(0.125, 0.08, label_fcnt, fontsize='large')
    plt.figtext(0.75, 0.08, label_span, fontsize='large')
    plt.figtext(0.125, 0.05, label_rbw, fontsize='large')
    plt.figtext(0.47, 0.05, label_vbw, fontsize='large')
    plt.figtext(0.75, 0.05, label_swt, fontsize='large')

    plt.savefig(fname="dsa815_plot.png", format='png', dpi=300)

    plt.show()


def dsa815_set_settings(device, freq, span, rbw, vbw, att, ref, lna, tmd):
    cmd = ' '.join((':SENSe:FREQuency:CENTer', str(int(freq))))
    device.write(cmd)
    freq = int(device.ask(':SENSe:FREQuency:CENTer?'))
    print("Frequency:", freq / 10 ** 6, "MHz")

    cmd = ' '.join((':SENSe:FREQuency:SPAN', str(int(span))))
    device.write(cmd)
    span = int(device.ask(':SENSe:FREQuency:SPAN?'))
    print("SPAN:", span / 10 ** 6, "MHz")

    rbw = dsa815_set_rbw(device, rbw)
    vbw = dsa815_set_vbw(device, vbw)
    att = dsa815_set_atten(device, att)
    ref = dsa815_set_ref(device, ref)
    lna = dsa815_set_lna(device, lna)
    tmd = dsa815_set_trace_mode(device, tmd)
    sweep_time = float(device.ask(':SENSe:SWEep:TIME?'))

    return freq, span, rbw, vbw, att, ref, lna, tmd, sweep_time


def dsa815_set_rbw(device, rbw):
    rbw_min = 100
    rbw_max = 10 ** 6

    if rbw == 'auto':
        cmd = ':SENSe:BANDwidth:RESolution:AUTO ON'
        device.write(cmd)
        cmd = ':SENSe:BANDwidth:RESolution?'
        rbw = int(device.ask(cmd))

    elif rbw_min <= rbw <= rbw_max:
        cmd = ':SENSe:BANDwidth:RESolution:AUTO OFF'
        device.write(cmd)

        cmd = ' '.join((':SENSe:BANDwidth:RESolution', str(rbw)))
        device.write(cmd)

        cmd = ':SENSe:BANDwidth:RESolution?'
        rbw = int(device.ask(cmd))

    else:
        print("ERROR: Invalid RBW value")
        return 0

    print("RBW:", rbw / 10 ** 3, "kHz")

    return rbw


def dsa815_set_vbw(device, vbw):
    vbw_min = 100
    vbw_max = 3 * 10 ** 6

    if vbw == 'auto':
        cmd = ':SENSe:BANDwidth:VIDeo:AUTO ON'
        device.write(cmd)

    elif vbw_min <= vbw <= vbw_max:
        cmd = ':SENSe:BANDwidth:VIDeo:AUTO OFF'
        device.write(cmd)
        cmd = ' '.join((':SENSe:BANDwidth:VIDeo', str(vbw)))
        device.write(cmd)

    else:
        print("ERROR: Invalid VBW value")
        return 0

    vbw = int(device.ask(':SENSe:BANDwidth:VIDeo?'))
    print("VBW:", vbw / 10 ** 3, "kHz")
    return vbw


def dsa815_set_atten(device, att):
    att_min = 0
    att_max = 30

    if att == 'auto':
        cmd = ':SENSe:POWer:RF:ATTenuation:AUTO ON'
        device.write(cmd)

    elif att_min <= att <= att_max:
        cmd = ':SENSe:POWer:RF:ATTenuation:AUTO OFF'
        device.write(cmd)
        cmd = ' '.join((':SENSe:POWer:RF:ATTenuation', str(att)))
        device.write(cmd)
    else:
        print("ERROR: Invalid ATTEN value")
        return 0

    att = int(device.ask(':SENSe:POWer:RF:ATTenuation?'))
    print("Atten:", att, "dB")
    return att


def dsa815_set_ref(device, ref):
    ref_min = -100
    ref_max = 20

    if ref_min <= ref <= ref_max:
        cmd = ' '.join((':DISPlay:WINdow:TRACe:Y:SCALe:RLEVel', str(ref)))
        device.write(cmd)
    else:
        print("ERROR: Invalid reference level value")
        return 0

    ref = float(device.ask(':DISPlay:WINdow:TRACe:Y:SCALe:RLEVel?'))
    print("Ref level:", ref, "dBm")
    return ref


def dsa815_set_lna(device, lna_mode):
    if lna_mode == 'ON':
        cmd = ':SENSe:POWer:RF:GAIN:STATe ON'
        device.write(cmd)
    elif lna_mode == 'OFF':
        cmd = ':SENSe:POWer:RF:GAIN:STATe OFF'
        device.write(cmd)
    else:
        print("ERROR: Invalid LNA mode")
        return 0

    # lna_mode = device.ask(':SENSe:POWer:RF:GAIN:STATe?')
    print("LNA mode:", lna_mode)
    return lna_mode


def dsa815_set_trace_mode(device, trc_mode):
    if trc_mode == 'normal':
        cmd = ':TRACe1:MODE WRITe'
        device.write(cmd)
    elif trc_mode == 'maxhold':
        cmd = ':TRACe1:MODE MAXHold'
        device.write(cmd)
    else:
        print("ERROR: Invalid trace mode")
        return 0

    print("Trace mode:", trc_mode)
    return trc_mode


if __name__ == '__main__':
    main()