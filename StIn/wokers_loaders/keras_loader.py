import threading

import numpy as np
import tensorflow as tf
from keras.preprocessing import text
from tensorflow.python.keras.engine.input_layer import InputLayer
from keras.utils.data_utils import pad_sequences


from StIn import res_dict

max_features = 5000

tokenizer = text.Tokenizer(filters='[]\'\" ', split=',', num_words=max_features)


def keras_creator(work):
    model = tf.keras.models.load_model(work.worker.worker_path)
    return model


def keras_predictor(model, dtw):
    try:
        maxlen = 60

        for layer in model.layers:
            if type(layer) == InputLayer:
                maxlen = layer.input_shape[0][1]

        list_tokenized = tokenizer.texts_to_sequences([dtw])
        input_dtw = pad_sequences(list_tokenized, maxlen=maxlen)

        preds = model.predict(input_dtw)

        max_res_ind = np.unravel_index(np.argmax(preds, axis=None), preds.shape)
        res_dict[threading.current_thread().name] = (max_res_ind, "ok")
    except Exception as e:
        res_dict[threading.current_thread().name] = ("", str(e))
