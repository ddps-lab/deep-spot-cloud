#!/usr/bin/python

import sys, getopt
from os import listdir
from os.path import isfile,join
from convert_to_hour import convert_to_hourly_price

def read_files_in_directory(in_dir, out_dir):
    for f in listdir(in_dir):
        if isfile(join(in_dir, f)):
            convert_to_hourly_price(join(in_dir, f), join(out_dir, f))


def main(argv):
    input_path = ""
    output_path = ""
    try:
        opts, args = getopt.getopt(argv,"h:i:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'generate_test_hourly_logs.py -i <input path> -o <output path>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'generate_test_hourly_logs.py -i <input path> -o <output path>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_path = arg
        elif opt in ("-o", "--ofile"):
            output_path = arg
    read_files_in_directory(input_path, output_path)

if __name__ == "__main__":
   main(sys.argv[1:]) 


