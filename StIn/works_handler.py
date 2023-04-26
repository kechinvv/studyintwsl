import json
import multiprocessing
import os
import threading
import time
import datetime

import GPUtil
import psutil
from sqlalchemy import asc

from StIn import res_dict, db
from StIn.models import Work, MTypes, Statistic
from StIn.wokers_loaders.keras_loader import keras_loader
from StIn.wokers_loaders.pytorch_loader import pytorch_loader
from StIn.wokers_loaders.script_loader import script_loader
from StIn.wokers_loaders.tensor_loader import tensor_loader
from StIn.wokers_loaders.theano_loader import theano_loader

targets = {MTypes.pytorch: pytorch_loader, MTypes.keras: keras_loader, MTypes.tensorflow: tensor_loader,
           MTypes.theano: theano_loader, MTypes.script: script_loader}

app_dir = os.path.dirname(os.path.dirname(__file__))
folder_logs = os.path.join(app_dir, 'logs')


def update_stats(work, m_cpu, m_ram, gpu_data, duration, dtw, res):
    path = os.path.join(app_dir, 'logs', f'{work.id}.txt')
    if os.path.exists(path):
        os.remove(path)
    date = datetime.datetime.now().replace(microsecond=0)
    rows = Statistic.query.filter_by(work_id=work.id).count()
    print(rows)
    stat = Statistic(work_id=work.id, cpu=m_cpu, ram=m_ram, gpu=json.dumps(gpu_data), time=duration, date=date,
                     dtw=json.dumps(dtw), res=json.dumps(res))
    db.session.add(stat)
    db.session.commit()
    work.cpu = round((work.cpu * rows + m_cpu) / (rows + 1), 5)
    work.ram = round((work.ram * rows + m_ram) / (rows + 1), 5)
    work_gpu = json.loads(work.gpu)
    if len(work_gpu) < len(gpu_data):
        upd_gpu = gpu_data
        work.gpu = json.dumps(upd_gpu)
    elif len(work_gpu) == len(gpu_data):
        upd_gpu = work_gpu
        for i, (used, utils) in enumerate(work_gpu):
            upd_gpu[i][0] = (used * rows + gpu_data[i][0]) / (rows + 1)
            upd_gpu[i][1] = (utils * rows + gpu_data[i][1]) / (rows + 1)
        work.gpu = json.dumps(upd_gpu)
    work.time = round((work.time * rows + duration) / (rows + 1), 5)
    db.session.commit()
    if rows > 10000:
        deleting_stat = Statistic.query.filter_by(work_id=work.id).order_by(asc(Statistic.id)).first()
        db.session.delete(deleting_stat)
        db.session.commit()


def get_lvl(lang, dtw):
    work = Work.query.filter_by(language=lang, state=True).first()
    worker_type = work.worker.type
    res = "", "No active work"
    if worker_type:
        start_time = time.time()
        t = threading.Thread(target=targets.get(worker_type), args=(work, dtw,))
        t.start()
        pid = multiprocessing.current_process().pid
        py_proc = psutil.Process(pid)
        counter, cpu_sum, ram_sum, sum_gpu_used, sum_gpu_util = 0, 0, 0, 0, 0
        GPUs = GPUtil.getGPUs()
        gpu_data = [(0, 0)] * len(GPUs)
        while t.is_alive():
            counter += 1
            cpu = py_proc.cpu_percent()
            ram = py_proc.memory_percent()
            cpu_sum += cpu
            ram_sum += ram
            for i, gpu in enumerate(GPUs):
                gpu_used = gpu.memoryUsed
                gpu_util = gpu.memoryUtil * 100
                gpu_data[i][0] += gpu_used
                gpu_data[i][1] += gpu_util
            time.sleep(0.1)
        duration = time.time() - start_time
        if t.name in res_dict:
            res = res_dict.pop(t.name)
        if counter == 0:
            m_cpu, m_ram = 0, 0
        else:
            m_cpu = cpu_sum / counter
            m_ram = ram_sum / counter
            for i, gpu in enumerate(GPUs):
                gpu_data[i][0] /= counter
                gpu_data[i][1] /= counter
        update_stats(work, m_cpu, m_ram, gpu_data, duration, dtw, res)
        res = "1", "Ok"
    else:
        return "", "No active work"
    return res
