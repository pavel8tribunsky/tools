# coding 'utf-8'
import pyvisa
import serial
import csv
import time

# TODO:
# 1. Spectrum Analyzer Data Acquisition is very low because we need to receive 701 points
#    from instrument. It's necessary to replace frame acquisition by peak-search marker data
#    to speed up the VCO test bench.
# 2. Add power supply initial settings read, and restore at the end of VCO parameters measurement.
# 3. Add VCO power supply channel current consumption measurement and logging to DUT-file

# Special characters to be escaped
LF = 0x0A
CR = 0x0D
ESC = 0x1B
EOT = 0x04
PLUS = 0x2B


def dg4102_set(ch=1, wfm='sine', freq=1000, amp=0.001, offset=0, phase=0):

    if wfm == 'pulse':
        wfm = 'PULSe'
    elif wfm == 'ramp':
        wfm = 'RAMP'
    elif wfm == 'sine':
        wfm = 'SINusoid'
    elif wfm == 'square':
        wfm = 'SQUare'

    cmd = ':SOURce' + str(ch) + ':APPLy:' + wfm + ' ' + str(freq) + ',' + str(amp) + ',' + str(offset) + ',' + str(phase)
    dg4102.write(cmd)


def dp832_set(ch=1, voltage=3.3, current=0.1, output='on'):
    if output == 'on':
        output = 'ON'
    elif output == 'off':
        output = 'OFF'
    # set voltage and current for selected channel
    cmd = ':APPL CH' + str(ch) + ',' + str(voltage) + ',' + str(current)
    dp832.write(cmd)
    # turn output on/off
    cmd = ':OUTP CH' + str(ch) + ',' + output
    dp832.write(cmd)


def dp832_get(ch=1, parameter='current'):
    if parameter == 'current':
        output = 'CURR'
    elif parameter == 'voltage':
        output = 'VOLT'
    elif parameter == 'power':
        output = 'POWE'
    else:
        print("Specified parameter doesn't exist")

    cmd = ':MEAS:' + output + ':DC? CH' + str(ch)

    # return current in mA
    return float(dp832.query(cmd))*1000

def write_serial(cmd):

    print('Sending:', cmd)
    cmd = cmd + '\n'
    ser.write(cmd.encode())

    s = ser.read(701*3)
    if len(s) > 0:
        print(s.decode("utf-8"))


def write_csv(output_file_name, csv_row_1, csv_row_2, csv_row_3, csv_row_4):
    output_file = open(output_file_name + '.csv', 'w', newline='') # open file for writing
    output_writer = csv.writer(output_file, delimiter='\t')

    for i in range(len(csv_row_1) + 1):
        if i == 0:
            output_writer.writerow(['Control voltage [V]', 'Frequency [Hz]', 'Power [dBm]', 'Current consumption [mA]']) # write header into csv file
        else:
            output_writer.writerow([csv_row_1[i-1], csv_row_2[i-1], csv_row_3[i-1], csv_row_4[i-1]]) # write data into csv file

    output_file.close() # close csv-file


def prologix_set(gpib_addr=1):

#    write_serial('++rst')
#    time.sleep(7)
    write_serial('++mode 1')  # 0 - switch to DEVICE mode, 1 - switch to CONTROLLER mode
#    write_serial('++mode')  # get mode
#    write_serial('++ver')  # prologix adapter firmware version query
    write_serial('++addr ' + str(gpib_addr))  # set GPIB address
#    write_serial('++addr')  # get GPIB address
    write_serial('++auto 1')  # 0 - addresses the ADV R3271 to LISTEN mode, 1 - TALK mode
    write_serial('++eoi 1')  # 0 - disable EOI assertion with the last character
    #                         of any command sent over GPIB port, 1 - disable EOI assertion
#    write_serial('++eoi')  # 0 - disable EOI assertion with the last character
#    write_serial('++eos 2')  # 0 - append CR+LF to instrument commands, 1 - append CR,
    #                          2 - append LF, 3 - don't append anything to commands
#    write_serial('++eos')  # 0 - append CR+LF to instrument commands, 1 - append CR,
    write_serial('++eot_enable 1')  # 0 - append CR+LF to instrument commands, 1 - append CR,
    write_serial('++eot_char 10')
    write_serial('++savecfg 0')  # 0 - disable saving of configuration parameters in EPROM, 1 - enable


def r3271_set():
    write_serial('TYP?')  # it works!
    write_serial('REV?')
    #    write_serial('HP8562')
    write_serial('R3271')
    write_serial('SRQ OFF')
    #    write_serial('TS')  # take a single sweep
    #    write_serial('CONTS')  # continuous sweep
#    write_serial('MKPK HI')  # it works!


