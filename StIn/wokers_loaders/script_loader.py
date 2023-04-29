import threading
from subprocess import Popen, PIPE

import pip

from StIn import res_dict


def script_creator(work):
    if not work.worker.worker_path.endswith(".py"):
        raise Exception("It is not .py file")
    if work.worker.pip_path != '-':
        pip.main(['install', '-r', work.worker.pip_path])
    return work.worker.worker_path


def script_predictor(path, dtw):
    try:
        p = Popen(['python3', path], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(str(dtw).encode('utf8'))
        res_dict[threading.current_thread().name] = (output, "ok")
    except Exception as e:
        res_dict[threading.current_thread().name] = ("", str(e))
