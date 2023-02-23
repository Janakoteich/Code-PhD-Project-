#!/usr/bin/env python
# coding: utf-8

# In[195]:


#Add values to a dictionary
def add_values_in_dict(sample_dict, key, list_of_values):
    if key not in sample_dict:
        sample_dict[key] = list()   
    sample_dict[key].extend(list_of_values)
    return sample_dict

#Normalize data (I did not use it)
def NormalizeData(data, MIN, MAX):
    if data == 0:
        return 0
    else:
        return (data - MIN) / (MAX - MIN)
       


# In[196]:


#function to check both wifi and ble are synchronized
def check_timeslots(df_w, df_b):
    w_min = df_w['Time'].min()
    b_min = df_b['Time'].min()
    
    w_max = df_w['Time'].max()
    b_max = df_b['Time'].max()
    
    if w_min > b_min:
        df_b = df_b[(df_b['Time'] >= w_min)]
    else:
        df_w = df_w[(df_w['Time'] >= b_min)]
        
    if w_max > b_max:
        df_w = df_w[(df_w['Time'] <= b_max)]
    else:
        df_b = df_b[(df_b['Time'] <= w_max)]  
        
        
    return df_w, df_b


# In[197]:


def combine_wifi_ble(dataset_wifi,dataset_ble):
    
    df_w = pd.read_csv(dataset_wifi)
    df_b = pd.read_csv(dataset_ble)

    df_w.rename(columns = {'rssi':'rssi_w'}, inplace = True)
    df_w.rename(columns = {'bssid':'mac_w'}, inplace = True)
    df_w.rename(columns = {'ssid':'ssid_w'}, inplace = True)
    
    df_b.rename(columns = {'rssi':'rssi_b'}, inplace = True)
    df_b.rename(columns = {'mac':'mac_b'}, inplace = True)
    
    #we need only Time, ssid, bssid and rssi (for ble no need for name because we miss some)
    df_w = df_w[['Time','ssid_w','mac_w','rssi_w']]
    df_b = df_b[['Time','mac_b','rssi_b']]

    #remove the outliers (my phone mac address)
    df_w.drop(df_w[df_w['ssid_w'] == 'iPhone'].index, inplace = True)
    df_w.drop(df_w[df_w['ssid_w'] == 'Jana :p'].index, inplace = True)                 
    df_w.dropna(inplace=True)
    df_w.reset_index(drop=True, inplace=True)

    #change ssid from categorical data to numerical data
    df_w['ssid_w'] = number.fit_transform(df_w['ssid_w'].astype('str'))

    # convert timestamps to dates 
    df_w.index = pd.to_datetime(df_w.index)
    df_b.index = pd.to_datetime(df_b.index)
    
    #check the synchronization of the two files
    df_w, df_b = check_timeslots(df_w, df_b)
    
    #--------------------------------Now Combine the two dataframes-------------------------------------------------
    # Setting the timestamp as the index
    df_w.set_index('Time', inplace=True)
    df_b.set_index('Time', inplace=True)

    # Just perform a join and that's it
    result = df_w.join(df_b, how='outer')
    result.reset_index(inplace=True)
    result = result.rename(columns = {'index':'Time'})
    result['Time'] = pd.to_datetime(result['Time'],format= '%H:%M:%S' )
    
    return result


# In[198]:


def get_list_mac_wifi(df_w):
    uniq_mac_w = df_w['mac_w'].unique()
    #uniq_mac_w = uniq_mac_w[~np.isnan(uniq_mac_w)]
    uniq_mac_w = uniq_mac_w[~pd.isnull(uniq_mac_w)]
    Nbssid_w = len(uniq_mac_w)
    
    return uniq_mac_w

def get_list_mac_ble(df_b):
    uniq_mac_b = df_b['mac_b'].unique()
    #uniq_mac_b = uniq_mac_b[~np.isnan(uniq_mac_b)]
    uniq_mac_b = uniq_mac_b[~pd.isnull(uniq_mac_b)]
    Nbssid_b = len(uniq_mac_b)
    
    return uniq_mac_b


# In[199]:


def get_nb_AP_with_same_ssid(df_result):
    counter = 0
    uniq_ssid = df_result['ssid_w'].unique()
    #uniq_mac_b = uniq_mac_b[~np.isnan(uniq_mac_b)]
    uniq_ssid = uniq_ssid[~pd.isnull(uniq_ssid)]
    
    for i in range(len(uniq_ssid)):
        x = df_result.loc[df_result['ssid_w'] == uniq_ssid[i]].count()
        if x>1:
            counter = counter + 1
    print df.groupby(['Team','Year']).groups
    
    
    return counter


