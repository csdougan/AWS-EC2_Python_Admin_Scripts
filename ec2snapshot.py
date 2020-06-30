from __future__ import print_function
from ec2utils import *
import operator
import xlsxwriter


# Create snapshots of all volumes attached to an instance specified by its id
def create_snapshots_by_instance_id(conn,instance_id):
	volumes = conn.get_all_volumes(filters={'attachment.instance-id' : instance_id})	
	snapshots=[]
	for v in volumes:
		snapshots.append(v.create_snapshot())
	return snapshots


def create_snapshot_by_volume_id(conn,volume_id):
	volume = conn.get_all_volumes(filters={'volume-id' : volume_id})	
	new_snap=volume[0].create_snapshot()
	return new_snap.id

## This function returns the following fields -
## <Volume ID>, <Snap ID>, <Snap Date>, <Snap Time>
def get_snapshot_info_by_volume_id(conn,volume_id):
	snapshots = conn.get_all_snapshots(filters={'volume_id' : volume_id})	
	snaplist=[]	
	for s in snapshots:
		snapdate,snaptime=str(s.start_time)[:19].split('T')
		snaplist.append([volume_id,s.id,snapdate,snaptime])
	snaplist=sorted(snaplist, key=operator.itemgetter(0,2,3),reverse=False)
	return snaplist

def get_latest_snapshot_info_by_instance_id(conn,instance_id,displaytype="all"):
	instance_name=get_instance_name_by_id(conn,instance_id)	
	volume_list=conn.get_all_volumes(filters={'attachment.instance-id' : instance_id})	
	instance_snaplist=[]
	for v in volume_list:
		snaps_by_vol_list=get_snapshot_info_by_volume_id(conn,v.id)
		if (len(snaps_by_vol_list) > 0):
			if (displaytype != "none"):
				instance_snaplist.append([instance_id,instance_name] + snaps_by_vol_list[len(snaps_by_vol_list)-1])
		else:
			if (displaytype != "exists"):
				instance_snaplist.append([instance_id,instance_name,v.id,"<none found>","<N/A>","<N/A>"])
	return instance_snaplist

## This function returns the following fields -
## <Instance ID>, <Instance Name>, <Volume ID>, <Snap ID>, <Snap Date>, <Snap Time>
def get_full_snapshot_info_by_instance_id(conn,instance_id,displaytype="all"):
	instance_name=get_instance_name_by_id(conn,instance_id)	
	volume_list=conn.get_all_volumes(filters={'attachment.instance-id' : instance_id})	
	instance_snaplist=[]
	for v in volume_list:
		snaps_by_vol_list=get_snapshot_info_by_volume_id(conn,v.id)
		if (len(snaps_by_vol_list) == 1):
				instance_snaplist.append([instance_id,instance_name] + snaps_by_vol_list[0])		
		elif (len(snaps_by_vol_list) > 1):
			for snap_info in snaps_by_vol_list:
				instance_snaplist.append([instance_id,instance_name] + snap_info)
		else:
			if (displaytype != "exists"):
				instance_snaplist.append([instance_id,instance_name,v.id, "<none found>","<N/A>","<N/A>"])
	return instance_snaplist
		
## This function returns the following fields -
## <Instance ID>, <Instance Name>, <Volume ID>, <Snap ID>, <Snap Date>, <Snap Time>
def list_instances_and_snapshot_info(conn,displaytype="latest"):
	instance_obj_list=get_instance_references(conn)
	outputarray=[]
	for ins_obj in instance_obj_list:
		if (displaytype == "full"):
			all_snaps_for_instance_list=get_full_snapshot_info_by_instance_id(conn,ins_obj[0].id,"all")
		else:
			all_snaps_for_instance_list=get_latest_snapshot_info_by_instance_id(conn,ins_obj[0].id,"all")
		for individual_snap_info in all_snaps_for_instance_list:

			outputarray.append(individual_snap_info)
	return outputarray



def get_list_of_all_instance_ids(conn):
	instance_list = get_instance_references(conn)
	returnlist=[]
	for instances in instance_list:
		returnlist.append(instances[0].id)
	return returnlist

def main():
	print("nothing here")


if __name__ == "__main__":
	main()

