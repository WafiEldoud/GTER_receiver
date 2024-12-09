from functions import *
import threading
from sqlalchemy import create_engine

engine = create_engine('postgresql+psycopg2://postgres:30486@localhost:5432/postgres')

if __name__ == '__main__':
    file_pos= 'pos'
    file_ztd = 'stats'
    check_interval = 5
    pos_thread = threading.Thread(target=monitor_pos_file, args=(
        file_pos,
        check_interval,
        engine,
        5)
        )
    ztd_thread = threading.Thread(target=monitor_ZTD_file, args=(
        file_ztd,
        check_interval,
        engine,
        5)
        )

    pos_thread.start()
    ztd_thread.start()
    stop_event = threading.Event()
    
    try:
        while pos_thread.is_alive() or ztd_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('Manual interruption received. Stopping threads...')
        stop_event.set()

   
    pos_thread.join()
    ztd_thread.join()
    





    