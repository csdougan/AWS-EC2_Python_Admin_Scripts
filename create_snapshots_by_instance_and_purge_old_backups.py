#!/usr/bin/python
from __future__ import print_function
from ec2_class import *
from time import strftime, gmtime
import xlsxwriter

global logToConsole=False

datestamp = datetime.datetime.now().strftime('%d%m%Y')	
timestamp = datetime.datetime.now().strftime('%H%M%S')

	
home = os.path.expanduser("~")
output_dir = home + '/reports/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
if not os.path.exists(output_dir + '/xlsx/'):
	os.makedirs(output_dir + '/xlsx/')
if not os.path.exists(output_dir + '/csv/'):
	os.makedirs(output_dir + '/csv/')
if not os.path.exists(home + '/log/'):
	os.makedirs(home + '/log/')

logfile_name = home + '/log/' + 'scheduled_backup_run.' + datestamp + '.' + timestamp + '.log';


def logme(string_to_log,logfile_name):
	if (logToConsole=True):
		print(string_to_log)
	logfile_object = open(logfile_name,'a',0)
	logfile_object.write(string_to_log + "\n")
	logfile_object.close()

	


def get_snapshots_to_remove(myEC2Class,default_retention_value,specified_instances=[]):
	snaps_to_remove=[]
	specified_instance_ids=[]

	if len(specified_instances) == 0:
		specified_instances = myEC2Class.instance_details

	for record in myEC2Class.volume_details:
		in_backup_policy=False
		volid,volobj,volblkd,insid,insobj,num_of_total_snaps=record
		number_of_backup_snaps=0

		for sid,sno,vid,vo,iid,io,sd,st,ubami,amiid,svex,ioex,amex,sndesc in myEC2Class.snapshot_details:
	        	if vid == volid:
				if 'Backup_Type' in sno.__dict__['tags']:
					if sno.__dict__['tags']['Backup_Type'] == 'Scheduled':
                               			number_of_backup_snaps += 1

		for specified_instance in specified_instances:
			i_id = specified_instance[0]
			i_obj = specified_instance[2]
			i_name = specified_instance[1]
			retention_value = default_retention_value
			if i_id == insid:
				logme("\n" + volid +" on "+ i_name + " (" + i_id + ") : Checking if Scheduled Backup Policy is to be applied..",logfile_name)
				if 'Apply_Scheduled_Backup_Policy' in i_obj.__dict__['tags']:
					logme("\tApply_Scheduled_Backup_Policy tag found",logfile_name)
					if i_obj.__dict__['tags']['Apply_Scheduled_Backup_Policy'].lower() == "yes":
						logme("\tScheduled Backup Policy is applied to " + i_name +" (" + i_id + ")",logfile_name)
						if 'Backup_Retention' in i_obj.__dict__['tags']:
							logme("\tBackup retention value found",logfile_name)
							retention_value = int(i_obj.__dict__['tags']['Backup_Retention'])
							logme("\tRetention value is now :" + str(retention_value),logfile_name)
						logme("\tTotal snapshots of volume : " + str(num_of_total_snaps),logfile_name)			
						logme("\tTotal snapshots created by scheduled backup policy : " + str(number_of_backup_snaps),logfile_name)			
						if number_of_backup_snaps > retention_value:
							num_of_snaps_to_delete = number_of_backup_snaps - retention_value
							logme("\tNumber of backup snapshots to delete : " + str(num_of_snaps_to_delete),logfile_name)
							oldest_snapshots=myEC2Class.return_oldest_snapshots_to_delete_for_vol(volid,num_of_snaps_to_delete)
							for vid,snapid,snapdate,snaptime in oldest_snapshots:
								snaps_to_remove.append([insid,vid,snapid,snapdate,snaptime,number_of_backup_snaps,retention_value])
						else:
							logme("\tNumber of snapshots to delete : 0",logfile_name)				
	return snaps_to_remove	