def r3271_get_spectrum():
    """ This function gets start and stop frequencies and binary trace data form ADVANTEST R3271

    Args:
        trace_name: Specify 'A' or 'B' trace name to get

    Returns:
        List of [prescaler, R-counter, A-counter, B-counter, N-counter]

    Raises:
        KeyError: Raises an exception.
    """

    n_points = 701
    # Start frequency query
    cmd = 'FA?'
    cmd = cmd + '\n'
    ser.write(cmd.encode())
    s = ser.read(256)
    print(s)
    s_ = s.decode('utf-8')
    s = s_[4:]
    start_frequency = float(s)

    # Stop frequency query
    cmd = 'FB?'
    cmd = cmd + '\n'
    ser.write(cmd.encode())
    s = ser.read(256)
    print(s)
    s_ = s.decode('utf-8')
    s = s_[4:]
    stop_frequency = float(s)

    # Reference level query
    cmd = 'RL?'
    cmd = cmd + '\n'
    ser.write(cmd.encode())
    s = ser.read(256)
    print(s)
    s_ = s.decode('utf-8')
    s = s_[5:]
    reference_level = float(s)

    cmd = 'TS'
    cmd = cmd + '\n'
    ser.write(cmd.encode())

    cmd = 'TBA?'
    cmd = cmd + '\n'
    ser.write(cmd.encode())
    s = ser.read(2*n_points - 1)
    trace_a_ = []
    for i in range(n_points - 1):
        k = (i * 2)
        trace_a_.append(int.from_bytes([s[k], s[k+1]], byteorder='big'))

    cmd = 'TBB?'
    cmd = cmd + '\n'
    ser.write(cmd.encode())
    s = ser.read(2*n_points - 1)
    trace_b_ = []
    for i in range(n_points - 1):
        k = (i * 2)
        trace_b_.append(int.from_bytes([s[k], s[k+1]], byteorder='big'))

    x_res_hz = (stop_frequency - start_frequency) / 700
    x0 = start_frequency
    y_res_db = 100 / 400  # dB per vertical point (400 points at all)
    y0 = reference_level - 100  # dBm value of 0 position

    frequency = []
    for i in range(len(trace_a_)):
        frequency.append(int(i*x_res_hz + x0))

    trace_a = []
    for spectrum_bin in trace_a_:
        trace_a.append(spectrum_bin*y_res_db + y0)

    trace_b = []
    for spectrum_bin in trace_b_:
        trace_b.append(spectrum_bin*y_res_db + y0)

    return [frequency, trace_a, trace_b]


def peak_index_search(trace):
    peak_index = 0
    peak_value = -200
    for i in range(len(trace)):
        if trace[i] > peak_value:
            peak_index = i
            peak_value = trace[i]
    return peak_index


def gpib_release_control():

    # set continuous sweep
    cmd = 'CONTS'
    cmd = cmd + '\n'
    ser.write(cmd.encode())

    write_serial('++loc')


if __name__ == '__main__':

    t = time.time()
    print("VCO Test is Started")

    ser = serial.Serial('COM3', 115200, timeout=0.5)
#    prologix_set(gpib_addr='1')

    rm = pyvisa.ResourceManager()
    # print(rm.list_resources())

    dg4102 = rm.open_resource('USB0::0x1AB1::0x0641::DG4E191600601::INSTR')
    dp832 = rm.open_resource('USB0::0x1AB1::0x0E11::DP8C192502607::INSTR')

    prologix_set()
    r3271_set()

#    print('Test Set includes:')
#    awg = dg4102.query("*IDN?")
#    ps = dp832.query("*IDN?")
#    print(awg[:25])
#    print(ps[:24])

    dg4102.write(':OUTPut1 ON')

    dp832_set(ch=1, voltage=3.3, current=0.1, output='off')
    dp832_set(ch=2, voltage=3.3, current=0.1, output='off')
    dp832_set(ch=3, voltage=3.3, current=0.1, output='off')

    dp832_ch1_voltage = [3.3, 5.0]

    for i in dp832_ch1_voltage:
        dp832_set(ch=1, voltage=3.3, current=0.1, output='on')
        dp832_set(ch=2, voltage=3.3, current=0.1, output='on')
        dp832_set(ch=3, voltage=i, current=0.05, output='on')

        vco_vct = []
        vco_frq = []
        vco_pwr = []
        vco_cur = []
        for j in range(46):
            ofs = j/10
            vco_vct.append(ofs)
            dg4102_set(ch=1, wfm='sine', freq=1000, amp=0.001,
                       offset=ofs, phase=0)
            freq, trace_a, trace_b = r3271_get_spectrum()
            current = dp832_get(ch=3, parameter='current')
            index = peak_index_search(trace=trace_a)
            vco_frq.append(freq[index])
            vco_pwr.append(trace_a[index])
            vco_cur.append(current)
        write_csv(('DUT_1_' + str(i) + 'V'), vco_vct, vco_frq, vco_pwr, vco_cur)
        dp832_set(ch=3, voltage=i, current=0.1, output='off')

    dg4102.write(':OUTPut1 OFF')
    dg4102_set(ch=1, wfm='sine', freq=1000, amp=0.001, offset=0, phase=0)
    dg4102.close()
    dp832_set(ch=1, voltage=3.3, current=0.1, output='off')
    dp832_set(ch=2, voltage=3.3, current=0.1, output='off')
    dp832.write(':SYST:LOCK OFF')
    dp832.close()


#    write_serial('MKN?')  # it works!
#    write_serial('MKOFF')  # it works!
    gpib_release_control()  # it works!
#    write_serial('++rst')  # performs a power-on reset of the controller, takes about 5 seconds
#    time.sleep(6)
    print("VCO Test is Stoped")
    print("Time Elapsed: ", time.time() - t)
