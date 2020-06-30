from __future__ import print_function
import boto
import datetime
import operator
import xlsxwriter
import boto.ec2
import os.path
from boto.ec2.connection import EC2Connection

def get_config_info(configfile):
	with open(configfile) as f:
		lines=f.readlines()
	region=lines[0][7:].rstrip('\n')
	awskeyid=lines[1][9:].rstrip('\n')
	awsseckey=lines[2][10:].rstrip('\n')
	awsaccountid=lines[3][10:].rstrip('\n')
	f.close()
	return [region,awskeyid,awsseckey,awsaccountid]	

'''
	Ec2Utils.conn = connection object for class
	Ec2Utils.available_regions = array of available regions
	Ec2Utils.reservations = array of reservation objects 
	Ec2Utils.instance_objects = array of all instance objects available
	
	Ec2Utils.snapshot_objects = array of all snapshot objects available
	#Ec2Utils.volume_objects = array of all volume objects available
	#Ec2Utils.volume_details = [<volume id>,<volume object>,<volume block device>,<instance id>,<instance obj>,<number of snaps>]
	#Ec2Utils.snapshot_details = [<snapshot id>,<snapshot object>,<volume id>,<volume object>,<instance id>,<instance obj><snapdate><snaptime>,<used by AMI>,<AMI Id>,<Source Vol Exists?>,<Instance Obj Exists?>,<AMI Exists?>,<Snapshot Description>]
	#Ec2Utils.instance_details = [<instance id>,<instance name>,<instance object>,<launchdate>,<launchtime>,<createdate>,<createtime>,<stopdate>,<stoptime>,<root dev name>,<root dev id>]
'''	