# In[200]:


def cut_combined_df(result):
    flag = 0 # to check the first row in the df.
    df_x = pd.DataFrame()
    list_w = []
    list_b = []
    
    for cl in result['Time']:
        if flag == 0:
            start = cl
            flag = 1 
        else:
            nextt = cl
            delta_t = nextt - start
            timedelta_seconds = delta_t.total_seconds()
            
            if timedelta_seconds > 60: #2mins
                df_x = result[(result['Time']< delta_t + start) & (result['Time']> start)]
                start = nextt  

                bssid_list_w = get_list_mac_wifi(df_x)
                bssid_list_b = get_list_mac_ble(df_x)
                
                dict_w, dict_b = statistics(df_x, bssid_list_w, bssid_list_b)
                
                list_wx = feature_extraction_wifi(df_x, dict_w, bssid_list_w)
                list_bx = feature_extraction_ble(df_x, dict_b, bssid_list_b)
                list_w.append(list_wx)
                list_b.append(list_bx)
                
                #append list_x to a list                 
    return list_w, list_b


# In[201]:


def statistics(result, uniq_mac_w, uniq_mac_b):
    #get the unique bssid / Type:  <class 'numpy.ndarray'>
    #uniq_mac_w = df_w['bssid'].unique()
    #Nbssid_w = len(uniq_mac_w)

    #Now let's get the number of stable and unstable links for both wifi and ble.
    dict_w = {}
    for i in range(len(uniq_mac_w)): 
        x = result.loc[result['mac_w'] == uniq_mac_w[i]].min()
        y = result.loc[result['mac_w'] == uniq_mac_w[i]].max()
        delta_t = y[0] - x[0]
        timedelta_seconds = delta_t.total_seconds()
        if timedelta_seconds == 0:
            timedelta_seconds = 1
            
        rssi_mean = result[result["mac_w"] == uniq_mac_w[i]].mean()
        rssi_std = result[result["mac_w"] == uniq_mac_w[i]].std()
        rssi_mean = round(rssi_mean, 2)
        rssi_std = round(rssi_std, 2)

        ssid = result[result['mac_w'] == uniq_mac_w[i]]['ssid_w'] #so this is what? as output?
        #int_info = inter(df_w,uniq_mac_w[i])
        #int_number = int_info[0] 
        #int_avr_time = int_info[1]
        int_number = 0
        int_avr_time = 0

        dict_w = add_values_in_dict(dict_w, uniq_mac_w[i], [ssid.iloc[0],timedelta_seconds, rssi_mean[1], rssi_std[1], int_number, int_avr_time])    
    
    
    
    #--------------------ble-----------------------------------------------
    #uniq_mac_b = df_b['mac'].unique()
    #Nbssid_b = len(uniq_mac_b)
      
    dict_b = {}
    for i in range(len(uniq_mac_b)): 
        x = result.loc[result['mac_b'] == uniq_mac_b[i]].min()
        y = result.loc[result['mac_b'] == uniq_mac_b[i]].max()
        delta_t = y[0] - x[0]
        timedelta_seconds = delta_t.total_seconds()
        if timedelta_seconds == 0:
            timedelta_seconds = 1
            
        rssi_mean = result[result["mac_b"] == uniq_mac_b[i]].mean()
        rssi_std = result[result["mac_b"] == uniq_mac_b[i]].std()
        rssi_mean = round(rssi_mean, 2)
        rssi_std = round(rssi_std, 2)

        
        if math.isnan(rssi_mean[0]):
            dict_b = add_values_in_dict(dict_b, uniq_mac_b[i], [timedelta_seconds, rssi_mean[3], rssi_std[3]])  
        else:
            dict_b = add_values_in_dict(dict_b, uniq_mac_b[i], [timedelta_seconds, rssi_mean[2], rssi_std[2]])  
        
    return dict_w, dict_b


# In[202]:


