#!/usr/bin/python

# a file to convert randomly observed spot instance price to hourly price
# the output is written to the hourly_price dictionary where the key is hours since the epoch, and the value is the price in the time.
# The key in the hourly_price dictionary (hours) can be converted to a datetime object using hour_to_timestamp method

import sys, getopt, time, datetime
from collections import defaultdict
from dateutil.parser import parse

def hour_to_timestamp(hour):
    timestamp = datetime.datetime.fromtimestamp(hour * 3600)
    return timestamp

def convert_to_hourly_price(input_file, output_file):
    hourly_price = defaultdict(lambda:0.0, {})
    previous_record = defaultdict(lambda:-1, {})
    for line in reversed(open(input_file).readlines()):  # reading in the reverse order (the oldest one first
        price_time = line.rstrip().split()
        if len(price_time) < 2:
            continue
        new_price = float(price_time[0])
        current_second = int(time.mktime(parse(price_time[1]).timetuple()))
        current_hour = (current_second / 3600) 
        if (previous_record['seconds'] >= 0):
            if (previous_record['hour'] == current_hour): # no hour difference simply add the price
                hourly_price[current_hour] += ((current_second - previous_record['seconds']) / 3600.0 * previous_record['price'])
            elif (previous_record['hour'] < current_hour):
                processed_second = previous_record['seconds']
                for h in range(previous_record['hour'], current_hour):
                    hourly_price[h] += (((h+1)*3600 - processed_second)/3600.0) * previous_record['price']
                    processed_second = (h+1)*3600
                hourly_price[current_hour] += ((current_second - processed_second)/3600.0 * previous_record['price'])
            else:
                raise Exception("invalid hour entered old:%d new:%d",(previous_record['hour'], current_hour))

        previous_record['seconds'] = current_second
        previous_record['hour'] = current_hour
        previous_record['price'] = new_price
    
    for k in sorted(hourly_price):
        print hour_to_timestamp(k),hourly_price[k]


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


