
import paramiko
import time
import pandas as pd
from datetime import datetime
import os
import configparser


passwords = []

def switch_touch(ip, password):
    try:

         # Create an SSH client instance
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=ip, username='netadmin', password=password, timeout=5)
        ssh_shell = ssh_client.invoke_shell()
        ssh_shell.send("terminal length 0\n")  # Set terminal length to 0 to get the entire output
        #wait until the shell is ready
        while not ssh_shell.recv_ready():
            pass
        #write mem to save the config
        ssh_shell.send("write mem\n")
        #print out config
        ssh_shell.send("show run\n")
        #wait for it to finish
        time.sleep(3)
        #load config into string to pass
        switch_output = ssh_shell.recv(65535).decode('utf-8')
        i = 0
        while not switch_output.endswith('#') or len(switch_output) < 1000:
            time.sleep(1)
            switch_output += ssh_shell.recv(65535).decode('utf-8')
            i += 1
            if i > 35:
                return "Error: Connection timed out or switch took too long to respond", 14

        switch_output = switch_output.strip()
        return switch_output, 10
    except Exception as e:
        #traceback.print_exc()
        print("Error: " + str(e) + "\n")
        error = "Error: " + str(e) + "\n"
        error = error.strip()
        return error, 12
    finally:
         # Close SSH connection properly
            ssh_client.close()


def save_config(switch_name, switch_config):
    #strip switch name to remove any white space or newline characters
    switch_name = switch_name.strip()
    #grab current date and convert to string of xx-xx-xxxx format
    curr_time = datetime.now()
    date_string = curr_time.strftime("%m-%d-%Y").strip()
    #specify directory
    directory = "/mnt/sda/switch-configs/" + date_string
    #create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    #create the file name with format switchname_config-xx-xx-xxxx.txt
    filename = "{}_config-{}.txt".format(switch_name, date_string)
    #join the directory path to the filename
    filepath = os.path.join(directory, filename)
    #create the file and write out the config
    with open(filepath, "w") as f:
        f.write(switch_config)
    print("\nsaved", switch_name, "config")

def get_info():
    df = pd.read_csv("/opt/backup-script/switch_ips.csv")
    return df

def save_errors(switch_info):
    #print(switch_info)
    switch_info = switch_info[switch_info['error'].str.strip() != '']
    #print(switch_info)
    curr_time = datetime.now()
    date_string = curr_time.strftime("%m-%d-%Y").strip()
    #create the file name with format switchname_config-xx-xx-xxxx.txt
    filename = "/mnt/sda/switch-configs/switches_with_issues-{}.csv".format(date_string)
    #join the directory path to the filename
    switch_info.to_csv(filename, index=False)



###
def main():
    #open csv file
    switch_info = get_info()
    #create error column
    switch_info['error'] = ''
    #loop through every row
    for index, row in switch_info.iterrows():
        #grab ip and name
        switch_ip = row['switch_ips']
        switch_name = row['name']
        #loop for every password
        for i in range(len(passwords)):
            switch_config, return_code = switch_touch(switch_ip, passwords[i])
            if return_code == 10:
                break
        if return_code == 10: #if no error code 12 then save the config
            save_config(switch_name, switch_config)
        elif return_code == 14:
            switch_info.at[index, 'error'] = switch_config
            print (switch_name, switch_config)
        elif return_code == 12:  #else the switch is down or has a pswd that isn't in the list
            switch_info.at[index, 'error'] = switch_config
            print (switch_name, switch_config)
        else:
            print("!!!!Unknown Error Occured!!!!")
            return
        

    save_errors(switch_info)
###



if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('/opt/backup-script/pwds.ini')

    for key in config['pwds']:
        passwords.append(config['pwds'][key])
    main()
