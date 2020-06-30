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

	latest_input_array=myEC2Class.list_instances_and_snapshot_info("latest-all")
	found_input_array=myEC2Class.list_instances_and_snapshot_info("latest-found")
	notfound_input_array=myEC2Class.list_instances_and_snapshot_info("latest-notfound")
	full_input_array=myEC2Class.list_instances_and_snapshot_info("full")

	for output_type in "csv", "xlsx":
		if not os.path.exists(output_dir + "Latest_Snapshot_Info_for_All_Volumes/" + output_type):
			os.makedirs(output_dir + "Latest_Snapshot_Info_for_All_Volumes/" + output_type)
		if not os.path.exists(output_dir + "Latest_Snapshot_Info_for_All_Volumes__Missing_Snapshots_Excluded/" + output_type):
			os.makedirs(output_dir + "Latest_Snapshot_Info_for_All_Volumes__Missing_Snapshots_Excluded/" + output_type)
		if not os.path.exists(output_dir + "Latest_Snapshot_Info_for_All_Volumes__Missing_Snapshots_Only/" + output_type):
			os.makedirs(output_dir + "Latest_Snapshot_Info_for_All_Volumes__Missing_Snapshots_Only/" + output_type)
		if not os.path.exists(output_dir + "Every_Available_Snapshot_for_Volumes/" + output_type):
			os.makedirs(output_dir + "Every_Available_Snapshot_for_Volumes/" + output_type)

		if not os.path.exists(output_dir + "Snapshots_Used_By_AMI_Images/" + output_type):
			os.makedirs(output_dir + "Snapshots_Used_By_AMI_Images/" + output_type)

		if not os.path.exists(output_dir + "Orphaned_Snapshots/" + output_type):
			os.makedirs(output_dir + "Orphaned_Snapshots/" + output_type)

		if not os.path.exists(output_dir + "All_Snapshots_Including_Volume_AMI_and_Orphaned/" + output_type):
			os.makedirs(output_dir + "All_Snapshots_Including_Volume_AMI_and_Orphaned/" + output_type)

#Ec2Utils.snapshot_details = [0<snapshot id>,1<snapshot object>,2<volume id>,3<volume object>,4<instance id>,5<instance obj>6<snapdate>7<snaptime>,8<used by AMI>,9<AMI Id>,10<Source Vol Exists?>,11<Instance Obj Exists?>,12<AMI Exists?>,13<Snapshot Description>]	
	
		ami_input_array=[]
		for snapInfo in myEC2Class.snapshot_details:
			if snapInfo[8] == "yes":
				if snapInfo[12] == "yes":
					amiName=""	
					for amiObject in myEC2Class.ami_objects:
						if amiObject.id == snapInfo[9]:
							amiName=amiObject.name
								#AMI ID, AMI Name?, Snap ID, Vol ID, Snap Date, Snap Time, Snap Description
					volID="<none>"					
					if "vol-" in snapInfo[2]:
						volID=snapInfo[2]				
					ami_input_array.append([snapInfo[9],amiName,snapInfo[0],volID,snapInfo[6],snapInfo[7],snapInfo[13]])
		
		orphaned_input_array=[]
		for snapInfo in myEC2Class.snapshot_details:
			if snapInfo[10] != "yes":
				if snapInfo[8] != "yes": # if snapshot isnt used by ami...
					# 1:<snap id>, 2:<snapdate> 3:<snaptime> 4:<used by ami?> 5:<source vol exists?> 6:<ami exists?>
					orphaned_input_array.append([snapInfo[0],snapInfo[6],snapInfo[7],snapInfo[8],snapInfo[10],"N/A"])
				else:
					if snapInfo[12] != "yes":
						# 1:<snap id>, 2:<snapdate> 3:<snaptime> 4:<used by ami?> 5:<source vol exists?> 6:<ami exists?>
						orphaned_input_array.append([snapInfo[0],snapInfo[6],snapInfo[7],snapInfo[8],snapInfo[10],snapInfo[12]])

#	Ec2Utils.snapshot_details = [0<snapshot id>,1<snapshot object>,2<volume id>,3<volume object>,4<instance id>,5<instance obj>6<snapdate>7<snaptime>,8<used by AMI>,9<AMI Id>,10<Source Vol Exists?>,11<Instance Obj Exists?>,12<AMI Exists?>,13<Snapshot Description>]	
		fullinfo_input_array=[]
		for fullinfo in myEC2Class.snapshot_details:
			fullinfo_input_array.append([fullinfo[0],fullinfo[2],fullinfo[4],fullinfo[6],fullinfo[7],fullinfo[8],fullinfo[9],fullinfo[10],fullinfo[11],fullinfo[12],fullinfo[13]])

		
		header = ["Snap ID", "Volume ID", "Instance ID", "Snap Date", "Snap Time", "Used by AMI?", "AMI ID", "Source Vol Exists?", "Instance Exists?", "AMI Exists?", "Snap Description"]
		myEC2Class.generate_report_from_array(output_dir + "All_Snapshots_Including_Volume_AMI_and_Orphaned/" + output_type + "/" + timestamp + "_All_Snapshots_Including_Volume_AMI_and_Orphaned." + output_type,header,fullinfo_input_array,worksheet_title='All Inc AMI Orphan')
		header = ["Snap ID", "Snap Date", "Snap Time", "Used by AMI", "Source Vol Exists?", "AMI Exists?"]
		myEC2Class.generate_report_from_array(output_dir + "Orphaned_Snapshots/" + output_type + "/" + timestamp + "_Orphaned_Snapshots." + output_type,header,orphaned_input_array,worksheet_title='Orphaned_Snapshots')	

		header = ["AMI ID","AMI Name","Snap ID","Vol ID","Snap Date","Snap Time","Snapshot Description"]
		myEC2Class.generate_report_from_array(output_dir + "Snapshots_Used_By_AMI_Images/" + output_type + "/" + timestamp + "_Snapshots_Used_By_AMI_Images." + output_type,header,ami_input_array,worksheet_title='AMI Image Snapshots')

		header = ["Instance ID","Instance Name","Volume ID","Snap ID","Snap Date","Snap Time","Snapshot Description","Total Snapshots Available"]
		myEC2Class.generate_report_from_array(output_dir + "Latest_Snapshot_Info_for_All_Volumes/" + output_type + "/" + timestamp + "_Latest_Snapshot_Info_for_All_Volumes." + output_type,header,latest_input_array,worksheet_title='latest Info Full')
		myEC2Class.generate_report_from_array(output_dir + "Latest_Snapshot_Info_for_All_Volumes__Missing_Snapshots_Excluded/" + output_type  + "/" + timestamp + "_Latest_Snapshot_Info_for_All_Volumes__Missing_Snapshots_Excluded." + output_type,header,found_input_array,worksheet_title='latest Snapshots Found')
		myEC2Class.generate_report_from_array(output_dir + "Latest_Snapshot_Info_for_All_Volumes__Missing_Snapshots_Only/" + output_type + "/" + timestamp + "_Latest_Snapshot_Info_for_All_Volumes__Missing_Snapshots_Only." + output_type,header,notfound_input_array,worksheet_title='Missing Snapshots')
		header = ["Instance ID","Instance Name","Volume ID","Snap ID","Snap Date","Snap Time","Snapshot Description"]
		myEC2Class.generate_report_from_array(output_dir + "Every_Available_Snapshot_for_Volumes/" + output_type + "/" + timestamp +  "_Every_Available_Snapshot_for_Volumes." + output_type,header,full_input_array,worksheet_title='All Snapshot Info')

if __name__ == "__main__":
	main()


