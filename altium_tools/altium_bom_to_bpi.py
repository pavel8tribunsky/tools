# coding: utf-8
# The program convert Altium's Bill of Materials to Bill to Purchase Items

# TODO:
# 1. The program skips some components, for example 51 Ohm resistor,
# and all IC's.

import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator)
import os.path
import sys
import time

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

    output_file = open(input_file_name[:-4] + '_bpi.txt', 'w', newline='') # create file with "_out" postfix
    output_writer = csv.writer(output_file, delimiter='\t', quoting = csv.QUOTE_NONE, escapechar='', quotechar='')

    cmp_rpt_cnt = []

    for pattern in part_number:
        repeat_index = []
        for j in range(len(part_number)):
            if part_number[j] == pattern:
                repeat_index.append(j)
        print(repeat_index)

        cmp_rpt_cnt.append(repeat_index)

    for pattern in cmp_rpt_cnt:
        duplicate_count = 0
        duplicate_index = []
        for j in range(len(cmp_rpt_cnt)):
            if cmp_rpt_cnt[j] == pattern:
                duplicate_count += 1
                if duplicate_count > 1:
                    duplicate_index.append(j)

        for i in duplicate_index:
            cmp_rpt_cnt.pop(i)

    cmp_rpt_cnt.pop(0)

    for cmp_pn in cmp_rpt_cnt:
        part_number_ = part_number[cmp_pn[0]]
        qty = len(cmp_pn)
        mfr = manufacturer[cmp_pn[0]]
        if part_label[cmp_pn[0]] == '':
            value = ''
        else:
            value = '(' + str(part_label[cmp_pn[0]]) + ')'
        output_writer.writerow([part_number_,  '', '', mfr, '', qty, '', '', qty]) # write data into csv file
        if value != '':
            output_writer.writerow([value])  # write data into csv file
  
    output_file.close()  # close csv-file


if __name__ == '__main__':
    input_file_name = sys.argv[1]
    read_bom_template(input_file_name)
    t = time.time()
    write_csv(designator, component_type, part_number, part_label, manufacturer, quantity)
    print("%.6f" % (time.time()-t))
