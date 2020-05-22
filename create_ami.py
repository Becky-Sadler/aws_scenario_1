import boto3
import yaml
import os
import botocore

config = yaml.safe_load(open("config.yml"))
 
access_key = config['aws_access_key_id']
secret_key = config['aws_secret_access_key']
default_region = config['aws_default_region']

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

def create_security_group(description, name):
	response = ec2_client.create_security_group(
		Description = description,
		GroupName = name
	)
	
	sg_id = response['GroupId']
	return(sg_id)

security_group_id = create_security_group('Security group for EC2 Scenario 1', 'EC2 group')

def create_sg_rule(groupid, fromport, protocol, IP_range, description, toport):
	response = ec2_client.authorize_security_group_ingress(
    GroupId= groupid,
    #GroupName='string',
    IpPermissions=[
        {
            'FromPort': fromport,
            'IpProtocol': protocol,
            'IpRanges': [
                {
                    'CidrIp': IP_range,
                    'Description': description
                },
            ],
            'ToPort': toport,
        },
    ],
)