def get_backup_volumes(myEC2Class,specified_instances=[]):
	snaps_created=[]
	specified_instance_ids=[]
	if len(specified_instances) == 0:
		specified_instances = myEC2Class.instance_details

	for record in myEC2Class.volume_details:
		volid,volobj,volblkd,insid,insobj,num_of_snaps=record
		for specified_instance in specified_instances:
			i_id = specified_instance[0]
			i_name = specified_instance[1]
			i_obj = specified_instance[2]
			if i_id == insid:
				if 'Backup_Retention' in i_obj.__dict__['tags']:
					retention_value = int(i_obj.__dict__['tags']['Backup_Retention'])
				if 'Apply_Scheduled_Backup_Policy' in i_obj.__dict__['tags']:
					if i_obj.__dict__['tags']['Apply_Scheduled_Backup_Policy'].lower() == "yes":
						timestamp=strftime("%d-%m-%Y %H:%M:%S", gmtime())
						created_snapshot=volobj.create_snapshot()
						created_snapshot.add_tags({'Name': 'Scheduled Backup of ' + i_name + ' (' + i_id + ') ' + timestamp , 'Instance_ID' : i_id, 'Volume_ID'  : volid,'Backup_Type' : 'Scheduled' })						
						snapid=created_snapshot.id
						snapdate,snaptime=str(created_snapshot.start_time)[:19].split('T')
						snaps_created.append([i_name,insid,volid,snapid,snapdate,snaptime])
	return snaps_created

def delete_snapshots(myEC2Class,snaps_to_remove):
	deleted_snapshots=[]
	for snap_to_remove in snaps_to_remove:
		for snapshots in myEC2Class.snapshot_details:
			# check ids match up - we do this to find out the object for the snapshot being deleted			
			if snap_to_remove[2] == snapshots[0]:
				logme("Deleting " + snapshots[0] + " of volume " + snapshots[2] + " (" + str(snapshots[5].__dict__['tags']['Name']) + ")...",logfile_name)				
				snapshots[1].delete()
				deleted_snapshots.append(snapshots)
	return deleted_snapshots


def get_EC2_totals_for_backup_policy_usage(myEC2Class):
	total_snapshots_created_other=0
	total_snapshots_created_by_backup_policy=0
	total_instances_backup_policy_off=0
	total_instances_backup_policy_on=0
	total_instances_backup_policy_unset=0

	for snaps_detail in myEC2Class.snapshot_details:
		sna_obj=snaps_detail[1]
		if 'Backup_Type' in sna_obj.__dict__['tags']:
			if sna_obj.__dict__['tags']['Backup_Type'] == "Scheduled":
				total_snapshots_created_by_backup_policy += 1
			else:
				total_snapshots_created_other += 1
		else:
			total_snapshots_created_other += 1

	for instance_detail in myEC2Class.instance_details:
		i_obj = instance_detail[2]
		if 'Apply_Scheduled_Backup_Policy' in i_obj.__dict__['tags']:
			if i_obj.__dict__['tags']['Apply_Scheduled_Backup_Policy'].lower() == "yes":
				total_instances_backup_policy_on += 1
			else:
				total_instances_backup_policy_off += 1
		else:
			total_instances_backup_policy_unset += 1
		
	return [total_snapshots_created_by_backup_policy,total_snapshots_created_other,total_instances_backup_policy_on,total_instances_backup_policy_off,total_instances_backup_policy_unset]


