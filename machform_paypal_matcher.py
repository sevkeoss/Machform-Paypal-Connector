import glob
import os
from os import path
import csv
import numpy as np

paypal_id_col = []
id_list = []
writer = None
paypal_dict = {}
payment_dict = {}
output_header = np.array(['Trans Type', 'Trans ID', 'Date', 'Currency', 'Gross', 'Fee', 'Net', 'Name', 'Misc. Fields'])
grand_gross_total = 0
grand_fee_total = 0
grand_net_total = 0


def run():
    global grand_gross_total
    global grand_fee_total
    global grand_net_total

    if output_file_exists():
        print("ERROR: Financial Output File.csv already exists. Please delete it before running this program.")
        return
    else:
        read_paypal_data()
        read_payment_data()
        find_non_matches()
        write_data(np.array(['', '', '', '', "{0:,.2f}".format(grand_gross_total), "{0:,.2f}".format(grand_fee_total),
                             "{0:,.2f}".format(grand_net_total)]))


def output_file_exists():
    return True if path.exists('Financial Output File.csv') else False


def read_payment_data():
    global id_list

    curr_path = os.getcwd()
    payment_files = glob.glob(curr_path + '/*.csv')
    write_data(output_header)
    for payment_file in payment_files:
        if payment_file != (curr_path + '/PayPal.csv'):
            with open(payment_file, 'r', encoding='ISO-8859-1') as p_file:
                next(p_file)
                reader = csv.reader(p_file, delimiter=',')
                for row in reader:
                    if len(row) == 0 or row[6] == '':
                        continue
                    id_list.append(row[6])
                    payment_dict.update({row[6]: row})
            find_matches()
            del id_list[:]


def read_paypal_data():
    global paypal_id_col

    with open('PayPal.csv', 'r', encoding='ISO-8859-1') as paypal_file:
        next(paypal_file)
        reader = csv.reader(paypal_file, delimiter=',')
        for row in reader:
            if len(row) == 0:
                continue
            paypal_dict.update({row[12]: np.array(row)})
            paypal_id_col.append(row[12])
    paypal_id_col.sort()


def find_matches():
    global paypal_dict
    global grand_gross_total
    global grand_fee_total
    global grand_net_total

    elements_removal = []
    gross_total = 0
    fee_total = 0
    net_total = 0
    for paypal_id in paypal_id_col:
        for id in id_list:
            if paypal_id == id:
                payment_data = payment_dict.get(id)
                paypal_data = paypal_dict.get(paypal_id)
                gross_total, fee_total, net_total = update_totals(paypal_data, gross_total, fee_total, net_total)

                misc_data = np.char.split(payment_data[8:], ',')
                write_data(np.array([payment_data[7], payment_data[6], paypal_data[0], paypal_data[4], paypal_data[5],
                                     paypal_data[6], paypal_data[7], paypal_data[11], *(col[0] for col in misc_data)]))
                elements_removal.append(id)
                break

    update_grand_totals(gross_total, fee_total, net_total)
    write_data(['', '', '', '', "{0:,.2f}".format(gross_total), "{0:,.2f}".format(fee_total),
                "{0:,.2f}".format(net_total)])

    for element in elements_removal:
        paypal_id_col.remove(element)


def find_non_matches():
    global paypal_id_col

    gross_total = 0
    fee_total = 0
    net_total = 0

    for paypal_id in paypal_id_col:
        data = paypal_dict.get(paypal_id)
        gross_total, fee_total, net_total = update_totals(data, gross_total, fee_total, net_total)
        write_data(np.array(['**NO MATCH**', paypal_id, data[0], data[4], data[5], data[6], data[7], data[11]]))

    update_grand_totals(gross_total, fee_total, net_total)
    write_data(np.array(['', '', '', '', "{0:,.2f}".format(gross_total), "{0:,.2f}".format(fee_total),
                         "{0:,.2f}".format(net_total)]))


def update_totals(data, gross_total, fee_total, net_total):
    gross_total = gross_total + float(data[7].replace(',', ''))
    fee_total = fee_total + float(data[8].replace(',', ''))
    net_total = net_total + float(data[9].replace(',', ''))

    return gross_total, fee_total, net_total


def update_grand_totals(gross_total, fee_total, net_total):
    global grand_gross_total
    global grand_fee_total
    global grand_net_total

    grand_gross_total = grand_gross_total + gross_total
    grand_fee_total = grand_fee_total + fee_total
    grand_net_total = grand_net_total + net_total


def write_data(data):
    global writer

    with open('Financial Output File.csv', 'a', encoding='ISO-8859-1') as writeFile:
        writer = csv.writer(writeFile, lineterminator='\r')
        writer.writerow(data)


run()
