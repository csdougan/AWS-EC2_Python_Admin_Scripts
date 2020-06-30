from __future__ import print_function
from ec2utils import *
from ec2snapshot import *
import xlsxwriter



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
		for instance in instances:
			instance_id,instance_name=instance
			print(instance_id,"\t",instance_name)	
			return_array.append(instance_id)
	

def main():
	region,awskeyid,awsseckey,outputfile,outtype=get_config_info('config_files/awsconfig.txt.ctrust_acc')
	SG_development,SG_preprod,SG_production=get_server_designations_by_sg('config_files/server_categories.txt')
	conn = connect_to_region(region,awskeyid,awsseckey)
	instance_obj_list=get_instance_references(conn)

	print("SG_development Servers :")
	display_instances(SG_development,instance_obj_list,conn)
	
	print("SG_preprod Servers :")
	display_instances(SG_preprod,instance_obj_list,conn)
	
	print("SG_production Servers :")
	display_instances(SG_production,instance_obj_list,conn)


if __name__ == "__main__":
	main()
