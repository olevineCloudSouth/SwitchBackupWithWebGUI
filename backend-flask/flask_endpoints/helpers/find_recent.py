import os

def find_recent(mainpath, switch_name, type):
    if type not in ['config', 'arps', 'int', 'mac']:
        raise ValueError("Improper type specified")
    try:
        # List all files in the directory
        files = os.listdir(mainpath)
        # Filter files that match the switch name and have '_config' in their name
        #print(files)

        #print(f"{switch_name}_{type}")
        files = [f for f in files if f.startswith(f"{switch_name}_{type}")]

        if not files:
            print("found none from this mainpath/date")
            return None
        files.sort(key=lambda f: int(f.split('-')[-1].split('.')[0]), reverse=True)
        
        return os.path.join(mainpath, files[0])
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

