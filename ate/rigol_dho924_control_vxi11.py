# Before using this script install packages:
# - VXI-11          pip install python-vxi11
# - Pillow          pip install Pillow

import sys
import vxi11


def main():
    device_ip = "192.168.20.161"
    device = vxi11.Instrument(device_ip)
    device_id = device.ask("*IDN?")
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
    elif device_id[1] == 'DHO924S':
        device_id = ' '.join(device_id[:2])
        print("Device ID :", device_id)

    try:
        filename = dho900_get_screenshot(device)
        crop(filename, left=12, upper=92, right=(1024-12), lower=(600-92))

    except KeyboardInterrupt:
        pass


def dho900_get_screenshot(device, format='PNG'):
    import os

    cmd = ''
    extension = ''

    if format == 'BMP':
        cmd = ':DISPlay:DATA? BMP'
        extension = 'bmp'
    elif format == 'PNG':
        cmd = ':DISPlay:DATA? PNG'
        extension = 'png'
    elif format == 'JPG':
        cmd = ':DISPlay:DATA? JPG'
        extension = 'jpg'
    else:
        print("ERROR: Invalid image format")
        return 0
    
    filename = 'RigolDS'
    dir_content = os.listdir()
    for num in range(127):
        file_exist = False
        f = ''
        f = "".join((filename, str(num)))
        for obj in dir_content:
            if os.path.isfile(obj):
                obj_name = os.path.splitext(obj)[0]
                if f == obj_name:
                    file_exist = True
                    break
        if not file_exist:
            filename = f
            break

    filename = ".".join((filename, extension))

    device.write(cmd)
    image = device.read_raw()
    hdr_len = int(chr(image[1])) # bytes to string to int
    image = image[(hdr_len+2):]

    with open(filename, "wb") as fw:
        fw.write(image)

    print("File saved:", filename)
    return filename


def crop(filename, left=12, upper=92, right=(1024-12), lower=(600-92)):
    from PIL import Image
    im = Image.open(filename)
    im_crop = im.crop((left, upper, right, lower))
    im_crop.save(filename, quality=100)


if __name__ == '__main__':
    main()