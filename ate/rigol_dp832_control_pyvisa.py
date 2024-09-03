# coding 'utf-8'
import pyvisa
import serial
import csv
import time
import sys

# Special characters to be escaped
LF = 0x0A
CR = 0x0D
ESC = 0x1B
EOT = 0x04
PLUS = 0x2B

# Set voltage in Volts and current in Amperes for each DP832 channel
V1, I1, V2, I2, V3, I3 = 12, 0.3, 6, 0.2, 3.3, 0.2


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
    return float(dp832.query(cmd))


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


def peak_index_search(trace):
    peak_index = 0
    peak_value = -200
    for i in range(len(trace)):
        if trace[i] > peak_value:
            peak_index = i
            peak_value = trace[i]
    return peak_index


if __name__ == '__main__':

    t = time.time()
    rm = pyvisa.ResourceManager()
    device = rm.list_resources()
    print("DEVICE ID:", device[0])

    dp832 = rm.open_resource('USB0::0x1AB1::0x0E11::DP8C172001976::INSTR')

    dp832_set(ch=1, voltage=V1, current=I1, output='on')
    dp832_set(ch=2, voltage=V2, current=I2, output='on')
    dp832_set(ch=3, voltage=V3, current=I3, output='off')
    print("Power Supply is turned on")

    try:
        while 1:
            voltage = []
            current = []

            for i in range(1, 4, 1):
                voltage.append(dp832_get(ch=i, parameter='voltage'))
                current.append(dp832_get(ch=i, parameter='current'))

            print("CH1: {:7.4f}V {:6.4f}A   CH2: {:7.4f}V {:6.4f}A   CH3: {:7.4f}V {:6.4f}A".format(voltage[0], current[0], voltage[1], current[1], voltage[2], current[2]))
            time.sleep(2)
    except KeyboardInterrupt:
        pass


    dp832_set(ch=1, voltage=V1, current=I1, output='off')
    dp832_set(ch=2, voltage=V2, current=I2, output='off')
    dp832_set(ch=3, voltage=V3, current=I3, output='off')

    time.sleep(2)

    v = []
    c = []

    for i in range(1, 4, 1):
        v.append(dp832_get(ch=i, parameter='voltage'))
        c.append(dp832_get(ch=i, parameter='current'))

    print("CH1: {:7.4f}V {:6.4f}A   CH2: {:7.4f}V {:6.4f}A   CH3: {:7.4f}V {:6.4f}A".format(v[0], c[0], v[1], c[1], v[2], c[2]))

    dp832.write(':SYST:LOCK OFF')
    dp832.close()


#    write_serial('MKN?')  # it works!
#    write_serial('MKOFF')  # it works!
#    write_serial('++rst')  # performs a power-on reset of the controller, takes about 5 seconds
#    time.sleep(6)
    print("Power Supply is turned off")
    print("Time Elapsed: ", time.time() - t)
