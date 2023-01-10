#!/usr/bin/env python
# coding: utf-8

# # WiFi:

# In[17]:


import pandas as pd
import numpy as np
from scipy import stats 
import os
from csv import DictWriter
import csv 
import ast
import json

# txt_file = os.path.join(os.path.expanduser('~'), 'Data_to_publish_encrypted', 'Static','Office','O8','Text','wifi.txt')
# txt_files1 = os.path.join(os.path.expanduser('~'), 'Data_to_publish_encrypted', 'Static','Office','O8','CSV','wifi.csv')

txt_file = os.path.join(os.path.expanduser('~'), 'Desktop','channel1','AllchannelTest.txt')
txt_files1 = os.path.join(os.path.expanduser('~'), 'Desktop','channel1','AllchannelTest.csv')


header_list = ['Time', 'ssid', 'bssid', 'sec', 'channel', 'rssi']

with open(txt_files1, 'w') as file:
    dw = csv.DictWriter(file, delimiter=',', fieldnames=header_list)
    dw.writeheader()
    
    
    
## 2) Re-write the text file to facilite its transformation to csv file

with open(txt_file, 'r') as f:
    data = f.read()
    data = data.replace('(', '{')
    data = data.replace(')', '}')
    data = data.replace('=', ':')
    data = data.replace('{ssid:', '{\'ssid\':')
    data = data.replace('bssid:', '\'bssid\':')
    data = data.replace('sec:', '\'sec\':')
    data = data.replace('channel:', '\'channel\':')
    data = data.replace('rssi:', '\'rssi\':')
    data = data.replace(';','V')
    
with open(txt_file, 'w') as file:
      file.write(data)
  
print("Text replaced")



#transform
wifi_dict = {}

with open(txt_file,'r') as f:
    line = f.readline()
    while line:
        line = f.readline().strip()
    
        wifi_dict = {'Time' : line[11:19]}
        data = line[21:].strip()
        print(data)
        dict = ast.literal_eval(str(data))
        wifi_dict.update(dict)
        print("After conversion: ", wifi_dict)
            
        # Add dictionary to a file
        with open(txt_files1, 'a') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=header_list)
            dictwriter_object.writerow(wifi_dict)
        f_object.close()
            
        wifi_dict = {}  
    


# # Bluetooth:

# In[65]:


import pandas as pd
import numpy as np
from scipy import stats 
import os
from csv import DictWriter
import csv 
import ast
import json

header_list = ['Time','adv_flag','def_tx_pwr', 'mac','rssi','name','scan_tx_pwr','conn_tx_pwr','tx_range','adv_tx_pwr']


txt_file = os.path.join(os.path.expanduser('~'), 'Data_to_publish', 'Static','Office','O8','Text','ble.txt')
txt_files1 = os.path.join(os.path.expanduser('~'), 'Data_to_publish', 'Static','Office','O8','CSV','ble.csv')

with open(txt_files1, 'w') as file:
    dw = csv.DictWriter(file, delimiter=',', fieldnames=header_list)
    dw.writeheader()

    
#Transform
bleu_dict = {}
dict = {}
with open(txt_file,'r') as f:
    
    line = f.readline()
    while line:
        line = f.readline().strip()
        bleu_dict = {'Time' : line[11:19]}
        data = line[21:].strip()
        print(data)
        dict = ast.literal_eval(str(data))
        bleu_dict.update(dict)
        print("After conversion: ", bleu_dict)
        
        # Add dictionary to a file
        with open(txt_files1, 'a') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=header_list)
            dictwriter_object.writerow(bleu_dict)
        f_object.close()
             
        bleu_dict = {}  


# # LoRa:

# In[76]:


import pandas as pd
import numpy as np
from scipy import stats 
import os
from csv import DictWriter
import csv 
import ast
import json

header_list = ['Time','spreading_factor','data','frequency', 'bandwidth','rx_timestamp','rssi','snr','sfrx','sftx','tx_trials','tx_power','tx_time_on_air','tx_counter','tx_frequency']

txt_file = os.path.join(os.path.expanduser('~'), 'Data_to_publish_encrypted', 'Static','Office','O8','Text','lora.txt')
txt_files1 = os.path.join(os.path.expanduser('~'), 'Data_to_publish_encrypted', 'Static','Office','O8','CSV','lora.csv')


with open(txt_files1, 'w') as file:
    dw = csv.DictWriter(file, delimiter=',', fieldnames=header_list)
    dw.writeheader()
    
## 2) Re-write the text file to facilite its transformation to csv file
with open(txt_file, 'r') as f:
    data = f.read()
    data = data.replace('(', '{')
    data = data.replace(')', '}')
    data = data.replace('=', ':')
    data = data.replace('{rx_timestamp:', '{\'rx_timestamp\':')
    data = data.replace('rssi:', '\'rssi\':')
    data = data.replace('snr:', '\'snr\':')
    data = data.replace('sfrx:', '\'sfrx\':')
    data = data.replace('sftx:', '\'sftx\':')
    data = data.replace('tx_trials:', '\'tx_trials\':')
    data = data.replace('tx_power:', '\'tx_power\':')
    data = data.replace('tx_time_on_air:', '\'tx_time_on_air\':')
    data = data.replace('tx_counter:', '\'tx_counter\':')
    data = data.replace('tx_frequency:', '\'tx_frequency\':')
    
    
with open(txt_file, 'w') as file:
    file.write(data)
  
print("Text replaced")


#Transform
lora_dict = {}

with open(txt_file,'r') as f:
    line = f.readline()
    print(line + "---------------")
    while line:
        line = f.readline().strip()

        if line[0:1] == '2':
            lora_dict = {'Time' : line[11:19]}
            data = line[21:].strip()
            print(data)
            dict = ast.literal_eval(str(data))
            lora_dict.update(dict)
            print("After conversion ONE: ", lora_dict)
        if line[0:1] == '{':
            data2 = line[0:].strip()
            print(data2)
            dict = ast.literal_eval(str(data2))
            lora_dict.update(dict)
            print("After conversion TWO: ", lora_dict)
            
            # Add dictionary to a file
            with open(txt_files1, 'a') as f_object:
                dictwriter_object = DictWriter(f_object, fieldnames=header_list)
                dictwriter_object.writerow(lora_dict)
            f_object.close()
            lora_dict = {}
            
          


# # Acc:

# In[74]:


import pandas as pd
import numpy as np
from scipy import stats 
import os
from csv import DictWriter
import csv 
import ast

header_list = ['Time','Acceleration','Roll','battery_voltage', 'battery_percentage','Pitch']

txt_file = os.path.join(os.path.expanduser('~'), 'Data_to_publish_encrypted', 'Static','Office','O7','Text','acc.txt')
txt_files1 = os.path.join(os.path.expanduser('~'), 'Data_to_publish_encrypted', 'Static','Office','O7','CSV','acc.csv')

with open(txt_files1, 'w') as file:
    dw = csv.DictWriter(file, delimiter=',', fieldnames=header_list)
    dw.writeheader()
    
    
#Transform the text file to csv    
acc_dict = {}
dict = {}
with open(txt_file,'r') as f:
    line = f.readline()
    while line:
        line = f.readline().strip()
        acc_dict = {'Time' : line[11:19]}
        data = line[21:].strip()
        print(data)
        dict = ast.literal_eval(str(data))
        acc_dict.update(dict)
        print("After conversion: ", acc_dict)
            
        # Add dictionary to a file
        with open(txt_files1, 'a') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=header_list)
            dictwriter_object.writerow(acc_dict)
        f_object.close()
            
        acc_dict = {} 


# In[ ]:




