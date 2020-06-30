#!/usr/bin/python
from __future__ import print_function
from ec2_class import *
import xlsxwriter
import sys
import datetime

def main():
	timestamp = datetime.datetime.now().strftime('%d-%m-%Y')	
	
	home = os.path.expanduser("~")
	output_dir = home + '/reports/'
	if not os.path.exists(output_dir):
		    os.makedirs(output_dir)
	for output_type in "csv","xlsx":
		if not os.path.exists(output_dir + output_type):
			os.makedirs(output_dir + output_type)


	region,awskeyid,awsseckey=get_config_info(home + '/.aws_config/awsconfig.txt.ctrust_acc')
	myEC2Class = EC2Utils(region,awskeyid,awsseckey)


if __name__ == "__main__":
	main()

