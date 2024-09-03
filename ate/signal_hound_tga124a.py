# -*- coding: utf-8 -*-

# This example generates a signal.

import sys
sys.path.append('D:\\SYNTEIRA\\GitHub\\python_tools\\ate\\signal_hound_tga124a\\')

import tg_api
import time

def get_tg_status():

    # Print device type
    device_status = tg_api.tg_status_check(device)['status']
    print (f'Device Status: {device_status}')

    # Print device type
    device_type = tg_api.tg_get_device_type(device)['device_type']
    print (f'Device Type: {device_type}')

    # Print serial number
    serial = tg_api.tg_get_serial_number(device)['serial']
    print (f'Serial Number: {serial}')

    # Configure signal
    tg_api.tg_set_freq_amp(device, 1.0e9, -15)


def set_tg(frequency_hz, amplitude_dbm):

    # Configure signal
    tg_api.tg_set_freq_amp(device, 1.0e9, amplitude_dbm)


if __name__ == "__main__":

    freq = []
    for i in range(51):
        freq.append(1.0e9 + i*0.1e9)

    device = 0

    t = time.time()

    # Open device
    tg_api.tg_open_device(device)

    print("Time Elapsed: ", (time.time() - t))

    get_tg_status()

    for f in freq:
        t = time.time()
        set_tg(frequency_hz=f, amplitude_dbm = -15)
        print("Set Frequency: ", f, "Time Elapsed: ", (time.time() - t))

    # Close device
    tg_api.tg_close_device(device);
