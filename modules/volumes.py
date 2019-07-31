from modules import instance
import boto3
import config


class Volume:
    def __init__(self, vol_obj, count):
        self.id = vol_obj.id
        self.count = count
        self.name = "N/A"
        self.create_time = vol_obj.create_time
        self.InstanceId = vol_obj.attachments[0]['InstanceId']
        instance_tag = instance.get_instance_tags(self.InstanceId)
        self.instanceName = (instance_tag['Name'] if instance_tag['Name'] is not None else "N/A")
        self.device = vol_obj.attachments[0]['Device']
        self.a_zone = vol_obj.availability_zone
        if vol_obj.tags is not None:
            for tag in vol_obj.tags:
                if tag['Key'] == 'Name':
                    self.name = tag['Value']
                    break


def get_encrypted():
    ec2 = boto3.resource('ec2', region_name=config.REGION)
    filters = [
        {
            'Name': 'encrypted',
            'Values': ['true']
        }
    ]
    volumes = ec2.volumes.filter(region_name=config.REGION)
    return [vol.id for vol in volumes]


def get_unencrypted():
    vol_list = []
    count = 1
    ec2 = boto3.resource('ec2', region_name=config.REGION)
    filters = [
        {
            'Name': 'encrypted',
            'Values': ['false']
        }
    ]
    for vol in ec2.volumes.filter(Filters=filters):
        try:
            instance_id = vol.attachments[0]['InstanceId']
            v = Volume(vol, count)
            vol_list.append(v)
            count += 1
        except IndexError as e:
            pass
    return vol_list


def get_all():
    ec2 = boto3.resource('ec2', region_name=config.REGION)
    volumes = ec2.volumes.all()  # If you want to list out all volumes
    return [vol.id for vol in volumes]


def get_vol_object(vol_id):
    vol_list = []
    count = 1
    ec2 = boto3.resource('ec2', region_name=config.REGION)
    for vol in ec2.volumes.filter(VolumeIds=vol_id):
        v = Volume(vol, count)
        vol_list.append(v)
        count += 1
    return vol_list


def encrypt(vol_object):
    print("(" + str(vol_object.name) + ") Starting to encrypt volume.")
    # Calculate maximum attempts to check the availability of resources.
    max_attempts = config.WAITING_TIME / 10

    # To manage resources.
    client = boto3.client('ec2', region_name=config.REGION)
    ec2 = boto3.resource('ec2', region_name=config.REGION)
    volume = ec2.Volume(vol_object.id)

    # Waiter to monitor resource creation.
    waiter_snapshot = client.get_waiter('snapshot_completed')
    waiter_volume = client.get_waiter('volume_available')

    """
    START Detaching Volume
    """
    print("(" + str(vol_object.name) + ") [Step 0] Detaching the volume from instance.")
    response = client.detach_volume(
        Force=True,
        InstanceId=vol_object.InstanceId,
        VolumeId=vol_object.id,
        DryRun=config.DRY_RUN
    )
    waiter_volume.wait(
        VolumeIds=[
            vol_object.id
        ],
        DryRun=config.DRY_RUN,
        WaiterConfig={
            'Delay': 10,
            'MaxAttempts': max_attempts
        }
    )

    """
    Creating a snapshot from existing Volume.
    """
    print("(" + str(vol_object.name) + ") [Step 1] Creating a new snapshot from existing volume.")
    snapshot_copy = volume.create_snapshot(
        Description='Temporary snapshot to encrypt volume ' + vol_object.id + '.',
        DryRun=config.DRY_RUN,
        TagSpecifications=[
            {
                'ResourceType': 'snapshot',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': vol_object.name
                    },
                    {
                        'Key': 'InstanceID',
                        'Value': vol_object.InstanceId
                    },
                    {
                        'Key': 'InstanceName',
                        'Value': vol_object.instanceName
                    }
                ]
            }
        ]
    )
    snapshot_copy_id = snapshot_copy.id
    print(
        "(" + str(vol_object.count) + ") [Step 1] Waiting for new snapshot create_snapshot to become available: " + str(
            snapshot_copy_id))

    waiter_snapshot.wait(
        SnapshotIds=[
            snapshot_copy_id,
        ],
        DryRun=config.DRY_RUN,
        WaiterConfig={
            'Delay': 10,
            'MaxAttempts': max_attempts
        }
    )

    """
    Copying new snapshot to a new encrypted snapshot.
    """
    print("(" + str(vol_object.name) + ") [Step 2] Copying new snapshot to a new encrypted snapshot.")
    snapshot_copy_encrypted = snapshot_copy.copy(
        Description='Encrypted Copy created to replace ' + vol_object.id + ' (' + vol_object.instanceName + ').',
        Encrypted=True,
        SourceRegion=config.REGION,
        DryRun=config.DRY_RUN
    )
    snapshot_copy_encrypted_id = snapshot_copy_encrypted['SnapshotId']
    print("(" + str(vol_object.name) + ") [Step 2] Waiting for encrypted snapshot to become available (" + str(
        snapshot_copy_encrypted_id) + ")")

    waiter_snapshot.wait(
        SnapshotIds=[
            snapshot_copy_encrypted_id,
        ],
        DryRun=config.DRY_RUN,
        WaiterConfig={
            'Delay': 10,
            'MaxAttempts': max_attempts
        }
    )

    """
    Create new volume from new encrypted snapshot.
    """
    print("(" + str(vol_object.name) + ") [Step 3] Creating new Volume from encrypted snapshot.")
    encrypted_volume_id = client.create_volume(
        AvailabilityZone=vol_object.a_zone,
        SnapshotId=snapshot_copy_encrypted_id,
        VolumeType='gp2',
        DryRun=config.DRY_RUN,
        TagSpecifications=[
            {
                'ResourceType': 'volume',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': vol_object.name
                    },
                    {
                        'Key': 'InstanceID',
                        'Value': vol_object.InstanceId
                    },
                    {
                        'Key': 'InstanceName',
                        'Value': vol_object.instanceName
                    }
                ]
            }
        ]
    )['VolumeId']

    print("(" + str(vol_object.name) + ") [Step 3] Waiting for new volume creation to complete. (" + str(
        encrypted_volume_id) + ")")

    waiter_volume.wait(
        VolumeIds=[
            encrypted_volume_id,
        ],
        DryRun=config.DRY_RUN,
        WaiterConfig={
            'Delay': 10,
            'MaxAttempts': max_attempts
        }
    )

    """
    Attach new encrypted volume to the instance.
    """
    print("(" + str(vol_object.count) + ") Attaching volume to the instance.")
    response = client.attach_volume(
        Device=vol_object.device,
        InstanceId=vol_object.InstanceId,
        VolumeId=encrypted_volume_id,
        DryRun=config.DRY_RUN
    )
    print("(" + str(vol_object.count) + ") Completed volume encryption process.")
    if config.CLEANUP:
        response = client.delete_snapshot(
            SnapshotId=snapshot_copy_id,
            DryRun=config.DRY_RUN
        )
        response = client.delete_snapshot(
            SnapshotId=snapshot_copy_encrypted_id,
            DryRun=config.DRY_RUN
        )
        response = client.delete_volume(
            VolumeId=vol_object.id,
            DryRun=config.DRY_RUN
        )
    else:
        print("Following resources are skipped from being deleted: \n"
              + str(vol_object.id) + "\n"
              + str(snapshot_copy_id) + "\n"
              + str(snapshot_copy_encrypted_id) + "\n"
              + "Exiting thread")