def main():
	global myEC2Utils
	region,awskeyid,awsseckey,awsaccountid=get_config_info(home + '/.aws_config/awsconfig.txt.ctrust_acc')
	myEC2Class = EC2Utils(region,awskeyid,awsseckey,awsaccountid)
	retention_value=2
	totals_array=[]
	if not os.path.exists(output_dir + "Snapshots_Created_By_Scheduled_Backup/csv"):
		os.makedirs(output_dir + "Snapshots_Created_By_Scheduled_Backup/csv")
	if not os.path.exists(output_dir + "Snapshots_Created_By_Scheduled_Backup/xlsx"):
		os.makedirs(output_dir + "Snapshots_Created_By_Scheduled_Backup/xlsx")
	if not os.path.exists(output_dir + "Totals_for_scheduled_backup_run/csv"):
		os.makedirs(output_dir + "Totals_for_scheduled_backup_run/csv")
	if not os.path.exists(output_dir + "Totals_for_scheduled_backup_run/xlsx"):
		os.makedirs(output_dir + "Totals_for_scheduled_backup_run/xlsx")
	logme("-------------------------------------------------------------",logfile_name)
	logme("Scheduled Backup Run : " + datetime.datetime.now().strftime("%A %D @ %T"),logfile_name)
	logme("-------------------------------------------------------------",logfile_name)
	logme("Total snapshots existing pre backup process : " + str(len(myEC2Class.snapshot_details)),logfile_name)
	totals_array.append(["Total Snapshots Pre Backup Process : ",len(myEC2Class.snapshot_details)])
	logme("Starting Scheduled Backup Process.....",logfile_name)
	created_snaps=get_backup_volumes(myEC2Class)
	logme("Total new snapshots creared by backup process : " + str(len(created_snaps)),logfile_name)
	totals_array.append(["Total new snaps created by backup process : ", len(created_snaps)])
	header=['Instance Id','Instance Name','Volume ID','Snapshot ID','Snapshot Date','Snapshot Time']
	outputfile = output_dir + 'Snapshots_Created_By_Scheduled_Backup/' + 'xlsx/' + datestamp + '_' + timestamp + '_Snapshots_Created_By_Scheduled_Backup.xlsx'
	logme("\nCreating Excel report containing details about created snapshots",logfile_name)
	myEC2Class.generate_report_from_array(outputfile,header,created_snaps,"Snapshots_Created")
	outputfile = output_dir + 'Snapshots_Created_By_Scheduled_Backup/' + 'csv/' + datestamp + '_' + timestamp + '_Snapshots_Created_By_Scheduled_Backup.csv'
	myEC2Class.generate_report_from_array(outputfile,header,created_snaps,"Snapshots_Created")
	logme("\nRefreshing Snapshot Information to get latest backup information",logfile_name)
	myEC2Class.update()
	logme("\nStarting Process to Delete old backups....",logfile_name)
	total_pre_deletion=len(myEC2Class.snapshot_details)
	totals_array.append(["Total Pre Deletion",total_pre_deletion])
	logme("Total of all snapshots (pre deletion): " + str(total_pre_deletion),logfile_name)
	snaps_to_remove=get_snapshots_to_remove(myEC2Class,retention_value)
	logme("\nTotal number of snapshots to be deleted : " + str(len(snaps_to_remove)),logfile_name)
	totals_array.append(["Total Snapshots to be Deleted",len(snaps_to_remove)])
	logme("\nDeleting old backups....",logfile_name)		
	deleted_snapshots=delete_snapshots(myEC2Class,snaps_to_remove)
	logme("\nRefreshing Snapshot Information after deletion..",logfile_name)
	myEC2Class.update()
	total_post_deletion=len(myEC2Class.snapshot_details)
	total_deleted=total_pre_deletion-total_post_deletion
	logme("\nTotal Snapshots successfully deleted : " + str(total_deleted),logfile_name)
	totals_array.append(["Total snapshot Successfully Deleted",total_deleted])
	logme("Total of all snapshots (post deletion): " + str(total_post_deletion),logfile_name)
	totals_array.append(["Total of all snapshots (post deletion)",total_post_deletion])
	tscb,tsco,tibe,tibo,tibu=get_EC2_totals_for_backup_policy_usage(myEC2Class)
	logme("Total Snapshots in EC2 created by backup policy : " + str(tscb),logfile_name)
	totals_array.append(["Total Snapshots in EC2 created using backup policy",tscb])
	logme("Total Snapshots in EC2 not created by backup policy : " + str(tsco),logfile_name)
	totals_array.append(["Total Snapshots in EC2 not created using backup policy",tsco])
	logme("Total Instances in EC2 with backup policy applied : " + str(tibe),logfile_name)
	totals_array.append(["Total Instances in EC2 with backup policy applied",tibe])
	logme("Total Instances in EC2 with backup policy turned off : " + str(tibo),logfile_name)
	totals_array.append(["Total Instances in EC2 with backup policy turned off",tibo])
	logme("Total Instances in EC2 with backup policy unset : " + str(tibu),logfile_name)
	totals_array.append(["Total Instances in EC2 with backup policy unset",tibu])
	header=['Total Type','Total']
	logme("\nCreating Totals report file",logfile_name)
	outputfile = output_dir + 'Totals_for_scheduled_backup_run/' + 'xlsx/' + datestamp + '_' + timestamp + '_Totals_for_scheduled_backup_run.xlsx'
	myEC2Class.generate_report_from_array(outputfile,header,totals_array,"Backup Policy Totals")
	outputfile = output_dir + 'Totals_for_scheduled_backup_run/' + 'csv/' + datestamp + '_' + timestamp + '_Totals_for_scheduled_backup_run.csv'
	myEC2Class.generate_report_from_array(outputfile,header,totals_array,"Backup Policy Totals")
	logme("",logfile_name)
	logme("-------------------------------------------------------------",logfile_name)
	logme("Finished Backup Run : " + datetime.datetime.now().strftime("%A %D @ %T"),logfile_name)
	logme("-------------------------------------------------------------",logfile_name)


if __name__ == "__main__":
	main()


