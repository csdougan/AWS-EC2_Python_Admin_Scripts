#!/usr/bin/python
from __future__ import print_function
from ec2_class import *
import xlsxwriter
import sys


def list_summary_instance_info_xls(outputfile,myEC2Class):
	workbook = xlsxwriter.Workbook(outputfile)
	worksheet = workbook.add_worksheet()	
	printheader=True
	row=0
	col_width=[]
	for current_instance_object in myEC2Class.instance_objects:
		displaystring=""
		headerstring=""
		displaystring += myEC2Class.get_instance_name(current_instance_object) + "|"
		headerstring += "Instance Name" + "|"
		displaystring += myEC2Class.get_instance_id(current_instance_object) + "|"
		headerstring += "Instance ID" + "|"
		displaystring += myEC2Class.get_instance_instance_type(current_instance_object) + "|"	
		headerstring += "Type" + "|"	
		displaystring += myEC2Class.get_instance_placement(current_instance_object) + "|"	
		headerstring += "Placement" + "|"	
		displaystring += myEC2Class.get_instance_ipaddr(current_instance_object) + "|"	
		headerstring += "IP Address" + "|"	
		displaystring += myEC2Class.get_instance_prvipaddr(current_instance_object) + "|"	
		headerstring += "Private IP Address" + "|"	
		displaystring += myEC2Class.get_instance_key_name(current_instance_object) + "|"	
		headerstring += "Key Name" + "|"	
		displaystring += myEC2Class.get_instance_secgroup(current_instance_object) + "|"
		headerstring += "Security Group(s)" + "|"	
		displaystring += myEC2Class.get_instance_rootdevname(current_instance_object) + "|"
		headerstring += "Root Device Name" + "|"	
		displaystring += myEC2Class.get_instance_rootdevtype(current_instance_object) + "|"
		headerstring += "Root Device Type" + "|"	
		displaystring += myEC2Class.get_instance_blockmap(current_instance_object) + "|"
		headerstring += "Block Device Mapping" + "|"	
		displaystring += myEC2Class.get_instance_state(current_instance_object) + "|"
		headerstring += "State" + "|"
		displaystring += myEC2Class.get_instance_creation_datetime(current_instance_object) + "|"
		headerstring += "Date/Time Created" + "|"
		displaystring += myEC2Class.get_instance_launch_datetime(current_instance_object) + "|"	
		headerstring += "Date/Time Last Launched" + "|"
		displaystring += myEC2Class.get_instance_stop_datetime(current_instance_object) + "|"	
		headerstring += "Date/Time Stopped" + "|"
		displaystring += myEC2Class.retrieve_tags_in_csv_format(current_instance_object)
		headerstring += myEC2Class.list_tags_in_header_format()
		if printheader:
			headerstring=headerstring.split('|')
			col=0
			for headercell in headerstring:
				worksheet.write(row,col,headercell)
				col_width.append(len(headercell))
				worksheet.set_column(col,col,(col_width[col])+1)
				col += 1
			printheader = False
			row += 1
		displaystring=displaystring.split('|')
		col=0
		for rowcell in displaystring:
			if (len(rowcell) > col_width[col]):
				col_width[col]=len(rowcell)
				worksheet.set_column(col,col,(col_width[col])+1)
			worksheet.write(row,col,rowcell)
			col += 1
		row += 1
	workbook.close()

def main():
	region,awskeyid,awsseckey=get_config_info('config_files/awsconfig.txt.ctrust_acc')
	myEC2Class = EC2Utils(region,awskeyid,awsseckey)
	outputfile = sys.argv[1]
	list_summary_instance_info_xls(outputfile,myEC2Class)

if __name__ == "__main__":
	main()

