import multiprocessing
import threading

import theano
from six.moves import cPickle

from StIn import res_dict


def theano_creator(work):
    with open(work.worker.worker_path, 'rb') as f:
        classifier = cPickle.load(f)
        # compile a predictor function
        predictor = theano.function(
            inputs=[classifier.input],
            outputs=classifier.y_pred)
        # model = theano.misc.pkl_utils.load(f)
        return predictor


def theano_predictor(predictor, dtw):
    try:
        preds = predictor(dtw)
        res_dict[threading.current_thread().name] = (preds, "ok")
    except Exception as e:
        res_dict[threading.current_thread().name] = ("", str(e))
