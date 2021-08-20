import boto3 
import os 
import json
import sys
import re



session = boto3.session.Session(profile_name='')
s3 = session.client('ec2')

PROFILES = []

AWS_CONFIG_PATH = ""

SESSIONS = [
    # 's3',
    'ec2',
    # 'elb',
    # 'autoscaling'
]

OUTPUT_DIRECTORY = "./output"

IP_TYPE = 'PUBLIC'

FILTER = "0.0.0.0"


def load_aws_config_profiles(aws_config_path):
    profiles = []
    with open(AWS_CONFIG_PATH, "r") as f:
        for item in f.readlines():
            if "[profile" in item:
                splitted = item.split(" ")
                profiles.append(splitted[1].replace("]", "").strip("\n"))
    return profiles


def create_output_directory(dir_name):
    if not os.path.isdir(f"{OUTPUT_DIRECTORY}"):
        print(f"Creating output directory: {OUTPUT_DIRECTORY}")
        os.mkdir(f"{OUTPUT_DIRECTORY}")
    if not os.path.isdir(f"{OUTPUT_DIRECTORY}/{dir_name}"):
        os.mkdir(f"{OUTPUT_DIRECTORY}/{dir_name}")


def output_to_file(file_name, data):
    with open(f"{OUTPUT_DIRECTORY}/{file_name}", "w") as f: 
        obj = json.dumps(data, indent=4, sort_keys=True, default=str)
        f.write(obj)



def filter_ec2_by_ip(filter_ip, ec2_described, search_by='PRIVATE'):

    for instance in ec2_described["Instances"]:
        if search_by == 'PRIVATE':
            if "PrivateIpAddress" in instance.keys():
                print(instance["PrivateIpAddress"])
                if instance["PrivateIpAddress"] == filter_ip:
                    return {
                        "PrivateIpAddress": instance["PrivateIpAddress"],
                        "InstanceId": instance["InstanceId"]
                    }
        elif search_by == 'PUBLIC':
            if "PublicIpAddress" in instance.keys():
                print(instance["PublicIpAddress"])
                if instance["PublicIpAddress"] == filter_ip:
                    return {
                    "PublicIpAddress": instance["PublicIpAddress"],
                    "InstanceId": instance["InstanceId"]
                }
            



def ec2_describe(profile, session, filter, ip_type, output_resources=False):
    if not output_resources and filter == "": return
    filtered_data = []
    instances = session.describe_instances()
    if output_resources:
        output_to_file(f'{profile}/ec2_resources.json', instances)
    if filter != "":
        for item in instances["Reservations"]:
            filtered_ec2 = filter_ec2_by_ip(filter, item, ip_type)
            if filtered_ec2 is not None:
                filtered_data.append(filtered_ec2)

        output_to_file(f"{profile}/ec2_filtered_by_ip.json", filtered_data)


if __name__ == '__main__':
    # PROFILES = load_aws_config_profiles(AWS_CONFIG_PATH)



    for profile in PROFILES:
        create_output_directory(profile)
        for session in SESSIONS:
            print(f"Starting processing on resource: {session}. Profile: {profile}")
            aws_session = None
            if session == 'ec2':
                aws_session = boto3.session.Session(profile_name=profile).client(session, region_name='eu-west-1')  
            else:  
                aws_session = boto3.session.Session(profile_name=profile).client(session)

            globals()[f"{session}_describe"](
                profile, 
                aws_session, 
                FILTER,
                IP_TYPE
            )

    