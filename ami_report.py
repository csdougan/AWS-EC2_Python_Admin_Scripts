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


	region,awskeyid,awsseckey,awsaccountid=get_config_info(home + '/.aws_config/awsconfig.txt.ctrust_acc')
	myEC2Class = EC2Utils(region,awskeyid,awsseckey)
	amiImages=myEC2Class.conn.get_all_images(filters={'owner_id' : awsaccountid})
	amiImageArray=[]
	header=['amiId','amiLocation','amiState','amiOwnerId','amiOwnerAlias','amiis_public','amiArchitecture','amiPlatform','amiType','amiKernelId','amiRamDiskID','amiName','amiDescription','amiBlockDevMap','amiRootDevName','amiVirtType','amiHypervisor','amiInsLifeCycle','amiSriovNet','amiImageArray']


#Ec2Utils.snapshot_details = [<snapshot id>,<snapshot object>,<volume id>,<volume object>,<instance id>,<instance obj><snapdate><snaptime>]
	counter=0
	for snapshot in myEC2Class.snapshot_details:
		counter += 1
		snapDesc = snapshot[1].description
		if snapDesc.find("ami-") == -1:
			print(counter," : Not an AMI Snapshot : Desc = ",snapDesc)
		else:
			print(counter," : AMI Snapshot : Description = ",snapDesc)

	
	for amiImage in amiImages:
		amiId = amiImage.id
		amiLocation = amiImage.location
		amiState = amiImage.state
		amiOwnerId = amiImage.owner_id
		amiOwnerAlias = amiImage.owner_alias
		amiis_public = amiImage.is_public
		amiArchitecture = amiImage.architecture
		amiPlatform = amiImage.platform
		amiType = amiImage.type
		amiKernelId = amiImage.kernel_id
		amiRamDiskID = amiImage.ramdisk_id
		amiName = amiImage.name
		amiDescription = amiImage.description
		amiBlockDevMap = amiImage.block_device_mapping
		amiSnapshotId = amiImage.block_device_mapping.current_value.snapshot_id
		amiRootDevType = amiImage.root_device_type
		amiRootDevName = amiImage.root_device_name
		amiVirtType = amiImage.virtualization_type
		amiHypervisor = amiImage.hypervisor
		amiInsLifeCycle = amiImage.instance_lifecycle
		amiSriovNet = amiImage.sriov_net_support
		amiImageArray.append([amiId,amiLocation,amiState,amiOwnerId,amiOwnerAlias,amiis_public,amiArchitecture,amiPlatform,amiType,amiKernelId,amiRamDiskID,amiName,amiDescription,amiBlockDevMap,amiRootDevName,amiVirtType,amiHypervisor,amiInsLifeCycle,amiSriovNet,amiSnapshotId])

	for output_type in "csv","xlsx":
		output_file = output_dir + output_type + "/AMI_Image_Details." + timestamp + "." + output_type
		myEC2Class.generate_report_from_array(output_file,header,amiImageArray,"AMI Image Info")


if __name__ == "__main__":
	main()

