# Encrypt EC2 Volumes
This script aims to encrypt the ec2 volumes attached to instances.
The script asks the user to either encrypt all the volumes or specify a list of volumes to encrypt at run time. 

### Usage:
1. Update Config File: *config.py*
2. Run **main.py** (*$python main.py*)
3. Choose what volumes you wish to encrypt:
   - If you wish to proceed with all the volumes, enter Yes.
   - If you wish to choose your own volumes, enter No.
4. Confirm you wish to enter your own list of volume IDs.
5. Input a **space separated list** of Volume IDs.

### config.py
This file contains the basic configuration needed to execute the script:

| Attribute    | Usage                                                                                |
|:-------------|:-------------------------------------------------------------------------------------|
| REGION       | AWS Region where this script needs to execute in.                                    |
| THREADS      | Number of encryption processes to execute in parallel (1 process per snapshot).      |
| DRY_RUN      | Set Dry Run to True/False                                                            |
| CLEANUP      | When set to True, cleans up all intermediary snapshots and volumes.                  |
| WAITING_TIME | Waiting time in seconds (Some volumes might require large amount of time to process) |

### Other Details
- Python Version = 3.7.2
- Boto3 Version = 1.9.188
- Tabulate Version = 0.8.3
