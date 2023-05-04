import json
import threading

import numpy as np
import tensorflow as tf
from keras.preprocessing import text
from keras.preprocessing.text import tokenizer_from_json
from tensorflow.python.keras.engine.input_layer import InputLayer
from keras.utils.data_utils import pad_sequences

from StIn import res_dict

max_features = 5000


def keras_creator(work):
    model = tf.keras.models.load_model(work.worker.worker_path)
    if work.worker.pip_path != '-':
        with open(work.worker.pip_path) as f:
            data = json.load(f)
            tokenizer = tokenizer_from_json(data)
    else:
        tokenizer = None
    return [model, tokenizer]


def keras_predictor(nn, dtw):
    try:
        model = nn[0]
        tokenizer = nn[1]
        maxlen = 60

        if tokenizer:
            for layer in model.layers:
                if type(layer) == InputLayer:
                    maxlen = layer.input_shape[0][1]
            list_tokenized = tokenizer.texts_to_sequences([dtw])
            input_dtw = pad_sequences(list_tokenized, maxlen=maxlen)
        else:
            input_dtw = dtw
        preds = model.predict(input_dtw)

        max_res_ind = np.unravel_index(np.argmax(preds, axis=None), preds.shape)
        res_dict[threading.current_thread().name] = (str(max_res_ind[1]), "ok")
    except Exception as e:
        res_dict[threading.current_thread().name] = ("", str(e))
