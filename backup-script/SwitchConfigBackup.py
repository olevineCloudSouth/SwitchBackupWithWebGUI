from concurrent.futures import thread
from pydoc import ErrorDuringImport
import paramiko
import time
import pandas as pd
from datetime import datetime
import os
import threading
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib


passwords = []

switch_errors = []




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
                return "Error: Connection timed out or switch took too provide whole config", 14

        switch_output = switch_output.strip()
        ssh_client.close()
        return switch_output, 10
    except Exception as e:
        #traceback.print_exc()
        #print("Error: " + str(e) + "\n")
        error = "Error: " + str(e) + "\n"
        error = error.strip()
        return error, 12

def save_config(switch_name, switch_config):
    print(switch_name, "got here")
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

def thread_run(ip, name):
    print("\nRunning thread for switch", name)
    err_log = None
    for i in range(len(passwords)):
        switch_config, return_code = switch_touch(ip, passwords[i])
        if return_code == 10: #if no error code 12 then save the config
            save_config(name, switch_config)
            print("Saved config for", name)
            err_log = None
            break
        elif switch_config == 14 or return_code == 12:
            err_log = [ip, name, switch_config]
            print("Switch", name, "Error:", switch_config)
        else:
            print("!!!!Unknown Error Occured!!!!")
    if err_log:
        switch_errors.append(err_log)
            
def send_email(file_path):
    config = configparser.ConfigParser()
    config.read('/opt/backup-script/smtpCreds.ini')

    smtp_server = config['SMTP']['smtp_server']
    smtp_port = config['SMTP']['smtp_port']
    sender_email = config['SMTP']['sender_email']
    smtp_password = config['SMTP']['password']
    smtp_username = config['SMTP']['smtp_username']

    subject = "Switches with Issues found"
    body = "Please consult the attachment to see all of the switches that are currently having issues being accessed by the backup script from today's date."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = 'noc@cloudsouth.com'
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))
    if os.path.isfile(file_path):
        # Open the file in binary mode
        with open(file_path, "rb") as attachment:
            # MIMEBase instance to hold the attachment
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())

        # Encode the file to base64
        encoders.encode_base64(part)

        # Add header to the attachment
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')

        # Attach the file to the email
        msg.attach(part)
    else:
        print(f"File {file_path} not found.")
        return
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to a secure one
            server.login(smtp_username, smtp_password)  # Login to the SMTP server
            text = msg.as_string()  # Convert the message to a string
            server.sendmail(sender_email, 'olevine@cloudsouth.com', text)  # Send the email
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def save_errors(switch_errors):
    #convert errors to dataframe for panda's
    df = pd.DataFrame(switch_errors, columns=['IP', 'Name', 'Error'])
    curr_time = datetime.now()
    date_string = curr_time.strftime("%m-%d-%Y").strip()
    #create the file name with format switchname_config-xx-xx-xxxx.txt
    filename = "/mnt/sda/switch-configs/switches_with_issues-{}.csv".format(date_string)
    #join the directory path to the filename
    df.to_csv(filename, index=False)
    return filename


def main():
    switch_info = get_info()
    thread_list = []

    for index, row in switch_info.iterrows():
        if row['retired'] == 'yes':
            print('Skipping retired switch')
        else:

       	    # Grab IP and name
       	    switch_ip = row['switch_ips']
       	    switch_name = row['name']
       	    print("Starting thread for switch", switch_name)
        
        	 # Start thread for that IP and name before looping and starting another thread
       	    t = threading.Thread(target=thread_run, args=(switch_ip, switch_name))
       	    thread_list.append(t)
       	    t.start()

    # Wait for all threads to finish
    for t in thread_list:
        t.join()

    # Once all threads are finished, save errors
    send_email(save_errors(switch_errors))


    print("All threads finished.")
    print("Finito")

    
    

    



if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('/opt/backup-script/pwds.ini')

    for key in config['pwds']:
        passwords.append(config['pwds'][key])
    main()
