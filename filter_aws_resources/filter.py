import boto3 
import os 
import json
import sys
import re



session = boto3.session.Session(profile_name='devops')
s3 = session.client('ec2')

PROFILES = [
    'adserver',
    'adswizz-dev',
    'data-processing',
    'data-science-dev'
]

SESSIONS = [
    's3',
    'ec2',
    'elb',
    'autoscaling'
]

OUTPUT_DIRECTORY = "./output"

FILTER = "(?=.*inventory)(?=.*c2)"


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




def s3_describe(profile, session, filter, output_resources=False):
    if not output_resources and filter == "": return
    filtered_data = []
    buckets = session.list_buckets()
    if output_resources:
        output_to_file(f'{profile}/s3_resources.json', buckets)
    if filter != "":
        for item in buckets["Buckets"]:
            filtered_bucket = filter_s3_by_name(filter, item)
            if filtered_bucket is not None:
                filtered_data.append(filtered_bucket)

        output_to_file(f"{profile}/s3_filtered.json", filtered_data)


def ec2_describe(profile, session, filter, output_resources=False):
    if not output_resources and filter == "": return
    filtered_data = []
    instances = session.describe_instances()
    if output_resources:
        output_to_file(f'{profile}/ec2_resources.json', instances)
    if filter != "":
        for item in instances["Reservations"]:
            filtered_ec2 = filter_ec2_by_name(filter, item)
            if filtered_ec2 is not None:
                filtered_data.append(filtered_ec2)

        output_to_file(f"{profile}/ec2_filtered.json", filtered_data)


def autoscaling_describe(profile, session, filter, output_resources=False):
    if not output_resources and filter == "": return
    filtered_data =[]
    scaling_groups = session.describe_auto_scaling_groups()
    if output_resources:
        output_to_file(f'{profile}/asg_resources.json', scaling_groups)
    if filter != "":
        if scaling_groups["AutoScalingGroups"] == []:
            print("No Auto Scaling Groups found.")
            return
        for item in scaling_groups["AutoScalingGroups"]:
            filtered_asg = filter_asg_by_name(filter, item)
            if filtered_asg is not None:
                filtered_data.append(filtered_asg)

        output_to_file(f"{profile}/asg_filtered.json", filtered_data)


def elb_describe(profile, session, filter, output_resources=False):
    if not output_resources and filter == "": return
    filtered_data = []
    load_balancers = session.describe_load_balancers()
    if output_resources:
        output_to_file(f'{profile}/elb_resources.json', load_balancers)
    if filter != "":
        for item in load_balancers["LoadBalancerDescriptions"]:
            filtered_elb = filter_elb_by_name(filter, item)
            if filtered_elb is not None:
                filtered_data.append(filtered_elb)

        print(filtered_data)
        output_to_file(f"{profile}/elb_filtered.json", filtered_data)



def filter_ec2_by_name(tag_name_filter, ec2_described):
    for instance in ec2_described["Instances"]:
        if "Tags" in instance.keys():
            for tag in instance["Tags"]:
                if tag["Key"] == "Name":
                    if re.search(tag_name_filter, tag["Value"], re.IGNORECASE):
                        return {
                            "InstanceName": tag["Value"],
                            "InstanceId": instance["InstanceId"]
                        }


def filter_s3_by_name(bucket_name_filter, bucket_described):
    if re.search(bucket_name_filter, bucket_described["Name"], re.IGNORECASE):
        return bucket_described


def filter_elb_by_name(elb_name_filter, elb_described):
    if re.search(elb_name_filter, elb_described["LoadBalancerName"], re.IGNORECASE):
        return {
            "LoadBalancerName": elb_described["LoadBalancerName"],
            "LoadBalancerDNSName": elb_described["DNSName"],
            "Instances": elb_described["Instances"],
        }


def filter_asg_by_name(asg_name_filter, asg_described):
    if re.search(asg_name_filter, asg_described["AutoScalingGroupName"], re.IGNORECASE):
        return {
            "AutoScalingGroupName": asg_described["AutoScalingGroupName"],
            "Instances": asg_described["Instances"]
        }



if __name__ == '__main__':

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
                FILTER
            )
