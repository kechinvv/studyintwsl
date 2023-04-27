import threading
from subprocess import Popen, PIPE

import pip

from StIn import res_dict


def script_creator(work):
    if work.worker.pip_path != '-':
        pip.main(['install', '-r', work.worker.pip_path])
    p = Popen(['python3', work.worker.worker_path], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return p


def script_predictor(p, dtw):
    try:
        output, err = p.communicate(str(dtw).encode('utf8'))
        res_dict[threading.current_thread().name] = (output, "ok")
    except Exception as e:
        res_dict[threading.current_thread().name] = ("", str(e))
