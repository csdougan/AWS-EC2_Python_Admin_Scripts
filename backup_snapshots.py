from __future__ import print_function
from ec2utils import *
from ec2snapshot import *
import xlsxwriter



def get_instances_ids_in_sg(security_group,instance_list,conn):	
	instance_list=get_instance_references(conn)
	found_instances=[]
	for instanceobj in instance_list:
		for secgroup in instanceobj[0].groups:
			if secgroup.id == security_group:
				found_instances.append(instanceobj[0].id)
	return found_instances

def get_instances_obj_in_sg(security_group,instance_list,conn):	
	instance_list=get_instance_references(conn)
	found_instances=[]
	for instanceobj in instance_list:
		for secgroup in instanceobj[0].groups:
			if secgroup.id == security_group:
				found_instances.append(instanceobj)
	return found_instances

def get_server_designations_by_sg(configfile):
	global SG_DEVELOPMENT,SG_PREPROD,SG_PRODUCTION
	with open(configfile) as f:
		lines=f.readlines()
	SG_DEVELOPMENT=lines[0][12:].rstrip('\n').split(',')
	SG_PREPROD=lines[1][8:].rstrip('\n').split(',')
	SG_PRODUCTION=lines[2][11:].rstrip('\n').split(',')
	f.close()
	return [SG_DEVELOPMENT,SG_PREPROD,SG_PRODUCTION]



def display_instances(sg_array,instance_obj_list,conn):
	instances=[]
	for secgroup in sg_array:
		instances=get_instances_ids_in_sg(secgroup,instance_obj_list,conn)
		for instance_id in instances:
			instance_name=get_instance_name_by_id(conn,instance_id)
			print(instance_id,"\t",instance_name)	
			

def get_instance_ids_in_designation(sg_array,instance_obj_list,conn):
	return_array=[]
	for secgroup in sg_array:
		instances=get_instances_ids_in_sg(secgroup,instance_obj_list,conn)
		for instance_id in instances:
			return_array.append(instance_id)
	return return_array
	

def get_instance_obj_in_designation(sg_array,instance_obj_list,conn):
	return_array=[]
	for secgroup in sg_array:
		instances=get_instances_obj_in_sg(secgroup,instance_obj_list,conn)
		for instance in instances:
			instance_id,instance_name=instance
			print(instance_id,"\t",instance_name)	
			return_array.append(instance_id)

def number_of_snapshots_by_vol(instance_ids,conn):
	returnarray=[]
	for instance_id in instance_ids:
		volume_list=conn.get_all_volumes(filters={'attachment.instance-id' : instance_id})
		num_of_volumes=(len(volume_list))
		
		for v in volume_list:
			snapshots = conn.get_all_snapshots(filters={'volume_id' : v.id})
			num_of_snapshots = (len(snapshots))	
			returnarray.append([instance_id,v.id,num_of_snapshots])			
	return returnarray

def get_list_of_all_instance_ids(instance_obj_list):
	returnarray=[]
	for instance in instance_obj_list:
		returnarray.append(instance[0].id)
	return returnarray


def return_oldest_snapshots_for_vol(vol_id,num_of_snapshots_to_return,conn):
	snapshot_info=get_snapshot_info_by_volume_id(conn,vol_id)
	total_snapshots=len(snapshot_info)
	snapshots_to_ignore=total_snapshots-num_of_snapshots_to_return
	returnarray=[]
	for i in range (0,num_of_snapshots_to_return):
#	for i in range (snapshots_to_ignore,total_snapshots):
		returnarray.append(snapshot_info[i])
	return returnarray
	
		

def main():
	region,awskeyid,awsseckey,outputfile,outtype=get_config_info('config_files/awsconfig.txt.ctrust_acc')
	SG_development,SG_preprod,SG_production=get_server_designations_by_sg('config_files/server_categories.txt')
	conn = connect_to_region(region,awskeyid,awsseckey)
	instance_obj_list=get_instance_references(conn)

	print("**************************************************************************")

	# get list of ids for instances classed as production
	#instance_ids=get_instance_ids_in_designation(SG_production,instance_obj_list,conn)
	instance_ids=get_list_of_all_instance_ids(instance_obj_list)
	
	#get number of snapshots by vol for each instance id
	total_snaps_by_vol=number_of_snapshots_by_vol(instance_ids,conn)
	# set retention value
	RETENTION_VALUE=2
	#iterate through array
	snaps_to_remove=[]
	for record in total_snaps_by_vol:
		instance_id,volid,num_of_snapshots=record
		#print("Instance ID : ",instance_id,"Vol : ",volid,"# Snapshots:",num_of_snapshots)
		#check if num_of_snapshots exceeds retention value
		if num_of_snapshots > RETENTION_VALUE:
#			print("Instance ID : ",instance_id,"Vol : ",volid,"# Snapshots:",num_of_snapshots)
			# work out how many snapshots need to be removed
			num_of_snaps_to_delete = num_of_snapshots - RETENTION_VALUE
#			print("Vol : ",volid,"for Instance ",instance_id," has too many snapshots.")
#			print("There are",num_of_snapshots,"snapshots")
#			print("This is ",num_of_snaps_to_delete,"more than the retention value set.")
#			print("The current retention value is",RETENTION_VALUE)
			# get oldest snapshots
			oldestsnapshots=return_oldest_snapshots_for_vol(volid,num_of_snaps_to_delete,conn)
#			print("The snapshots to remove are :")
			for vid,snapid,snapdate,snaptime in oldestsnapshots:
#				print ("Snapshot id :",snapid,"Snap Date:",snapdate,"Snap Time:",snaptime)
				snaps_to_remove.append([instance_id,vid,snapid,snapdate,snaptime])
	print("Number of Snaps to retain is set to :",RETENTION_VALUE)
	iids_with_snaps_to_remove=set([iid for iid,vid,sid,sd,st in snaps_to_remove])
	for iids in iids_with_snaps_to_remove:
		sids=[sid for iid,vid,sid,sd,st in snaps_to_remove if iid==iids]
		print("Instance ID : ",iids,"has",len(sids),"snapshots to remove")
		print("\tThe details for these are:")
		for iid,vid,sid,sd,st in snaps_to_remove:
			if iid==iids:			
				print("Volid:",vid,"Snapid:",sid,"SnapDate:",sd,"SnapTime:",st)
	#iids_with_snaps_to_remove=set([iid for iid,vid,sid,sd,st in snaps_to_remove if iid == 'i-466ec90b'])


			
			
		
	


if __name__ == "__main__":
	main()


