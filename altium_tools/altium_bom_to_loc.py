# coding: utf-8
# The program convert Altium's Bill of Materials to List of Components

import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator)
import os.path
import sys

NUM_SKIP_LINES = 2

designator = []
component_type = []
part_number = []
part_label = []
manufacturer = []
quantity = []


def read_bom_template(input_file_name):

    # open reference data file for reading
    input_file = open(input_file_name, 'r', newline='')
    reader = csv.reader(input_file, delimiter='\t')  # use tab delimiter

    # skip the header
    for i in range(NUM_SKIP_LINES):
        next(reader, None)

    # read data from csv-file
    for designator_, component_type_, part_number_, part_label_, manufacturer_, quantity_ in reader:
        designator.append(designator_)
        component_type.append(component_type_)
        part_number.append(part_number_)
        part_label.append(part_label_)
        manufacturer.append(manufacturer_)
        quantity.append(quantity_)

    # close csv-file
    input_file.close()


def write_csv(designator, component_type, part_number, part_label, manufacturer, quantity):

    output_file = open(input_file_name[:-4] + '_loc.txt', 'w', newline='') # create file with "_out" postfix
    output_writer = csv.writer(output_file, delimiter='\t', quoting = csv.QUOTE_NONE, escapechar='', quotechar='')

    cnt = 0

    ref_des = ''

    for i in range(len(designator)):

        if i < (len(designator) - 2):
            if part_number[i] != part_number[i+1]:
                if cnt == 0:
                    ref_des = designator[i]
                if part_label[i] == '':
                    value = str(part_number[i]) + ' ' + str(manufacturer[i])
                else:
                    value = str(part_number[i]) + ' (' + str(part_label[i]) + ') ' + str(manufacturer[i])
                qty = str(int(quantity[i]) + cnt)
                output_writer.writerow([ref_des, value, qty]) # write data into csv file
                ref_des = ''
                cnt = 0

            else:
                cnt += 1
                if cnt == 1:
                    ref_des_start = str(designator[i])
                    ref_des_stop = str(designator[i+1])
                    ref_des = ref_des_start + ', ' + ref_des_stop
                else:
                    ref_des_stop = str(designator[i+1])
                    ref_des = ref_des_start + ' - ' + ref_des_stop
        else:
            if cnt == 0:
                ref_des = designator[i]
            if part_label[i] == '':
                value = str(part_number[i]) + ' ' + str(manufacturer[i])
            else:
                value = str(part_number[i]) + ' (' + str(part_label[i]) + ') ' + str(manufacturer[i])
            qty = str(int(quantity[i]) + cnt)
            output_writer.writerow([ref_des, value, qty])  # write data into csv file

    output_file.close() # close csv-file


if __name__ == '__main__':

    input_file_name = sys.argv[1]
    read_bom_template(input_file_name)
    write_csv(designator, component_type, part_number, part_label, manufacturer, quantity)
