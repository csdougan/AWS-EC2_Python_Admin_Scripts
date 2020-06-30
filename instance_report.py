#!/usr/bin/python
from __future__ import print_function
from ec2_class import *
import xlsxwriter
import sys
import datetime

def main():
	timestamp = datetime.datetime.now().strftime('%d%m%Y')	
	
	home = os.path.expanduser("~")
	output_dir = home + '/reports/'
	if not os.path.exists(output_dir):
		    os.makedirs(output_dir)

	region,awskeyid,awsseckey,awsaccountid=get_config_info(home + '/.aws_config/awsconfig.txt.ctrust_acc')
	myEC2Class = EC2Utils(region,awskeyid,awsseckey,awsaccountid)

	header=['Instance Name','Instance ID','Type','Placement','IP Address','Private IP Address','Key Name','Security Group(s)','Root Device Name','Root Device Type','Block Device Mapping','State','Date/Time Created','Date/Time Last Launched','Date/Time Stopped']
	for tag in myEC2Class.alltags:
		header.append("[Tag] " + tag)
	input_array=[]
	for current_instance_object in myEC2Class.instance_objects:
		line_array=[]
		line_array.append(myEC2Class.get_instance_name(current_instance_object))
		line_array.append(myEC2Class.get_instance_id(current_instance_object))
		line_array.append(myEC2Class.get_instance_instance_type(current_instance_object))
		line_array.append(myEC2Class.get_instance_placement(current_instance_object))
		line_array.append(myEC2Class.get_instance_ipaddr(current_instance_object))
		line_array.append(myEC2Class.get_instance_prvipaddr(current_instance_object))
		line_array.append(myEC2Class.get_instance_key_name(current_instance_object))
		line_array.append(myEC2Class.get_instance_secgroup(current_instance_object))
		line_array.append(myEC2Class.get_instance_rootdevname(current_instance_object))
		line_array.append(myEC2Class.get_instance_rootdevtype(current_instance_object))
		line_array.append(myEC2Class.get_instance_blockmap(current_instance_object))
		line_array.append(myEC2Class.get_instance_state(current_instance_object))
		line_array.append(myEC2Class.get_instance_creation_datetime(current_instance_object))
		line_array.append(myEC2Class.get_instance_launch_datetime(current_instance_object))
		line_array.append(myEC2Class.get_instance_stop_datetime(current_instance_object))

		for knowntag in myEC2Class.alltags:
			knowntag_value=myEC2Class.get_instance_tag_info(current_instance_object,knowntag)
			line_array.append(knowntag_value)
		input_array.append(line_array)

	for output_type in "csv", "xlsx":
		if not os.path.exists(output_dir + "AWS_Instance_Details/" + output_type):
			os.makedirs(output_dir + "AWS_Instance_Details/" + output_type)
		output_file = output_dir + "AWS_Instance_Details/" + output_type + "/" + timestamp + "_AWS_Instance_Details." + output_type
		myEC2Class.generate_report_from_array(output_file,header,input_array,"AWS Instance Info")

if __name__ == "__main__":
	main()

