import threading
from tabulate import tabulate
import config
from modules import volumes
from modules import helper
from modules import instance


def encrypt(vol_obj):
    multi_processing = None
    for vol_obj in vol_obj:
        multi_processing = threading.Thread(target=volumes.encrypt,
                                            args=(vol_obj,)
                                            )
        multi_processing.start()
    multi_processing.join()


def start(vol_obj_list):
    # Create a list of list of volume objects, in order to process them using threads.
    vol_obj_separated = [vol_obj_list[i:i + config.THREADS] for i in range(0, len(vol_obj_list), config.THREADS)]
    for vol_group in vol_obj_separated:
        # Stop instances which are to be processed:
        print("\n\nFollowing Instances needs to be stopped before starting the process of encrypting:")
        # Step 4: Display the list of volumes to proceed with encryption.
        print(tabulate([[v.InstanceId, v.instanceName, v.id, v.name] for v in vol_group],
                       headers=['Instance ID', 'Instance Name', 'Vol ID', 'Vol Name']))
        # Step 5: Confirm?
        if helper.query_yes_no("\nStart encryption for above " + str(len(vol_group)) + " volumes now? "):
            # Step 6: Execute in parallel.
            instance.stop_all([v.InstanceId for v in vol_group])
            print("All instances Stopped.")
            encrypt(vol_group)
            print("Encryption start.")
        else:
            print("Skipping above " + str(config.THREADS) + " volumes.\n")
        # Step 7: go to step 4.
    print("rest")