class EC2Utils:
	def __init__(self,region,awskeyid,awsseckey,awsaccountid):
		self.conn = boto.ec2.connect_to_region(region,aws_access_key_id=awskeyid,aws_secret_access_key=awsseckey)
		self.awsaccountid = awsaccountid
		self.update()

	def update(self):
		self.available_regions=[]
		self.reservations=self.conn.get_all_reservations()
		self.instance_objects=[]
		for reservation in self.reservations:
			for instance in reservation.instances:
				self.instance_objects.append(instance)		
		self.volume_objects=self.conn.get_all_volumes()	
		self.snapshot_objects=self.conn.get_all_snapshots(owner='self')
		self.snapshot_details=[]
		self.instance_details=[]
		self.volume_details=[]
		self.alltags=[]
		self.ami_objects=self.conn.get_all_images(filters={'owner_id' : self.awsaccountid})
		check_regions = boto.ec2.regions() 

		for regionname in check_regions:
			regsub=str(regionname)[11:]	
			self.available_regions.append(regsub)


		self.snapshot_details=[]
		for s in self.snapshot_objects:
			volid=""
			volobj=None
			insid=""
			instance_object=None							
			sourceVolExists="no"
			insObjExists="no"
			amiImgExists="no"
			usedByAmi="no"
			amiImgID=""

			snapDesc=s.description

			findAmiInDesc=snapDesc.find("ami-")
			if findAmiInDesc != -1:
				usedByAmi="yes"
				amiImgID=snapDesc[findAmiInDesc:].split(' ')[0]
				for amiImage in self.ami_objects:
					if amiImage.id == amiImgID:
						amiImgExists="yes"
					
			for v in self.volume_objects:
				if s.volume_id == v.id:
					sourceVolExists="yes"
					volid=v.id
					volobj=v
					for i in self.instance_objects: 
						if i.id == v.attach_data.instance_id:
							instance_object=i
							insObjExists="yes"
							insid = i.id
			snapdate,snaptime=str(s.start_time)[:19].split('T')		
			#create array containing snapshot id, snapshot object, volume id, volume object,
			# instance id, instance object, snap date, snap time, 
			# used by ami image, ami image id, source vol exists,ins obj exists,ami image exists,snapDesc
			self.snapshot_details.append([s.id,s,volid,volobj,insid,instance_object,snapdate,snaptime,usedByAmi,amiImgID,sourceVolExists,insObjExists,amiImgExists,snapDesc])		
		self.snapshot_details=sorted(self.snapshot_details, key=operator.itemgetter(0,2,4,6,7),reverse=False)
		
		for v in self.volume_objects:
			instance_object=None
			for i in self.instance_objects: 
				if i.id == v.attach_data.instance_id:
					instance_object=i
			num_of_snaps=0			
			for s in self.snapshot_details:
				if s[2] == v.id:
					num_of_snaps+=1
				
			self.volume_details.append([v.id,v,v.attach_data.device,v.attach_data.instance_id,instance_object,num_of_snaps])
		self.volume_details=sorted(self.volume_details, key=operator.itemgetter(0,3),reverse=False)
		#build_master_tag_list(self,instance_list):
		self.alltags=[]

		for i in self.instance_objects:
			for tag_type, tag_value in i.__dict__['tags'].items():
				tagexists=False
				for knowntag in self.alltags:
					if tag_type == knowntag:
						tagexists=True
				if tagexists == False:
					self.alltags.append(tag_type)
		self.alltags.sort()

		self.instance_details=[]
		for i in self.instance_objects:
		# Launch date and time
			launchdate,launchtime="-","-"
			if i.launch_time:
				launchdate=i.launch_time[:19].split('T')[0]
				launchtime=i.launch_time[:19].split('T')[1]
				launchdate=datetime.datetime.strptime(launchdate, '%Y-%m-%d').strftime('%d/%m/%y')

		# Instance name (specified by 'Name' tag if it exists)
			iname=""	
			if 'Name' in i.__dict__['tags']:
				iname=i.__dict__['tags']['Name']
			else:
				iname="<none>"
			
		# get_instance_creation_datetime(self,instance):
			root_device = i.root_device_name
			createdate="-"
			createtime="-"

			root_vol = [vo for vid,vo,vd,iid,io,ns in self.volume_details if vd==root_device and iid==i.id]
			if len(root_vol) != 0:
				createdate=root_vol[0].create_time[:19].split('T')[0]
				createtime=root_vol[0].create_time[:19].split('T')[1]
				createdate=datetime.datetime.strptime(createdate, '%Y-%m-%d').strftime('%d/%m/%y')

		### get_instance_stop_datetime(self,instance):
			stopdate="-"
			stoptime="-"
			if i.reason:
				stopdate=i.reason.split("(")[1].split(' ')[0]
				stopdate=datetime.datetime.strptime(stopdate, '%Y-%m-%d').strftime('%d/%m/%y')		
				stoptime=i.reason.split("(")[1].split(' ')[1]


			root_dev_id = "-"
			for v in self.volume_details:
				if i.root_device_name == v[2]:
					root_dev_id = v[0]

		# Build the instance details array			
			self.instance_details.append([i.id,iname,i,launchdate,launchtime,createdate,createtime,stopdate,stoptime,i.root_device_name,root_dev_id])

	def get_instance_id(self,instance):
		return str(instance.id)

	def get_instance_pubdns(self,instance):	
		return str(self,instance.public_dns_name)

	def get_instance_prvdns(self,instance):			
		return str(instance.private_dns_name)

	def get_instance_state(self,instance):	
		return str(instance.state)

	def get_instance_state_code(self,instance):	
		return str(instance.state_code)

	def get_instance_key_name(self,instance):	
		return str(instance.key_name)

	def get_instance_instance_type(self,instance):	
		return str(instance.instance_type)

	def get_instance_launch_time(self,instance):
		return str(instance.launch_time)

	def get_instance_image_id(self,instance):	
		return str(instance.image_id)

	def get_instance_placement(self,instance):	
		return str(instance.placement)

	def get_instance_place_group(self,instance):	
		return str(instance.placement_group)

	def get_instance_place_tenancy(self,instance):	
		return str(instance.placement_tenancy)

	def get_instance_kernel(self,instance):	
		return str(instance.kernel)

	def get_instance_ramdisk(self,instance):	
		return str(instance.ramdisk)

	def get_instance_arch(self,instance):	
		return str(instance.architecture)

	def get_instance_hyperv(self,instance):	
		return str(instance.hypervisor)

	def get_instance_vtype(self,instance):	
		return str(instance.virtualization_type)

	def get_instance_prodcode(self,instance):	
		return str(instance.product_codes)

	def get_instance_amiindex(self,instance):	
		return str(instance.ami_launch_index)

	def get_instance_monitored(self,instance):	
		return str(instance.monitored)

	def get_instance_spotreqid(self,instance):	
		return str(instance.spot_instance_request_id)

	def get_instance_subnetid(self,instance):			
		return str(instance.subnet_id)

	def get_instance_vpcid(self,instance):	
		return str(instance.vpc_id)

	def get_instance_ipaddr(self,instance):	
		return str(instance.ip_address)

	def get_instance_prvipaddr(self,instance):	
		return str(instance.private_ip_address)

	def get_instance_platform(self,instance):
		return str(instance.platform)

	def get_instance_rootdevname(self,instance):
		rootdevname=instance.root_device_name
		blockmaplist=self.get_instance_blockmap(instance)
		returnstring="-"
		for bd in blockmaplist.split("), "):
			bdname, bdid = bd.strip(")").split(" (")
			if (bdname == rootdevname):
				returnstring=bd
		return str(returnstring)

	def get_instance_rootdevtype(self,instance):
		return str(instance.root_device_type)

	def get_instance_blockmap(self,instance):
		volume_list = [v[1] for v in self.volume_details if v[3] == instance.id]
		returnstring=""
		counter=1
		for v in volume_list:
			returnstring += v.attach_data.device + " (" + str(v.id) + ", " + str(v.size) + "GB)"	
			if (counter < len(volume_list)):
				returnstring += ", "
			counter += 1
		return str(returnstring)	

	def get_instance_launch_datetime(self,instance):
		returnstring="-"
		for i in self.instance_details:
			if instance.id == i[0]:
				returnstring= i[3] + " " + i[4]
		return returnstring
		

	def get_instance_creation_datetime(self,instance):
		returnstring="-"
		for i in self.instance_details:
			if instance.id == i[0]:
				returnstring= i[5] + " " + i[6]
		return returnstring
	
	def get_instance_stop_datetime(self,instance):
		returnstring="-"
		for i in self.instance_details:
			if instance.id == i[0]:
				returnstring= i[7] + " " + i[8]
		return returnstring

	def get_instance_state_reason(self,instance):
		return str(instance.state_reason)

	def get_instance_secgroup(self,instance):
		secgrouplist=""
		counter=1
		for secgroup in instance.groups:
			secgrouplist += str(secgroup.name) + " (" + str(secgroup.id) + ")"
			if (counter < len(instance.groups)):
				secgrouplist += ", "
			counter += 1
		return str(secgrouplist)

	def get_instance_interfaces(self,instance):
		return str(instance.interfaces)

	def get_instance_ebs_opt(self,instance):
		return str(instance.ebs_optimized)

	def get_instance_profile(self,instance):
		return str(instance.instance_profile)

	def get_instance_tag_info(self,instance,tagtocheckfor):
		stringtoreturn=""	
		for tag_type, tag_value in instance.__dict__['tags'].items():
			if tag_type == tagtocheckfor:				
				stringtoreturn=tag_value
		return stringtoreturn	

	def get_instance_name(self,instance):
		if 'Name' in instance.__dict__['tags']:
			returnstring=instance.__dict__['tags']['Name']
		else:
			returnstring="<none>"
		return returnstring

	def get_instance_name_by_id(self,instance_id):
		returnstring=""		
		for i in self.instance_details:
			if i[0] == instance_id:
				returnstring=i[1]
		return returnstring	

	def create_snapshots_by_instance_id(self,instance_id):
		volumes = self.conn.get_all_volumes(filters={'attachment.instance-id' : instance_id}	)	
		snapshots=[]
		for v in volumes:
			snapshots.append(v.create_snapshot())
		return snapshots

	def create_snapshot_by_volume_id(self,volume_id):
		volume = self.conn.get_all_volumes(filters={'volume-id' : volume_id})[0]
		new_snap=volume.create_snapshot()
		return new_snap.id

	## This function returns the following fields -
	## <Volume ID>, <Snap ID>, <Snap Date>, <Snap Time>
	def get_snapshot_info_by_volume_id(self,volume_id):
		snaplist=[]
		for s in [snapinfo for snapinfo in self.snapshot_details if snapinfo[2] == volume_id]:
			snap_id=s[0]			
			snapdate=s[6]
			snaptime=s[7]
			snapDesc=s[13]
				
			snaplist.append([volume_id,snap_id,snapdate,snaptime,snapDesc])
		snaplist=sorted(snaplist, key=operator.itemgetter(0,2,3),reverse=False)
		return snaplist

	def get_latest_snapshot_info_by_instance_id(self,instance_id,displaytype="all"):
		instance_name=self.get_instance_name_by_id(instance_id)			
		instance_snaplist=[]
		for v in self.volume_details:
			volume_iid = v[3]
			num_of_snaps= v[5]
			if volume_iid == instance_id:	
				snaps_by_vol_list=self.get_snapshot_info_by_volume_id(v[0])
				if (len(snaps_by_vol_list) > 0):
					instance_snaplist.append([instance_id,instance_name] + snaps_by_vol_list[len(snaps_by_vol_list)-1] + [num_of_snaps])
				else:
					instance_snaplist.append([instance_id,instance_name,v[0],"<none found>","<N/A>","<N/A>","<N/A>",0])
		return instance_snaplist

	## This function returns the following fields -
	## <Instance ID>, <Instance Name>, <Volume ID>, <Snap ID>, <Snap Date>, <Snap Time>
	def get_full_snapshot_info_by_instance_id(self,instance_id,displaytype="all"):
		instance_name=self.get_instance_name_by_id(instance_id)	
		instance_snaplist=[]
		for v in self.volume_details:
			volume_iid = v[3]
			if volume_iid == instance_id:
				snaps_by_vol_list=self.get_snapshot_info_by_volume_id(v[0])
				if (len(snaps_by_vol_list) == 1):
						instance_snaplist.append([instance_id,instance_name] + snaps_by_vol_list[0])		
				elif (len(snaps_by_vol_list) > 1):
					for snap_info in snaps_by_vol_list:
						instance_snaplist.append([instance_id,instance_name] + snap_info)
				else:	
					instance_snaplist.append([instance_id,instance_name,v[0], "<none found>","<N/A>","<N/A>","<N/A>"])
		return instance_snaplist

	## This function returns the following fields -
	## <Instance ID>, <Instance Name>, <Volume ID>, <Snap ID>, <Snap Date>, <Snap Time>
	def list_instances_and_snapshot_info(self,displaytype="latest-all"):
		outputarray=[]
		for ins_obj in self.instance_objects:
			if (displaytype == "full"):
				temparray=self.get_full_snapshot_info_by_instance_id(ins_obj.id,"all")
				for record_line in temparray:
					outputarray.append(record_line)				
			elif (displaytype == "latest-all"):
				temparray=self.get_latest_snapshot_info_by_instance_id(ins_obj.id,"all")				
				for record_line in temparray:
					outputarray.append(record_line)
			elif (displaytype == "latest-found"):
				temparray=self.get_latest_snapshot_info_by_instance_id(ins_obj.id,"exists")
				for record_line in temparray:
					if record_line[3] != "<none found>":	
						outputarray.append(record_line)
			elif (displaytype == "latest-notfound"):
				temparray=self.get_latest_snapshot_info_by_instance_id(ins_obj.id,"all")
				for record_line in temparray:	
					if record_line[3] == "<none found>":
						outputarray.append(record_line)
		return outputarray

	def get_list_of_all_instance_ids(self):
		returnlist=[]
		for instance in self.instance_objects:
			returnlist.append(instance.id)
		return returnlist

	def get_list_of_all_instance_ids(self):
		returnarray=[]
		for instance_id in [instance[0] for instance in self.instance_details]:
			returnarray.append(instance_id)
		return returnarray

	def return_oldest_snapshots_for_vol(self,vol_id,num_of_snapshots_to_return):
		snapshot_list=[]
		for sid,sno,vid,vo,iid,io,sd,st,ubami,amiid,srcvexists,iobjexists,amiexists,snapDesc in self.snapshot_details:
			if vid == vol_id:
				snapshot_list.append([vid,sid,sd,st])
		snapshot_list=sorted(snapshot_list, key=operator.itemgetter(2,3),reverse=False)
		total_snapshots=len(snapshot_list)
		returnarray=[]
		for i in range (0,num_of_snapshots_to_return):
			returnarray.append(snapshot_list[i])
		return returnarray

        def return_oldest_snapshots_to_delete_for_vol(self,vol_id,num_of_snapshots_to_return):
                snapshot_list=[]
                for sid,sno,vid,vo,iid,io,sd,st,ubami,amiid,srcvexists,iobjexists,amiexists,snapDesc in self.snapshot_details:
                        if vid == vol_id:
				if 'Backup_Type' in sno.__dict__['tags']:
					if sno.__dict__['tags']['Backup_Type'] == 'Scheduled':
                                		snapshot_list.append([vid,sid,sd,st])
                snapshot_list=sorted(snapshot_list, key=operator.itemgetter(2,3),reverse=False)
                total_snapshots=len(snapshot_list)
                returnarray=[]
		if num_of_snapshots_to_return > total_snapshots:
			num_of_snapshots_to_return = total_snapshots
                for i in range (0,num_of_snapshots_to_return):
                        returnarray.append(snapshot_list[i])
                return returnarray


	def get_snapshots_to_remove(self,retention_value,specified_instances=[]):
		snaps_to_remove=[]
		specified_instance_ids=[]
		if len(specified_instances) == 0:
			specified_instance_ids = [iid[0] for iid in self.instance_details]
		else:
			specified_instance_ids = [ins.id for ins in specified_instances]
		for record in self.volume_details:
			volid,volobj,volblkd,insid,insobj,num_of_snaps=record
			for specified_iid in specified_instance_ids:
				if specified_iid == insid:
					if num_of_snaps > retention_value:
						num_of_snaps_to_delete = num_of_snaps - retention_value
						oldest_snapshots=self.return_oldest_snapshots_for_vol(volid,num_of_snaps_to_delete)
						for vid,snapid,snapdate,snaptime in oldest_snapshots:
							snaps_to_remove.append([insid,vid,snapid,snapdate,snaptime])
		return snaps_to_remove	


	def generate_report_from_array(self,outfile,header,input_array,worksheet_title='Untitled'):
		#create excel report file
		split_fname=outfile.split(".")
		report_type = split_fname[len(split_fname)-1].rstrip('\n')

		if report_type == 'xlsx':
			workbook = xlsxwriter.Workbook(outfile)
			worksheet = workbook.add_worksheet(worksheet_title)
		
			col=0
			col_width=[]
			for headercell in header:
				worksheet.write(0,col,headercell)
				col_width.append(len(headercell))
				worksheet.set_column(col,col,(col_width[col])+1)
				col += 1

			row=1
			for row_data in input_array:
				col=0
				for cell in row_data:		
					if (len(str(cell)) > col_width[col]):
						col_width[col] = (len(str(cell)))					
						worksheet.set_column(col,col,(col_width[col])+1)			
					worksheet.write(row,col,str(cell))
					col+=1
				row +=1
			workbook.close()
		#create csv report file	
		else:
			f = open(outfile,'w')
			line_to_output=""
			for headercell in header:
				line_to_output += headercell + "|"
			f.write(line_to_output + '\n')
	
			for row_data in input_array:
				line_to_output=""
				for cell in row_data:
					line_to_output += str(cell) + "|"
				f.write(line_to_output + '\n')
			f.close()
		
