import os
import csv
import requests
import socket
import sys

ieee_oui_file = 'ieee_oui.csv'
ieee_oui_url = "https://api.macvendors.com/"

def main():
    check_ieee_oui_exist()
    ip = get_host_ip()
    print("Host IP:", ip)
    print("\n")
    ip_prefix = ip.split(".")
    ip_prefix = ip_prefix[:3]

    print(sys.argv)
    for addr in range (int(sys.argv[1]), int(sys.argv[2])):
        addr = get_ping()

def check_ieee_oui_exist():
    if os.path.isfile(ieee_oui_file):
        pass
    else:
        try:
            get_ieee_oui_file()
        except:
            print("No internet connection")

    pass

def get_ieee_oui_file():
    output_file = open(ieee_oui_file, 'w', newline='') # open file for writing
    output_writer = csv.writer(output_file, delimiter='\t')

    for mac_addr in range(0xFFFFFFFFFFFF + 1):
        if mac_addr == 0:
            output_writer.writerow(['MAC address', 'Vendor']) # write header into csv file
        else:
            try:
                mac = [str((mac_addr & 0xFF0000000000) >> 40),\
                       str((mac_addr & 0x00FF00000000) >> 32),\
                       str((mac_addr & 0x0000FF000000) >> 24),\
                       str((mac_addr & 0x000000FF0000) >> 16),\
                       str((mac_addr & 0x00000000FF00) >> 8),\
                       str((mac_addr & 0x0000000000FF) >> 0)]
                mac = "-".join(mac)
                print(mac)
                #vendor_name = get_mac_details(mac_addr)
                output_writer.writerow("-".join(mac), vendor_name) # write data into csv file
            except:
                #print("No internet connection")
                output_file.close() # close csv-file
                #os.remove(ieee_oui_file)

    output_file.close() # close csv-file


def get_mac_details(mac_address):
     
    # Use get method to fetch details
    response = requests.get(url+mac_address)
    if response.status_code != 200:
        raise Exception("[!] Invalid MAC Address!")
    return response.content.decode()


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Создаем сокет (UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Настраиваем сокет на BROADCAST вещание.
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]

 
if __name__ == "__main__":
    main()