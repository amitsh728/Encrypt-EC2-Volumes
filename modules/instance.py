import boto3
import config


def get_instance_tags(instance_id):
    tags = {}

    client = boto3.client('ec2', region_name=config.REGION)
    instance = client.describe_instances(
        InstanceIds=[
            instance_id
        ]
    )['Reservations'][0]['Instances'][0]

    for tag in instance['Tags']:
        tags[tag['Key']] = tag['Value']

    return tags


def stop_all(instance_list):
    client = boto3.client('ec2', region_name=config.REGION)
    waiter = client.get_waiter('instance_stopped')
    response = client.stop_instances(
        InstanceIds=instance_list,
        DryRun=config.DRY_RUN,
        Force=True
    )
    print("Waiting for the instances to stop... ")
    waiter.wait(
        InstanceIds=instance_list,
        DryRun=config.DRY_RUN,
        WaiterConfig={
            'Delay': 6,
            'MaxAttempts': 100
        }
    )
    print("Instance successfully stopped.")
