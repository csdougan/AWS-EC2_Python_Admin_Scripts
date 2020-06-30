#!/usr/bin/python
from __future__ import print_function
from ec2_class import *
import xlsxwriter
import sys

def generate_excel_snapshot_report(outputfile,myEC2Class):
	all_row=1
	no_row=1
	exist_row=1
	full_row=1
	workbook = xlsxwriter.Workbook(outputfile)
	worksheet_all_ins = workbook.add_worksheet('Latest Snapshot - All Instances')	
	worksheet_snaps_exist = workbook.add_worksheet('Latest Snapshot - Snap Exists')
	worksheet_no_snaps = workbook.add_worksheet('Instances with No Snapshots')
	worksheet_full_snaps = workbook.add_worksheet('Full Snapshot List by Instances')
	latest_record_list = myEC2Class.list_instances_and_snapshot_info("latest")
	full_record_list = myEC2Class.list_instances_and_snapshot_info("full")	
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
	region,awskeyid,awsseckey=get_config_info('config_files/awsconfig.txt.ctrust_acc')
	myEC2Class = EC2Utils(region,awskeyid,awsseckey)
	outputfile = sys.argv[1]
	generate_excel_snapshot_report(outputfile,myEC2Class)

if __name__ == "__main__":
	main()


