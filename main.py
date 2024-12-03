from functions import *
import threading
import psycopg2
from sqlalchemy import create_engine

engine = create_engine('postgresql+psycopg2://postgres:30486@localhost:5432/postgres')

conn = psycopg2.connect(
    database= 'postgres',
    user = 'postgres',
    password = '30486',
    host = 'localhost',
    port = '5432'
)

if __name__ == "__main__":
    file_pos= "pos"
    file_ztd = 'stats'
    check_interval = 5
    pos_thread = threading.Thread(target=monitor_pos_file, args=(file_pos, check_interval))
    ztd_thread = threading.Thread(target=monitor_ZTD_file, args=(file_ztd, check_interval))

    pos_thread.start()
    ztd_thread.start()

    output = monitor_pos_file(file_pos, check_interval)

    # surface_pressure = 0
    # zhd_residuals = zhd_cal(pos_thread['longitude'], pos_thread['height'], surface_pressure)

    # zwd_residuals = zwd_cal(ztd_thread['ztd'], zhd_residuals['zhd'])

    # pressure = 0
    # tempreture = 0
    # R_w = 0
    # k_2 = 0
    # k_3 = 0
    # pwv = pwv_cal(zwd_residuals['zwd'], pressure, tempreture,R_w, k_2, k_3)
    # output.to_sql('ztd', engine, if_exists='replace')


    pos_thread.join()
    ztd_thread.join()

    