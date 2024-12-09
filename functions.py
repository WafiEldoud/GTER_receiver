import pandas as pd
import os
import time
import numpy as np
from sqlalchemy import create_engine

engine = create_engine('postgresql+psycopg2://postgres:30486@localhost:5432/postgres')


def monitor_ZTD_file(file_path, check_interval, engine, max_checks=None):

    last_size = 0
    data_frame = pd.DataFrame()
    check_count = 0

    while True:
        try:
            if max_checks and check_count >= max_checks:
                print('Maximum checks reached. Stopping monitoring.')
                break

            if os.path.exists(file_path):
                current_size = os.path.getsize(file_path)
                
                if current_size > last_size:
                    with open(file_path, 'r') as f:
                        f.seek(last_size)
                        new_lines = f.readlines()
                    
                    if new_lines:
                       
                        temp_df = pd.DataFrame(
                            [line.strip().split(',') for line in new_lines if line.strip()]
                        )

                        if not temp_df.empty:
                            temp_df.columns = [
                                'info', 'GPS_week', 'time', 'sol', 'antenna',
                                'ztd', 'ztdf', 'nan_1', 'nan_2', 'nan_3', 'nan_4',
                                'nan_5', 'nan_6', 'nan_7', 'nan_8', 'nan_9'
                            ]

                            temp_df = temp_df[temp_df['info'] == '$TROP']
                            temp_df = temp_df[['info', 'GPS_week', 'time', 'sol', 'antenna', 'ztd', 'ztdf']]
                            data_frame = pd.concat([data_frame, temp_df], ignore_index=True)
                            temp_df.to_sql('ztd', engine, if_exists='append', index=False)
                            
                            print(f'New ztd data added to database. Number of new rows: {len(temp_df)}')

                        else:
                            print('No valid data in new lines.')
                    
                    
                    last_size = current_size
                
                else:
                    print('No new data found.')

            else:
                print(f'File {file_path} does not exist.')

            time.sleep(check_interval)
            check_count += 1

        except Exception as e:
            print(f'An error occurred: {e}')
            break

    return data_frame


def monitor_pos_file(file_path, check_interval, engine, max_checks=None):

    last_size = 0
    data_frame = pd.DataFrame()
    check_count = 0

    while True:
        try:
            if max_checks and check_count >= max_checks:
                print('Maximum checks reached. Stopping monitoring.')
                break

            if os.path.exists(file_path):
                current_size = os.path.getsize(file_path)
                
                if current_size > last_size:
                    with open(file_path, 'r') as f:
                        f.seek(last_size)
                        new_lines = f.readlines()
                    
                    if new_lines:
                        temp_df = pd.DataFrame(
                            [line.split() for line in new_lines]
                        )
                        
                        if not temp_df.empty:
                            temp_df.columns = [
                                'GPS_week', 'time', 'latitude', 'longitude',
                                'hight', 'sol', 'n_sat', 'sdn', 'sde', 'sdu',
                                 'sdne','sdeu','sdun', 'age', 'ratio'
                            ]

                            temp_df = temp_df.drop(index=0).reset_index(drop=True)
                            data_frame = pd.concat([data_frame, temp_df], ignore_index=True)
                            temp_df.to_sql('positions', engine, if_exists='append', index=False)
                            
                            print(f'New positions data added to database. Number of new rows: {len(temp_df)}')
                        else:
                            print('No valid data in new lines.')
                    
                    # Update last read size
                    last_size = current_size
                
                else:
                    print('No new data found.')

            else:
                print(f'File {file_path} does not exist.')

            time.sleep(check_interval)
            check_count += 1

        except Exception as e:
            print(f'An error occurred: {e}')
            break

    return data_frame


def zhd_cal(positions, pressure):
    zhd_list = []
    for i, row in positions.iterrows():
        longitude = float(row['longitude'])
        height = float(row['hight'])
        zhd = (0.0022768 * pressure)/1 - ((0.00266 * np.cos(longitude)) - (2.8 * 10**-7 *height))
        zhd_list.append(zhd)
    zhd_data = {'zhd': zhd_list}
    zhd_df = pd.DataFrame(zhd_data)
    return zhd_df


def fetch_data(conn, query):
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        print(f'Error fetching data: {e}')
        return pd.DataFrame()


def pwv_cal(zwd_readings, pressure, tempreture,R_w, k_2, k_3):
    pwv_list = []
    for i, row in zwd_readings.iterrows():
        zwd = row['ztd']
        pwv = zwd * 10**6/(pressure*R_w(k_2 + (k_3/tempreture)))
        pwv_list.append(pwv)
    pwv_data = {'pwv': pwv_list}
    pwv_df = pd.DataFrame(pwv_data)
    return pwv_df