#feature extraction from the summerized dataframe!
def feature_extraction_wifi(df_w, dict_w, uniq_mac_w):
    
    #declare list of features to be returned:
    wifi_list = []
    
    #declare variables
    short_duration_w = 0 #number of links with short duration
    medium_duration_w = 0 #number of links with medium duration
    long_duration_w = 0 #number of links with long duration
    
    sd_list_w = [] #list short duration mac @
    md_list_w = [] #list medium duration mac @
    ld_list_w = [] #list long duration mac @

    sd_rssi_list_w = [] #list rssi of short duration
    md_rssi_list_w = [] #list rssi of medium duration
    ld_rssi_list_w = [] #list rssi of long duration

    #Get the number of seconds for scanning for both wifi and bluetooth
    #delta_t = df_w['Time'][len(df_w)-1] - df_w['Time'][0]
    #w_time_sec = delta_t.total_seconds()
    w_time_sec = 60
    
    for i in range(len(uniq_mac_w)):
        n = dict_w[uniq_mac_w[i]][1] #time is the second index, ssid is the first
        contact_duration_wifi = n/w_time_sec * 100 
        
        if contact_duration_wifi < 30: #short duration
            short_duration_w = short_duration_w + 1
            sd_list_w.append(dict_w[uniq_mac_w[i]][1])
            sd_rssi_list_w.append(dict_w[uniq_mac_w[i]][2])

        elif contact_duration_wifi >= 70: #long duration
            long_duration_w = long_duration_w + 1
            ld_list_w.append(dict_w[uniq_mac_w[i]][1])
            ld_rssi_list_w.append(dict_w[uniq_mac_w[i]][2])
            
        else: # medium duration
            medium_duration_w = medium_duration_w + 1
            md_list_w.append(dict_w[uniq_mac_w[i]][1])
            md_rssi_list_w.append(dict_w[uniq_mac_w[i]][2])
            
                        
    #average contact duration and mean rssi for wifi
    if short_duration_w != 0:
        sd_avr_cd_wifi = sum(sd_list_w)/len(sd_list_w) #avr contact duration
        sd_mean_rssi_wifi = mean(sd_rssi_list_w) #mean rssi 
        sd_std_rssi_wifi = np.std(sd_rssi_list_w) #std rssi 
    else:
        sd_avr_cd_wifi = 0
        sd_mean_rssi_wifi = 0
        sd_std_rssi_wifi = 0

    if medium_duration_w !=0:
        md_avr_cd_wifi = sum(md_list_w)/len(md_list_w)
        md_mean_rssi_wifi = mean(md_rssi_list_w)
        md_std_rssi_wifi = np.std(md_rssi_list_w) #std rssi
    else:
        md_avr_cd_wifi = 0
        md_mean_rssi_wifi = 0
        md_std_rssi_wifi = 0
        
    if long_duration_w !=0:
        ld_avr_cd_wifi = sum(ld_list_w)/len(ld_list_w)
        ld_mean_rssi_wifi = mean(ld_rssi_list_w) 
        ld_std_rssi_wifi = np.std(ld_rssi_list_w) #std rssi
    else:
        ld_avr_cd_wifi = 0
        ld_mean_rssi_wifi = 0
        ld_std_rssi_wifi = 0
        
        
        
    #Now I should return a list
    wifi_list.append(short_duration_w)
    wifi_list.append(medium_duration_w)
    wifi_list.append(long_duration_w)
    wifi_list.append(format(sd_avr_cd_wifi,".3f"))
    wifi_list.append(format(md_avr_cd_wifi,".3f"))
    wifi_list.append(format(ld_avr_cd_wifi,".3f"))
    wifi_list.append(format(sd_mean_rssi_wifi,".3f"))
    wifi_list.append(format(md_mean_rssi_wifi,".3f"))
    wifi_list.append(format(ld_mean_rssi_wifi,".3f"))
    wifi_list.append(format(sd_std_rssi_wifi,".3f"))
    wifi_list.append(format(md_std_rssi_wifi,".3f"))
    wifi_list.append(format(ld_std_rssi_wifi,".3f"))
    
    return wifi_list


#-----------------------------------------BLE-----------------------------------------------#

