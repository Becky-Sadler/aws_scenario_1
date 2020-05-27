import boto3
import yaml
import os
import botocore

amazon_config = yaml.safe_load(open("config.yml"))

amazon_details = amazon_config['amazon']
 
access_key = amazon_details['aws_access_key_id']
secret_key = amazon_details['aws_secret_access_key']
default_region = amazon_details['aws_default_region']

# Creating session (configures credentials and default region)
session = boto3.Session(
	aws_access_key_id = access_key,
	aws_secret_access_key = secret_key,
	region_name = default_region
)

# Creating ec2 resource and client for session
ec2_resource = session.resource('ec2', region_name=default_region)
ec2_client = session.client('ec2', region_name=default_region)

# Function to create key pair to be used to launch instance - input = key pair name (minus the .pem), output = keypair.pem with correct permissions. 
def create_keypair(name_of_keypair):
	key_file = open('%s.pem'%name_of_keypair,'w')
	try:
		key = ec2_resource.create_key_pair(KeyName=name_of_keypair)
		key_pair_contents = str(key.key_material)
		key_file.write(key_pair_contents)
		os.system('chmod 400 %s.pem'%name_of_keypair)
	except botocore.exceptions.ClientError as e: 
		print(e)
	else:
		print('Key pair %s.pem sucessfully created'%name_of_keypair)
		return(name_of_keypair)

def create_security_group(description, name):
	try:
		response = ec2_client.create_security_group(
			Description = description,
			GroupName = name
		)
	except botocore.exceptions.ClientError as e: 
		print(e)
	else:
		print('Security group sucessfully created')	
		sg_id = response['GroupId']
		return(sg_id)

def create_sg_rule(groupid, ipPermissions):
	try:	
		response = ec2_client.authorize_security_group_ingress(
	    GroupId= groupid,
	    #GroupName='string',
	    IpPermissions= ipPermissions
	)
	except botocore.exceptions.ClientError as e: 
		print(e)
	else:
		print('Security group rule added: %s'%ipPermissions)	

def create_instances(**kwargs):
	try:
		response = ec2_client.run_instances(**kwargs)
	except botocore.exceptions.ClientError as e: 
		print(e)
	else:
		instance_ID = response['Instances'][0]['InstanceId']
		print('Instance created (%s)'%instance_ID)
		return instance_ID	

def get_user_data(file_name):
    f = open(file_name, 'r')
    user_data = f.read()
    return user_data

# Waiter definition **kwargs must be in the form of a dictionary. 
def add_waiter(waiter_type, **kwargs):
	try:
		waiter = ec2_client.get_waiter(waiter_type)
		waiter.wait(**kwargs)
	except botocore.exceptions.ClientError as e: 
		print(e)
	else:
		print(waiter_type)

# Create AMI function **kwargs must be in the form of a dictionary. 
def create_ami(**kwargs):
	try:
		response = ec2_client.create_image(**kwargs)
	except botocore.exceptions.ClientError as e: 
		print(e)
	else:
		ami_ID = response['ImageId'] 
		print('AMI created: %s'%ami_ID)
		return ami_ID

# clean up function that terminates the instance and puts the required ec2 values (key pair name, security group ID and AMI id) into a ec2 config file
def clean_up(instanceID, keypairName, sgID, amiID):
	try:
		ec2_resource.instances.filter(InstanceIds=[instanceID]).terminate()
	except botocore.exceptions.ClientError as e:
		print(e)
	else: 
		print('Instance %s terminated'%instanceID)
		#config here 
		key_pair = '%s.pem'%keypairName
		data = {'ec2_information': {'keypair_name': str(key_pair), 'security_group_ID': str(sgID), 'ami_ID' : str(amiID)}}
		config_file = open('ec2_config.yml', 'w')
		yaml.dump(data, config_file)
		print('ec2_config file created')



