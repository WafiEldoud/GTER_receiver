from functions import *
import threading

if __name__ == "__main__":
    file_pos= "pos"
    file_ztd = 'stats'
    check_interval = 5
    pos_thread = threading.Thread(target=monitor_pos_file, args=(file_pos, check_interval))
    ztd_thread = threading.Thread(target=monitor_ZTD_file, args=(file_ztd, check_interval))

    pos_thread.start()
    ztd_thread.start()
 
    pos_thread.join()
    ztd_thread.join()

    