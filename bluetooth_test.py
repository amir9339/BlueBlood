import bluetooth
import requests
import json
import time
from datetime import datetime
import requests


MAC_API_URL = 'http://macvendors.co/api/%s'
HISTORY_FILE = "history_test_2.txt"
DEVICES_FILE = "devices_file.json"
KNOWN_MAC = {"88:D0:39:2D:41:BD": "JBL E65BTNC"}
KNOWN_MAC_LIST = list(KNOWN_MAC.keys())
UTC_3 = 10800 # Beacause utc + 3
MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
LOCAL_API_URL = "http://127.0.0.1:8000/api/"
DISPLAY_TEXT = """
Hi you, The one with the {}
The first time I saw you was {}
"""



def get_mac_detailes(mac):
    # This function get mac address and return its name if it was seen before.
    # Otherwised it will return false

    with open(DEVICES_FILE) as f:
        data = json.loads(f.read())

    # Check if device already exists in file
    if mac in data:
        return data[mac]["name"]
    else:
        return False

def add_device_to_file(mac, name):
    # This function add a device to the discovered list

    company = get_mac_vendor_company(mac)
    new_device = {mac: {"company": company,
                            "name": name}
    }

    with open(DEVICES_FILE) as f:
        data = json.loads(f.read())

    data.update(new_device)
    with open(DEVICES_FILE, "w") as f:

        # Replace quotes with double quotes
        data = json.dumps(data)
        f.write(str(data))

def get_mac_vendor_company(mac):
    # This function get mac address and return its vendor company

    r = requests.get(MAC_API_URL % mac)

    if r:
        return r.json()["result"]["company"]

def discover_devices(Duration):
    discovered_mac_list = []

    print ('Searching for nearby devices...')
    nearby_devices=bluetooth.discover_devices(duration=Duration,lookup_names=True,
                                          flush_cache=True)
    print ('found %d devices'%len(nearby_devices))

    for addr,name in nearby_devices:
        try:
            print (' %s - %s'%(addr,name))

            if get_mac_detailes(addr):
                discovered_mac_list.append(addr)
            else:
                add_device_to_file(addr, name)

        except:
            name = name.encode('utf-8','replace')
            print (' %s - %s' % (addr, name))
            if get_mac_detailes(addr):
                discovered_mac_list.append(addr)
            else:
                add_device_to_file(addr, name)
    return discovered_mac_list


#add_device_to_file("88:D0:39:2D:41:B1", "test")
#print(get_mac_detailes("88:D0:39:2D:41:B1"))
#discover_devices(5)

def find_last_time(mac):
    # This function get mac address and return the last time it was seen

    with open(HISTORY_FILE) as f:
        data = f.readlines()

        # Read the file in backward
        for line_num in range(len(data)):
            line = data[-1 * (line_num + 1)]

            # Check if the mac exists in line
            if mac in line:
                line = line.split("&")
                time = int(float(line[0]))
                history_list = eval(line[1])
                print(datetime.utcfromtimestamp(time + UTC_3))
                return time

#find_last_time("40:C6:2A:AA:EE:AE")

def get_last_time_word(last_time):
    # The function takes time and returns
    # the word describing the time passed from that moment

    current_time = time.time()
    time_passed = current_time - last_time

    word = None

    # Less than an hour
    if HOUR >= time_passed > 5 * MINUTE:
        word = "less than an hour ago"

    # Return hour:minute as string
    elif HOUR * 12 >= time_passed >= HOUR:
        word = "at" + datetime.utcfromtimestamp(time + UTC_3).strftime('%H:%M')

    # Return month-day hour:minute
    elif WEEK >= time_passed > HOUR * 12:
        word = "at" + datetime.utcfromtimestamp(time + UTC_3).strftime('%m-%d %H:%M')

    elif time_passed > WEEK:
        word = "more than a week ago"

    return word



def send_api_request(text):
    r = requests.post(LOCAL_API_URL, data = {"text": text})

def main():

    while True:
        new_mac_addresses = discover_devices(10)
        all_mac = []

        with open(HISTORY_FILE) as f:
            data = f.readlines()
            for line_num in range(len(data)):
                line = data[-1 * (line_num + 1)]
                mac_list = eval(line.split("&")[1])
                all_mac.append(mac_list)

        for mac in new_mac_addresses:

            #Beacause this is a nested list
            for lst in all_mac[0:2]: # Searching for the last two queries
                if mac not in lst:
                    print("mmm... New device", mac)
                    last_time = find_last_time(mac)
                    if last_time:
                        utc_last_time = datetime.utcfromtimestamp(last_time + UTC_3)
                        time_word = get_last_time_word(last_time)

                    # Check if device is new to the system
                    if not last_time:
                        send_api_request("First time I see ya!")
                        print("First time I see ya!")
                        break
                    else:
                        name = get_mac_detailes(mac)
                        text = DISPLAY_TEXT.format(name, time_word)
                        send_api_request(text)
                        print(text)
                        break
                else:
                    send_api_request("Nothing new")
                    print("Nothing new")


        with open(HISTORY_FILE, "a") as f:
            f.write("{}&{}\n".format(time.time(), new_mac_addresses))


if __name__ == "__main__":
    main()

# To Do:
# Fix main()
