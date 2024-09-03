# -*- coding: utf-8 -*-

# Copyright (c) 2019 Signal Hound
# For licensing information, please see the API license in the software_licenses folder

from ctypes import *
from sys import exit

tglib = CDLL("D:\\SYNTEIRA\\GitHub\\python_tools\\ate\\signal_hound_tga124a\\x64\\tg_api.dll")


# ---------------------------------- Defines -----------------------------------

TG_MAX_DEVICES = 4

TG_REF_UNUSED = 0
TG_REF_INTERNAL_OUT = 1
TG_REF_EXTERNAL_IN = 2


# --------------------------------- Mappings ----------------------------------

tgOpenDevice = tglib.tgOpenDevice
tgOpenAllDevices = tglib.tgOpenAllDevices
tgCloseDevice = tglib.tgCloseDevice
tgStatusCheck = tglib.tgStatusCheck
tgGetSerialNumber = tglib.tgGetSerialNumber
tgGetDeviceType = tglib.tgGetDeviceType
tgSetFreqAmp = tglib.tgSetFreqAmp
tgSetReference = tglib.tgSetReference
tgSetAttenuator = tglib.tgSetAttenuator


# ---------------------------------- Utility ----------------------------------

def error_check(func):
    def print_status_if_error(*args, **kwargs):
        return_vars = func(*args, **kwargs)
        if "status" not in return_vars.keys():
            return return_vars
        status = return_vars["status"]
        if status != 0:
            print (f"Error {status} in {func.__name__}()")
        if status < 0:
            exit()
        return return_vars
    return print_status_if_error


# --------------------------------- Functions ---------------------------------

@error_check
def tg_open_device(device):
    return {
        "status": tgOpenDevice(device)
    }

@error_check
def tg_open_all_devices():
    num_devices_initialized = c_int(-1)
    status = tgOpenAllDevices(byref(num_devices_initialized))
    return {
        "status": status,
        "num_devices_initialized": num_devices_initialized.value
    }

@error_check
def tg_close_device(device):
    return {
        "status": tgCloseDevice(device)
    }

@error_check
def tg_status_check(device):
    return {
        "status": tgStatusCheck(device)
    }

@error_check
def tg_get_serial_number(device):
    serial = c_int(-1)
    status = tgGetSerialNumber(device, byref(serial))
    return {
        "status": status,
        "serial": serial.value
    }

@error_check
def tg_get_device_type(device):
    device_type = c_int(-1)
    status = tgGetDeviceType(device, byref(device_type))
    return {
        "status": status,
        "device_type": device_type.value
    }

@error_check
def tg_set_freq_amp(device, freq, ampl):
    return {
        "status": tgSetFreqAmp(device, c_double(freq), c_float(ampl))
    }

@error_check
def tg_set_reference(device, ref):
    return {
        "status": tgSetReference(device, ref)
    }

@error_check
def tg_set_attenuator(device, atten):
    return {
        "status": tgSetAttenuator(device, c_float(atten))
    }
