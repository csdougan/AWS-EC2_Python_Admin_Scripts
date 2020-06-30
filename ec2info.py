from __future__ import print_function
import boto
import boto.ec2
import xlsxwriter

from boto.ec2.connection import EC2Connection

# The following line turns on debugging
#boto.set_stream_logger('boto')

# The following reads in the AWS region, Key and Secret Key from a config file
# The structure of the file needs to be as follows -
#REGION=eu-west-1
#AWSKEYID=abcdef1234567adsgd
#AWSSECKEY=ab12b1b39ejfsdkdskdskfdsfid8dd
#OUTPUTFILE=somefile.xls

def get_config_info():
	global REGION,AWSKEYID,AWSSECKEY,OUTPUTFILE,OUTTYPE
	with open('../config_files/awsconfig.txt') as f:
		lines=f.readlines()
	REGION=lines[0][7:].rstrip('\n')
	AWSKEYID=lines[1][9:].rstrip('\n')
	AWSSECKEY=lines[2][10:].rstrip('\n')
	OUTPUTFILE=lines[3][11:].rstrip('\n')
	OUTTYPE=OUTPUTFILE.split(".")[1]
	f.close()


def connect_to_region(region_name):
	ec2conn = boto.ec2.connect_to_region(region_name,aws_access_key_id=AWSKEYID,aws_secret_access_key=AWSSECKEY)
	return ec2conn

def get_available_regions():
	conn = connect_to_ec2()
	check_regions = boto.ec2.regions() 
	available_regions=[]
	for regionname in check_regions:
		regsub=str(regionname)[11:]	
		available_regions.append(regsub)
	return available_regions		

def get_instance_status():
	reservation=get_reservations()
	instance_list=get_reservation_detail(reservation)
	return instance_list

def get_reservations():
	reservation_info=conn.get_all_reservations()
	return reservation_info

def get_reservation_detail(reservation_info):
	instance_info=[]	
	for reservations in reservation_info:
		instance_info.append(reservations.instances)
	return instance_info

# The following section defines the functions for retrieving instance information

def get_instance_id(instances):
	return str(instances[0].id)

def get_instance_pubdns(instances):	
	return str(instances[0].public_dns_name)

def get_instance_prvdns(instances):			
	return str(instances[0].private_dns_name)

def get_instance_state(instances):	
	return str(instances[0].state)

def get_instance_state_code(instances):	
	return str(instances[0].state_code)

def get_instance_key_name(instances):	
	return str(instances[0].key_name)

def get_instance_instance_type(instances):	
	return str(instances[0].instance_type)

def get_instance_launch_time(instances):	
	return str(instances[0].launch_time)

def get_instance_image_id(instances):	
	return str(instances[0].image_id)

def get_instance_placement(instances):	
	return str(instances[0].placement)

def get_instance_place_group(instances):	
	return str(instances[0].placement_group)

def get_instance_place_tenancy(instances):	
	return str(instances[0].placement_tenancy)

def get_instance_kernel(instances):	
	return str(instances[0].kernel)

def get_instance_ramdisk(instances):	
	return str(instances[0].ramdisk)

def get_instance_arch(instances):	
	return str(instances[0].architecture)

def get_instance_hyperv(instances):	
	return str(instances[0].hypervisor)

def get_instance_vtype(instances):	
	return str(instances[0].virtualization_type)

def get_instance_prodcode(instances):	
	return str(instances[0].product_codes)

def get_instance_amiindex(instances):	
	return str(instances[0].ami_launch_index)

def get_instance_monitored(instances):	
	return str(instances[0].monitored)

def get_instance_spotreqid(instances):	
	return str(instances[0].spot_instance_request_id)

def get_instance_subnetid(instances):			
	return str(instances[0].subnet_id)

def get_instance_vpcid(instances):	
	return str(instances[0].vpc_id)

def get_instance_ipaddr(instances):	
	return str(instances[0].ip_address)

def get_instance_prvipaddr(instances):	
	return str(instances[0].private_ip_address)

def get_instance_platform(instances):
	return str(instances[0].platform)

def get_instance_rootdevname(instances):
	rootdevname=instances[0].root_device_name
	blockmaplist=get_instance_blockmap(instances)
	returnstring="<MISSING>"
	for bd in blockmaplist.split(", "):
		bdname, bdid = bd.strip(")").split(" (")
		if (bdname == rootdevname):
			returnstring=bd
	return str(returnstring)


def get_instance_rootdevtype(instances):
	return str(instances[0].root_device_type)