#feature extraction from the summerized dataframe!
def feature_extraction_ble(df_b, dict_b, uniq_mac_b):
    
    #declare list of features to be returned:
    ble_list = []
    
    #declare variables
    short_duration_b = 0 #number of links with short duration
    medium_duration_b = 0 #number of links with medium duration
    long_duration_b = 0 #number of links with long duration

    sd_list_b = [] #list short duration mac @
    md_list_b = [] #list medium duration mac @
    ld_list_b = [] #list long duration mac @

    sd_rssi_list_b = [] #list rssi of short duration
    md_rssi_list_b = [] #list rssi of medium duration
    ld_rssi_list_b = [] #list rssi of long duration

    #delta_b = df_b['Time'][len(df_b)-1] - df_b['Time'][0]
    #b_time_sec = delta_b.total_seconds()
    b_time_sec = 60
    
    for i in range(len(uniq_mac_b)):
        n = dict_b[uniq_mac_b[i]][0]
        contact_duration_ble = n/b_time_sec * 100
        
        if contact_duration_ble < 30: #short duration
            short_duration_b = short_duration_b + 1
            sd_list_b.append(dict_b[uniq_mac_b[i]][0])
            sd_rssi_list_b.append(dict_b[uniq_mac_b[i]][1])

        elif contact_duration_ble >= 70: #long duration
            long_duration_b = long_duration_b + 1
            ld_list_b.append(dict_b[uniq_mac_b[i]][0])
            ld_rssi_list_b.append(dict_b[uniq_mac_b[i]][1])
            
        else: # medium duration
            medium_duration_b = medium_duration_b + 1
            md_list_b.append(dict_b[uniq_mac_b[i]][0])
            md_rssi_list_b.append(dict_b[uniq_mac_b[i]][1])


    #average contact duration and mean rssi for ble    
    if short_duration_b != 0:
        sd_avr_cd_ble = sum(sd_list_b)/len(sd_list_b)
        sd_mean_rssi_ble = mean(sd_rssi_list_b)
        sd_std_rssi_ble = np.std(sd_rssi_list_b) #std rssi
    else:
        sd_avr_cd_ble = 0
        sd_mean_rssi_ble = 0
        sd_std_rssi_ble = 0

    if medium_duration_b !=0:
        md_avr_cd_ble = sum(md_list_b)/len(md_list_b)
        md_mean_rssi_ble = mean(md_rssi_list_b)
        md_std_rssi_ble = np.std(md_rssi_list_b) #std rssi
    else:
        md_avr_cd_ble = 0
        md_mean_rssi_ble = 0
        md_std_rssi_ble = 0
        
    if long_duration_b !=0:
        ld_avr_cd_ble = sum(ld_list_b)/len(ld_list_b)
        ld_mean_rssi_ble = mean(ld_rssi_list_b)
        ld_std_rssi_ble = np.std(ld_rssi_list_b) #std rssi
    else:
        ld_avr_cd_ble = 0
        ld_mean_rssi_ble = 0
        ld_std_rssi_ble = 0
        
        
    
    #Now I shoulf return a list
    ble_list.append(short_duration_b)
    ble_list.append(medium_duration_b)
    ble_list.append(long_duration_b)
    ble_list.append(format(sd_avr_cd_ble,".3f"))
    ble_list.append(format(md_avr_cd_ble,".3f"))
    ble_list.append(format(ld_avr_cd_ble,".3f"))
    ble_list.append(format(sd_mean_rssi_ble,".3f"))
    ble_list.append(format(md_mean_rssi_ble,".3f"))
    ble_list.append(format(ld_mean_rssi_ble,".3f"))
    ble_list.append(format(sd_std_rssi_ble,".3f"))
    ble_list.append(format(md_std_rssi_ble,".3f"))
    ble_list.append(format(ld_std_rssi_ble,".3f"))
                               
    return ble_list


# In[203]:


def get_static_label(scen_index):
    if scen_index == 'H':
        return 'Home'
    if scen_index == 'O':
        return 'Office'
    if scen_index == 'B':
        return 'Bus Station'
    if scen_index == 'U':
        return 'University'
    if scen_index == 'R':
        return 'Restaurant'
    if scen_index == 'C':
        return 'Conference'  
    
def get_mobile_label(scen_index):
    if scen_index == 'B':
        return 'Bus'
    if scen_index == 'C':
        return 'Car'
    if scen_index == 'M':
        return 'Metro'
    if scen_index == 'P':
        return 'Pedestrian'
    if scen_index == 'T':
        return 'Train' 


# # Main :)

# In[204]:


# import required module
import os 
import matplotlib.pyplot as plt
import pandas as pd
import os
import csv
from csv import DictWriter
import seaborn as sns
from statistics import mean
import numpy as np
import hashlib
import warnings
from dateutil.parser import parse
from sklearn.preprocessing import LabelEncoder
import math

get_ipython().run_line_magic('matplotlib', 'inline')
warnings.filterwarnings('ignore')

