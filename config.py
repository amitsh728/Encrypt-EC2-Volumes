# AWS Region where to execute this script [Default: us-west-2].
REGION = "us-west-2"

# Number of parallel encryption to carry out [Default: 10].
THREADS = 10

# Set Dry Run to try or false [Default: False].
DRY_RUN = False

# Cleanup attribute which when set to True, cleanups all the intermediary created snapshots and old volumes.
# NOTE: Only set it to True if you are sure you don't need old volumes.
CLEANUP = False

# Waiting time in seconds (Some volumes might require large amount of time to process) [Default: 3 Hours].
WAITING_TIME = 10800