def get_instance_blockmap(instances):
	volume_list=conn.get_all_volumes(filters={'attachment.instance-id' : instances[0].id})
	returnstring=""
	counter=1
	for v in volume_list:
		returnstring += v.attach_data.device + " (" + str(v.id) + ")"
		if (counter < len(volume_list)):
			returnstring += ", "
		counter += 1
	return str(returnstring)

def get_instance_state_reason(instances):
	return str(instances[0].state_reason)

# Security Group Attributes that can be called are as follows -
# secgroup.id = Security ID
# secgroup.name = Security Name

def get_instance_secgroup(instances):
	secgrouplist=""
	counter=1
	for secgroup in instances[0].groups:
		secgrouplist += str(secgroup.name) + " (" + str(secgroup.id) + ")"
		if (counter < len(instances[0].groups)):
			secgrouplist += ", "
		counter += 1
	return str(secgrouplist)

def get_instance_interfaces(instances):
	return str(instances[0].interfaces)

def get_instance_ebs_opt(instances):
	return str(instances[0].ebs_optimized)

def get_instance_profile(instances):
	return str(instances[0].instance_profile)

# The following code is to retrieve the instance tag info
# there isn't currently a standard set of tags set so instead we use a 'master list' of
# all the currently existing tags across all instances and iterate through this to see
# if a tag is used for the current instance being queried.
# If it is used an entry is written into the relevant tag column - if not the column field is
# set to <none>.

def get_instance_tag_info(instances,tagtocheckfor):
	stringtoreturn=""	
	for tag_type, tag_value in instances[0].__dict__['tags'].items():
		if tag_type == tagtocheckfor:				
			stringtoreturn=tag_value
	return stringtoreturn

def get_instance_name(instances):
	if 'Name' in instances[0].__dict__['tags']:
		returnstring=instances[0].__dict__['tags']['Name']
	else:
		returnstring="<none>"
	return returnstring

def retrieve_tags_in_csv_format(instances,taglist):
	counter=1
	stringtoreturn=""		
	for knowntag in taglist:
		stringtoreturn += get_instance_tag_info(instances,knowntag)
		if (counter < len(taglist)):		
			stringtoreturn += "|"
		counter += 1
	return stringtoreturn

def build_master_tag_list(instance_list):
	taglist=[]
	for instances in instance_list:
		for tag_type, tag_value in instances[0].__dict__['tags'].items():
			tagexists=False
			for knowntag in taglist:
				if tag_type == knowntag:
					tagexists=True
			if tagexists == False:
				taglist.append(tag_type)
	taglist.sort()
	return taglist

def list_tags_in_header_format(taglist):
	counter=1
	stringtoreturn=""
	for tag in taglist:
		stringtoreturn += "[Tag] " + tag
		if (counter < len(taglist)):
			stringtoreturn += "|"
		counter += 1
	return stringtoreturn




def list_full_instance_info_csv(instance_list):
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
		displaystring += get_instance_rootdevname(instances) + "|"
		headerstring += "Root Device Name" + "|"	
		displaystring += get_instance_rootdevtype(instances) + "|"
		headerstring += "Root Device Type" + "|"	
		displaystring += get_instance_blockmap(instances) + "|"
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



def list_summary_instance_info_csv(instance_list):
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
		displaystring += get_instance_rootdevname(instances) + "|"
		headerstring += "Root Device Name" + "|"	
		displaystring += get_instance_rootdevtype(instances) + "|"
		headerstring += "Root Device Type" + "|"	
		displaystring += get_instance_blockmap(instances) + "|"
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

def list_summary_instance_info_xls(instance_list):

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
		displaystring += get_instance_rootdevname(instances) + "|"
		headerstring += "Root Device Name" + "|"	
		displaystring += get_instance_rootdevtype(instances) + "|"
		headerstring += "Root Device Type" + "|"	
		displaystring += get_instance_blockmap(instances) + "|"
		headerstring += "Block Device Mapping" + "|"	
		displaystring += get_instance_state(instances) + "|"
		headerstring += "State" + "|"
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


def main():
	global conn, workbook

	get_config_info()
	conn = connect_to_region(REGION)
	instance_list=get_instance_status()

	if (OUTTYPE == "csv"):
		list_summary_instance_info_csv(instance_list)
	elif (OUTTYPE == "xls") or (OUTTYPE == "xlsx"):
		list_summary_instance_info_xls(instance_list)
	else:
		print("Output File type not recognised")

if __name__ == "__main__":
	main()

