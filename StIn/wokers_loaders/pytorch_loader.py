import multiprocessing
import threading

from StIn import res_dict


def pytorch_loader(dtw):
    pid = multiprocessing.current_process().pid
    res_dict[threading.current_thread().name] = ""
