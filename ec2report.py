from __future__ import print_function
from ec2utils import *
from ec2snapshot import *
import xlsxwriter
#ec2report.py


def list_full_instance_info_csv(conn,instance_list,OUTPUTFILE):
	taglist=build_master_tag_list(instance_list)
	printheader=True
	for instances in instance_list:
		displaystring=""
		headerstring=""
		displaystring += get_instance_name(instances) + "|"
		headerstring += "Instance Name" + "|"
		displaystring += get_instance_id(instances) + "|"
		headerstring += "Instance ID" + "|"
		displaystring += get_instance_pubdns(instances) + "|"	
		headerstring += "Public DNS" + "|"
		displaystring += get_instance_prvdns(instances) + "|"	
		headerstring += "Private DNS" + "|"		
		displaystring += get_instance_state(instances) + "|"
		headerstring += "State" + "|"	
		displaystring += get_instance_state_code(instances) + "|"
		headerstring += "State Code" + "|"		
		displaystring += get_instance_key_name(instances) + "|"	
		headerstring += "Key Name" + "|"	
		displaystring += get_instance_instance_type(instances) + "|"	
		headerstring += "Type" + "|"	
		displaystring += get_instance_launch_time(instances) + "|"
		headerstring += "Launch Time" + "|"		
		displaystring += get_instance_image_id(instances) + "|"	
		headerstring += "Image ID" + "|"	
		displaystring += get_instance_placement(instances) + "|"	
		headerstring += "Placement" + "|"	
		displaystring += get_instance_place_group(instances) + "|"	
		headerstring += "Placement Group" + "|"	
		displaystring += get_instance_place_tenancy(instances) + "|"	
		headerstring += "Placement Tenancy" + "|"	
		displaystring += get_instance_kernel(instances) + "|"	
		headerstring += "Kernel" + "|"	
		displaystring += get_instance_ramdisk(instances) + "|"	
		headerstring += "Ramdisk" + "|"	
		displaystring += get_instance_arch(instances) + "|"	
		headerstring += "Architecture" + "|"	
		displaystring += get_instance_hyperv(instances) + "|"	
		headerstring += "Hypervistor" + "|"	
		displaystring += get_instance_vtype(instances) + "|"	
		headerstring += "Virtualization Type" + "|"	
		displaystring += get_instance_prodcode(instances) + "|"	
		headerstring += "Product Code" + "|"	
		displaystring += get_instance_amiindex(instances) + "|"	
		headerstring += "AMI Launch Index" + "|"	
		displaystring += get_instance_monitored(instances) + "|"	
		headerstring += "Monitored" + "|"	
		displaystring += get_instance_spotreqid(instances) + "|"	
		headerstring += "Spot Instance Req ID" + "|"	
		displaystring += get_instance_subnetid(instances) + "|"			
		headerstring += "Subnet ID" + "|"	
		displaystring += get_instance_vpcid(instances) + "|"	
		headerstring += "VPC ID" + "|"	
		displaystring += get_instance_ipaddr(instances) + "|"	
		headerstring += "IP Address" + "|"	
		displaystring += get_instance_prvipaddr(instances) + "|"	
		headerstring += "Private IP Address" + "|"	
		displaystring += get_instance_platform(instances) + "|"
		headerstring += "Platform" + "|"	
		displaystring += get_instance_rootdevname(conn,instances) + "|"
		headerstring += "Root Device Name" + "|"	
		displaystring += get_instance_rootdevtype(instances) + "|"
		headerstring += "Root Device Type" + "|"	
		displaystring += get_instance_blockmap(conn,instances) + "|"
		headerstring += "Block Device Mapping" + "|"	
		displaystring += get_instance_state_reason(instances) + "|"
		headerstring += "State Reason" + "|"	
		displaystring += get_instance_secgroup(instances) + "|"
		headerstring += "Security Group(s)" + "|"	
		displaystring += get_instance_interfaces(instances) + "|"
		headerstring += "Interfaces" + "|"	
		displaystring += get_instance_ebs_opt(instances) + "|"
		headerstring += "EBS Optimized" + "|"	
		displaystring += get_instance_profile(instances) + "|"
		headerstring += "Profile" + "|"	
		displaystring += retrieve_tags_in_csv_format(instances,taglist)
		headerstring += list_tags_in_header_format(taglist)
		if printheader:
			print(headerstring)
			printheader = False
		print(displaystring)



