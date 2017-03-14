#!/usr/bin/python

import sys, getopt
from dateutil.parser import parse

def convert_to_hourly_price(input_file, output_file):
    previous_record = {'year':-1, 'month':-1, 'day':-1, 'hour':-1, 'minute':-1, 'second':-1, 'price':-1}
    for line in reversed(open(input_file).readlines()):  # reading in the reverse order (the oldest one first
        price_time = line.rstrip().split("\t")
        price = float(price_time[0])
        timestamp = parse(price_time[1])
        if previous_record['year'] > 0:
            minute_passed

def main(argv):
    input_file_path = "us-west-2b_g2.2xlarge_linux"
    output_file_path = "hourly-us-west-2b_g2.2xlarge_linux"
    try:
        opts, args = getopt.getopt(argv,"h:i:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'convert_to_hour.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'convert_to_hour.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file_path = arg
        elif opt in ("-o", "--ofile"):
            output_file_path = arg
    print 'Input file is ', input_file_path
    print 'Output file is ', output_file_path
    convert_to_hourly_price(input_file_path, output_file_path)

if __name__ == "__main__":
   main(sys.argv[1:]) 