number  = LabelEncoder()

rootdir = os.path.join(os.path.expanduser('~'), 'Training_dataset')
v = 0
l = []
counterr = 0

for subdir, dirs, files in os.walk(rootdir):
    loc = 0
    for file in files:
        f = str(os.path.join(subdir, file))

        typ_mobility = f[28] # get the first character of the name of the directories, Mobile or Static
        typ_link = f[-5] # to get the type of the link if wifi or bluetooth
        if typ_mobility == 'S' and (typ_link == 'i' or typ_link == 'e'): # for Static scenarios we get both files  
            #BLE
            if loc == 0: 
                ble_path = f #get path
                              
            #WiFi
            if loc == 1:
                wifi_path = f
                
                result  = combine_wifi_ble(wifi_path,ble_path)
                list_wifi, list_ble = cut_combined_df(result)

                label_index = ble_path[35]
                label = get_static_label(label_index)
                
 #--------------------------------------------------------------------------------------               
                for i in range(len(list_wifi)):
                    lw = list_wifi[i]
                    lb = list_ble[i]
                    for j in range(len(lb)):
                        lw.append(lb[j])
                    lw.append(label)   
                    lw.append(0) #means static
                    counterr = counterr + 1
                    l.append(lw)
#-------------------------------------------------------------------------------------- 
                print(wifi_path)
                print(ble_path)
                loc = -1
             
            #REload counter for the next scenario
            loc = loc + 1   
            
    
        if typ_mobility == 'M' and (typ_link == 'i' or typ_link == 'e'): # for Static scenarios we get both files 
            #BLE
            if loc == 0: 
                ble_path = f #get path

            #WiFi
            if loc == 1:
                wifi_path = f
                
                result  = combine_wifi_ble(wifi_path,ble_path)
                list_wifi, list_ble = cut_combined_df(result)

                label_index = ble_path[35]
                label = get_mobile_label(label_index)
                
                #Combine two lists
 #--------------------------------------------------------------------------------------               
                for i in range(len(list_wifi)):
                    lw = list_wifi[i]
                    lb = list_ble[i]
                    for j in range(len(lb)):
                        lw.append(lb[j])
                    lw.append(label)   
                    lw.append(1) # means 1
                    counterr = counterr + 1
                    l.append(lw)
#-------------------------------------------------------------------------------------- 
                print(wifi_path)
                print(ble_path)
                loc = -1
             
            #REload counter for the next scenario
            loc = loc + 1        
        
        
#print(l)
print('Done :)')


# # Five minutes

# In[170]:


print(len(l)) #5min


# In[184]:


headers  = ['short_duration_w', 'medium_duration_w', 'long_duration_w', 'sd_avr_cd_wifi', 'md_avr_cd_wifi', 'ld_avr_cd_wifi','sd_mean_rssi_wifi','md_mean_rssi_wifi','ld_mean_rssi_wifi','sd_std_rssi_wifi','md_std_rssi_wifi','ld_std_rssi_wifi', 'short_duration_b','medium_duration_b','long_duration_b', 'sd_avr_cd_ble', 'md_avr_cd_ble', 'ld_avr_cd_ble','sd_mean_rssi_ble', 'md_mean_rssi_ble', 'ld_mean_rssi_ble', 'sd_std_rssi_ble','md_std_rssi_ble', 'ld_std_rssi_ble', 'scenario','Mobile']
input_file = pd.DataFrame.from_records(l)
input_file.columns = headers  


# In[172]:


path = os.path.join(os.path.expanduser('~'), 'input_files','five_min.csv')

input_file.to_csv(path, index=False)


# # Three Minutes

# In[183]:


print(len(l)) #3min


# In[185]:


path = os.path.join(os.path.expanduser('~'), 'input_files','three_min.csv')
input_file.to_csv(path, index=False)


# # Two Minutes

# In[189]:


print(len(l)) #2min
path = os.path.join(os.path.expanduser('~'), 'input_files','two_min.csv')
input_file.to_csv(path, index=False)


# # Onehalf Minute

# In[193]:


print(len(l)) #1.5min
path = os.path.join(os.path.expanduser('~'), 'input_files','onehalf_min.csv')
input_file.to_csv(path, index=False)


# # One Minute

# In[206]:


print(len(l)) #1min
path = os.path.join(os.path.expanduser('~'), 'input_files','one_min.csv')
input_file.to_csv(path, index=False)