def list_summary_instance_info_csv(conn,instance_list,OUTPUTFILE):
	f = open(OUTPUTFILE,'w')
	taglist=build_master_tag_list(instance_list)
	printheader=True
	for instances in instance_list:
		displaystring=""
		headerstring=""
		displaystring += get_instance_name(instances) + "|"
		headerstring += "Instance Name" + "|"
		displaystring += get_instance_id(instances) + "|"
		headerstring += "Instance ID" + "|"
		displaystring += get_instance_instance_type(instances) + "|"	
		headerstring += "Type" + "|"	
		displaystring += get_instance_placement(instances) + "|"	
		headerstring += "Placement" + "|"	
		displaystring += get_instance_ipaddr(instances) + "|"	
		headerstring += "IP Address" + "|"	
		displaystring += get_instance_prvipaddr(instances) + "|"	
		headerstring += "Private IP Address" + "|"	
		displaystring += get_instance_key_name(instances) + "|"	
		headerstring += "Key Name" + "|"	
		displaystring += get_instance_secgroup(instances) + "|"
		headerstring += "Security Group(s)" + "|"	
		displaystring += get_instance_rootdevname(conn,instances) + "|"
		headerstring += "Root Device Name" + "|"	
		displaystring += get_instance_rootdevtype(instances) + "|"
		headerstring += "Root Device Type" + "|"	
		displaystring += get_instance_blockmap(conn,instances) + "|"
		headerstring += "Block Device Mapping" + "|"	
		displaystring += get_instance_state(instances) + "|"
		headerstring += "State" + "|"
		displaystring += retrieve_tags_in_csv_format(instances,taglist)
		headerstring += list_tags_in_header_format(taglist)
		if printheader:
			f.write(headerstring + '\n')
			printheader = False
		f.write(displaystring + '\n')
	f.close()

def list_summary_instance_info_xls(conn,instance_list,OUTPUTFILE):

	workbook = xlsxwriter.Workbook(OUTPUTFILE)
	worksheet = workbook.add_worksheet()	
	
	taglist=build_master_tag_list(instance_list)
	printheader=True
	row=0
	col_width=[]
	for instances in instance_list:
		displaystring=""
		headerstring=""
		displaystring += get_instance_name(instances) + "|"
		headerstring += "Instance Name" + "|"
		displaystring += get_instance_id(instances) + "|"
		headerstring += "Instance ID" + "|"
		displaystring += get_instance_instance_type(instances) + "|"	
		headerstring += "Type" + "|"	
		displaystring += get_instance_placement(instances) + "|"	
		headerstring += "Placement" + "|"	
		displaystring += get_instance_ipaddr(instances) + "|"	
		headerstring += "IP Address" + "|"	
		displaystring += get_instance_prvipaddr(instances) + "|"	
		headerstring += "Private IP Address" + "|"	
		displaystring += get_instance_key_name(instances) + "|"	
		headerstring += "Key Name" + "|"	
		displaystring += get_instance_secgroup(instances) + "|"
		headerstring += "Security Group(s)" + "|"	
		displaystring += get_instance_rootdevname(conn,instances) + "|"
		headerstring += "Root Device Name" + "|"	
		displaystring += get_instance_rootdevtype(instances) + "|"
		headerstring += "Root Device Type" + "|"	
		displaystring += get_instance_blockmap(conn,instances) + "|"
		headerstring += "Block Device Mapping" + "|"	
		displaystring += get_instance_state(instances) + "|"
		headerstring += "State" + "|"
		displaystring += get_instance_creation_datetime(conn,instances) + "|"
		headerstring += "Date/Time Created" + "|"
		displaystring += get_instance_launch_datetime(instances) + "|"	
		headerstring += "Date/Time Last Launched" + "|"
		displaystring += get_instance_stop_datetime(instances) + "|"	
		headerstring += "Date/Time Stopped" + "|"
		displaystring += retrieve_tags_in_csv_format(instances,taglist)
		headerstring += list_tags_in_header_format(taglist)
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

