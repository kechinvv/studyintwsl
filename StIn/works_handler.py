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
from StIn.models import Work, MTypes, Statistics
from StIn.wokers_loaders.keras_loader import keras_creator, keras_predictor
from StIn.wokers_loaders.pytorch_loader import pytorch_creator, pytorch_predictor
from StIn.wokers_loaders.script_loader import script_creator, script_predictor

model_creators = {MTypes.pytorch: pytorch_creator, MTypes.keras: keras_creator, MTypes.script: script_creator}
model_predictors = {MTypes.pytorch: pytorch_predictor, MTypes.keras: keras_predictor, MTypes.script: script_predictor}

app_dir = os.path.dirname(os.path.dirname(__file__))
folder_logs = os.path.join(app_dir, 'logs')

active_models = {}


def update_stats(work, m_cpu, m_ram, gpu_data, duration, dtw, res):
    path = os.path.join(app_dir, 'logs', f'work-{work.id}.txt')
    if os.path.exists(path):
        os.remove(path)
    date = datetime.datetime.now().replace(microsecond=0)
    rows = Statistics.query.filter_by(work_id=work.id).count()
    stat = Statistics(work_id=work.id, cpu=m_cpu, ram=m_ram, gpu=json.dumps("gpu_data"), time=duration, date=date,
                      dtw=json.dumps(""), res=json.dumps(""))
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
        deleting_stat = Statistics.query.filter_by(work_id=work.id).order_by(asc(Statistics.id)).first()
        db.session.delete(deleting_stat)
        db.session.commit()


def get_lvl(lang, dtw):
    work = Work.query.filter_by(language=lang, state=True).first()
    worker_type = work.worker.type
    res = "", "No active work"
    if worker_type:
        start_time = time.time()
        t = threading.Thread(target=model_predictors.get(worker_type), args=(active_models[work.id][1], dtw,))
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
    else:
        return "", "No active work"
    return res


def create_model(work):
    active_models[work.id] = work.worker.type, model_creators.get(work.worker.type)(work)


def delete_model(work):
    if work.id in active_models.keys():
        del active_models[work.id]
