import sys
from modules import volumes


def query_yes_no(question, default="no"):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("Invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def process_user_input(user_input):
    valid_list = []
    invalid_list = []
    v_list = user_input.split()
    for v in v_list:
        if v.startswith("vol-"):
            valid_list.append(v)
        else:
            invalid_list.append(v)
    return valid_list, invalid_list


def receive_manual_input():
    u_input = input("Enter the list of volumes separated by spaces:")
    valid_list, invalid_list = process_user_input(u_input)
    if not invalid_list:
        return volumes.get_vol_object(valid_list)
    else:
        if query_yes_no("Few volume IDs are invalid, proceed with the valid IDs? "):
            return volumes.get_vol_object(valid_list)
        else:
            return []