def generate_excel_snapshot_report(conn,OUTPUTFILE):
	all_row=1
	no_row=1
	exist_row=1
	full_row=1
	workbook = xlsxwriter.Workbook(OUTPUTFILE)
	worksheet_all_ins = workbook.add_worksheet('Latest Snapshot - All Instances')	
	worksheet_snaps_exist = workbook.add_worksheet('Latest Snapshot - Snap Exists')
	worksheet_no_snaps = workbook.add_worksheet('Instances with No Snapshots')
	worksheet_full_snaps = workbook.add_worksheet('Full Snapshot List by Instances')
	latest_record_list = list_instances_and_snapshot_info(conn,"latest")
	full_record_list = list_instances_and_snapshot_info(conn,"full")	
	col_width_all = []
	col_width_no = []
	col_width_exist = []
	col_width_full = []
	col=0	
	for header_cell in "Instance ID","Instance Name","Volume ID","Snap ID","Snap Date","Snap Time":
		worksheet_all_ins.write(0,col,header_cell)
		worksheet_all_ins.set_column(0,col,len(header_cell)+1)
		worksheet_snaps_exist.write(0,col,header_cell)
		worksheet_snaps_exist.set_column(0,col,len(header_cell)+1)
		worksheet_no_snaps.write(0,col,header_cell)
		worksheet_no_snaps.set_column(0,col,len(header_cell)+1)
		worksheet_full_snaps.write(0,col,header_cell)
		worksheet_full_snaps.set_column(0,col,len(header_cell)+1)
		col_width_all.append(len(header_cell))
		col_width_exist.append(len(header_cell))
		col_width_no.append(len(header_cell))
		col_width_full.append(len(header_cell))

		col += 1

	for record_line in latest_record_list:
		col=0
		for cell in record_line:	
			if (len(cell) > col_width_all[col]):
				col_width_all[col]=len(cell)
				worksheet_all_ins.set_column(col,col,(col_width_all[col])+1)
			worksheet_all_ins.write(all_row,col,cell)
			col += 1		
		all_row += 1
		if record_line[3]=="<none found>":
			col=0		
			for cell in record_line:
				if (len(cell) > col_width_no[col]):
					col_width_no[col]=len(cell)
					worksheet_no_snaps.set_column(col,col,(col_width_no[col])+1)
				worksheet_no_snaps.write(no_row,col,cell)
				col += 1		
			no_row += 1
		else:
			col=0		
			for cell in record_line:
				if (len(cell) > col_width_exist[col]):
					col_width_exist[col]=len(cell)
					worksheet_snaps_exist.set_column(col,col,(col_width_exist[col])+1)
				worksheet_snaps_exist.write(exist_row,col,cell)
				col += 1		
			exist_row += 1


	for record_line in full_record_list:
		col=0
		for cell in record_line:
			if (len(cell) > col_width_full[col]):
				col_width_full[col]=len(cell)
				worksheet_full_snaps.set_column(col,col,(col_width_full[col])+1)
			worksheet_full_snaps.write(full_row,col,cell)
			col+=1
		full_row+=1


	col=0		
	for col_length in col_width_all:
		worksheet_all_ins.set_column(col,col,col_length+1)
		col += 1
	col=0
	for col_length in col_width_exist:
		worksheet_snaps_exist.set_column(col,col,col_length+1)
		col += 1
	col=0
	for col_length in col_width_no:
		worksheet_no_snaps.set_column(col,col,col_length+1)
		col += 1
	col=0
	for col_length in col_width_full:
		worksheet_full_snaps.set_column(col,col,col_length+1)
		col += 1
	workbook.close()


def main():
	REGION,AWSKEYID,AWSSECKEY,OUTPUTFILE,OUTTYPE=get_config_info('config_files/awsconfig.txt.ctrust_acc')
	conn = connect_to_region(REGION,AWSKEYID,AWSSECKEY)
	instance_obj_list=get_instance_references(conn)
	if (OUTTYPE == "csv"):
		list_summary_instance_info_csv(conn,instance_obj_list,OUTPUTFILE)
	elif (OUTTYPE == "xls") or (OUTTYPE == "xlsx"):
		list_summary_instance_info_xls(conn,instance_obj_list,OUTPUTFILE)
	else:
		print("Output File type not recognised")
	#generate_excel_snapshot_report(conn,'AWS_Snapshot_Info.xlsx')

if __name__ == "__main__":
	main()

