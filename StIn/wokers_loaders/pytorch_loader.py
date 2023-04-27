import threading

import torch

from StIn import res_dict


def pytorch_creator(work):
    model = torch.load(work.worker.worker_path)
    model.eval()
    return model


def pytorch_predictor(model, dtw):
    try:
        with torch.inference_mode():
            preds = model(dtw)
        res_dict[threading.current_thread().name] = (preds, "ok")
    except Exception as e:
        res_dict[threading.current_thread().name] = ("", str(e))
