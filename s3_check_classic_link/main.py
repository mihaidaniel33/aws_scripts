from s3_md5.main import AWS_PROFILE
import boto3 
import json


session = boto3.session.Session(profile_name='', region_name='')
ec2 = session.client('ec2')

def get_classic_link_resources():

    results = {}
    instance_name = 'NoName'

    resp = ec2.describe_classic_link_instances(MaxResults=1000)
    for instance in resp['Instances']:
        for tag in instance['Tags']:
            if tag['Key'] == 'Name':
                instance_name = tag['Value']
               
        if instance_name not in results.keys():
            results[instance_name] = [instance['InstanceId']]
        else:
            results[instance_name].append(instance['InstanceId'])
        print(instance_name)
            

    with open('results.json', 'w') as f:
        json.dump(results, f)




if __name__ == '__main__':
    get_classic_link_resources()