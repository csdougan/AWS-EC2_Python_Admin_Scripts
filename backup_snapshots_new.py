from __future__ import print_function
from ec2_class import *
import xlsxwriter

def main():
	global myEC2Utils
	region,awskeyid,awsseckey=get_config_info('config_files/awsconfig.txt.ctrust_acc')
	myEC2Utils=EC2Utils(region,awskeyid,awsseckey)
	retention_value=1
	snaps_to_delete=myEC2Utils.get_snapshots_to_remove(retention_value)
	header=['instance id','volume id','snapshot id','snapshot date','snapshot time']
	myEC2Utils.generate_report_from_array('csvtest.csv',header,snaps_to_delete)
	myEC2Utils.generate_report_from_array('xlsxtest.xlsx',header,snaps_to_delete)


if __name__ == "__main__":
	main()


