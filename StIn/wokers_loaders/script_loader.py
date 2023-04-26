import threading

from StIn import res_dict


def script_loader(work, dtw):
    i = 0
    while i != 99999999:
        i += 1
    res_dict[threading.current_thread().name] = "саске вернись в деревню"
