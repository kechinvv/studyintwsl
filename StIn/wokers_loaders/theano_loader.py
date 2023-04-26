import multiprocessing
import threading

from StIn import res_dict


def theano_loader(dtw):
    pid = multiprocessing.current_process().pid
    res_dict[threading.current_thread().name] = ""
