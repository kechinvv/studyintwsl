import sys
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
    p = None
    try:
        p = Popen([sys.executable, path], stdin=PIPE, stdout=PIPE,
                  stderr=PIPE)
        output, err = p.communicate(str(dtw).encode('utf-8'), timeout=15)
        print(err)
        res_dict[threading.current_thread().name] = (str(output.decode('ascii').strip()), "ok")
    except Exception as e:
        if p:
            p.kill()
        res_dict[threading.current_thread().name] = ("", str(e))
