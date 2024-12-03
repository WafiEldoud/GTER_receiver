import pandas as pd
import os
import time
import numpy as np
from sqlalchemy import create_engine

engine = create_engine('postgresql+psycopg2://postgres:30486@localhost:5432/postgres')
# Positions file info
def monitor_pos_file(file_path, check_interval):
    last_size = 0
    data_frame = pd.DataFrame()
    
    while True:
        try:
            if os.path.exists(file_path):
                current_size = os.path.getsize(file_path)
                if current_size > last_size:
                    with open(file_path, 'r') as f:
                        f.seek(last_size)
                        new_lines = f.readlines()
                    
                    if new_lines:
                        temp_df = pd.DataFrame(
                            [line.split() for line in new_lines],
                        )
                        data_frame = pd.concat(
                            [data_frame, temp_df], ignore_index=True
                        )
                        
                    last_size = current_size
                    print(f"New data added to positions DataFrame. number of rows: {len(data_frame)}")
                else:
                    print("No new data found.")
                    break
            else:
                print(f"File {file_path} does not exist.")
            
            time.sleep(check_interval)
           
        except KeyboardInterrupt:
            print("Monitoring stopped.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

    data_frame.columns= [
            'GPS_week', 'time', 'latitude', 'longitude',
            'hight', 'sol', 'n_sat', 'sdn', 'sde', 'sdu',
            'sdne','sdeu','sdun', 'age', 'ratio'
        ]
    data_frame = data_frame.drop(index=0).reset_index(drop=True)
    data_frame.to_sql('positions', engine, if_exists='append')
    
    return data_frame

# ZTD file info
def monitor_ZTD_file(file_path, check_interval):
    last_size = 0
    data_frame = pd.DataFrame()
    
    while True:
        try:
            if os.path.exists(file_path):
                current_size = os.path.getsize(file_path)
                if current_size > last_size:
                    with open(file_path, 'r',) as f:
                        f.seek(last_size)
                        new_lines = f.readlines()
                    
                    if new_lines:
                    
                        temp_df = pd.DataFrame(
                            [line.strip().split(',') for line in new_lines if line.strip()]
                            ,
                        )
                        data_frame = pd.concat(
                            [data_frame, temp_df], ignore_index=True
                        )
                        
                    last_size = current_size
                    print(f"New data added to ZTD DataFrame. number of rows: {len(data_frame)} ")
                else:
                    print("No new data found.")
                    break
            else:
                print(f"File {file_path} does not exist.")
            
            time.sleep(check_interval)
           
           
        except KeyboardInterrupt:
            print("Monitoring stopped.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

    data_frame.columns = [
            'info','GPS_week','time','sol','antenna',
            'ztd','ztdf','nan_1','nan_2','nan_3','nan_4','nan_5',
            'nan_6','nan_7','nan_8','nan_9'
        ]
    data_frame = data_frame[data_frame['info'] == '$TROP']
    data_frame.to_sql('ztd', engine, if_exists='append')
    
    return data_frame

# ZHD extraction
def zhd_cal(positions, height, pressure):
    zhd_list = []
    for i, row in positions.iterrows():
        longitude = row['longitude']
        height = row['height']
        zhd = (0.0022768 * pressure)/1 - ((0.00266 * np.cos(longitude)) - (2.8 * 10^-7 *height))
        zhd_list.append(zhd)
    zhd_data = {'zhd': zhd_list}
    zhd_df = pd.DataFrame(zhd_data)
    return zhd_df

# ZWD extraction
def zwd_cal(ztd_readings, zhd_reading):
    zwd_list = []
    zwd = ztd_readings['ztd'] - zhd_reading['zhd']
    zwd_list.append(zwd)
    zwd_data = {'zwd': zwd_list}
    zwd_df = pd.DataFrame(zwd_data)
    return zwd_df

# PWV extraction
def pwv_cal(zwd_readings, pressure, tempreture,R_w, k_2, k_3):
    pwv_list = []
    for i, row in zwd_readings.iterrows():
        zwd = row['ztd']
        pwv = ztd * 10^6/(pressure*R_w(k_2 + (k_3/tempreture)))
        pwv_list.append(pwv)
    pwv_data = {'pwv': pwv_list}
    pwv_df = pd.DataFrame(pwv_data)
    return pwv_df
