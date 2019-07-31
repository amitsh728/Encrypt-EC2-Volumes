from modules import volumes
from modules import helper
from modules import encrypt
from tabulate import tabulate
import config

if __name__ == "__main__":
    # Step 1: Get volume list.
    vol_list = volumes.get_unencrypted()
    # Step 2: Display list to user.
    print("Following Volumes are not encrypted in " + config.REGION + " region: \n")
    print(tabulate([[v.count, v.id, v.name, v.instanceName, v.create_time] for v in vol_list],
                   headers=['S.No.', 'Vol ID', 'Vol Name', 'Instance Name', 'Create Time (UTC)']))

    if helper.query_yes_no("Proceed with the above selection (Choose No to choose a custom list of volumes)?"):
        encrypt.start(vol_list)
    elif helper.query_yes_no("Want to choose your own volumes (Choose No to exit the script)? "):
        v_list = helper.receive_manual_input()
        if v_list:
            encrypt.start(v_list)
        else:
            print("No Volume chosen. EXITING!")
