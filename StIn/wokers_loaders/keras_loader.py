import threading

import tensorflow as tf

from StIn import res_dict


def keras_creator(work):
    model = tf.keras.models.load_model(work.worker.worker_path)
    return model


def keras_predictor(model, dtw):
    try:
        preds = model.predict(dtw)
        res_dict[threading.current_thread().name] = (preds, "ok")
    except Exception as e:
        res_dict[threading.current_thread().name] = ("", str(e))
