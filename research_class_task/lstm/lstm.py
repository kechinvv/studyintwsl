import json

import numpy as np
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from keras.preprocessing import text
from keras.preprocessing.text import tokenizer_from_json

from keras.utils.data_utils import pad_sequences
from sklearn.model_selection import train_test_split
from tensorflow.python.keras import Input
from tensorflow.python.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.python.keras.engine.input_layer import InputLayer
from tensorflow.python.keras.layers import Embedding, LSTM, Dense, Activation, Dropout
from tensorflow.python.keras.models import Model, load_model
from tensorflow.python.keras.optimizer_v2.rmsprop import RMSprop

max_features = 5000
maxlen = 60

train = pd.read_csv("../data.csv")
# train = train.sample(frac=1)

x = train["data"].fillna(0).values
list_classes = ["zpd", "hard", "easy"]
y = train[list_classes].values

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

tokenizer = text.Tokenizer(filters='[]\'\" ', split=',', num_words=max_features)
tokenizer.fit_on_texts(list(x_train))
# train data
list_tokenized_train = tokenizer.texts_to_sequences(x_train)
X_tr = pad_sequences(list_tokenized_train, maxlen=maxlen)
# test data
list_tokenized_test = tokenizer.texts_to_sequences(x_test)
X_te = pad_sequences(list_tokenized_test, maxlen=maxlen)


def my_LSTM():
    inputs = Input(name='inputs', shape=[maxlen])
    layer = Embedding(max_features, 128, input_length=maxlen)(inputs)
    layer = LSTM(64)(layer)
    layer = Dense(256, name='FC1')(layer)
    layer = Activation('relu')(layer)
    layer = Dropout(0.1)(layer)
    layer = Dense(3, name='out_layer')(layer)
    layer = Activation('softmax')(layer)
    model = Model(inputs=inputs, outputs=layer)
    return model


def train():
    tokenizer_json = tokenizer.to_json()
    with open('tokenizer.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(tokenizer_json, ensure_ascii=False))

    model = my_LSTM()
    model.summary()
    model.compile(loss='binary_crossentropy', optimizer=RMSprop(), metrics=['accuracy'])

    batch_size = 1024  # big beefy GPUs like large batches
    epochs = 100

    file_path = "weightslstm.hdf5"
    checkpoint = ModelCheckpoint(file_path, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
    early = EarlyStopping(monitor="val_loss", mode="min", patience=5)

    callbacks_list = [checkpoint, early]  # early
    model.fit(X_tr, y_train,
              batch_size=batch_size,
              epochs=epochs,
              shuffle=True,
              validation_split=0.25,
              callbacks=callbacks_list)

    model.save('stin_model_lstm_2.keras')
    print(model.evaluate(X_te, y_test))


def show_sentence(sent_idx, model):
    print('# Input Sentence:\n `{}`'.format(x_test[sent_idx]))
    c_pred = model.predict(X_te[sent_idx:sent_idx + 1])[0]
    print('## Categories')
    for k, v, p in zip(list_classes, y[sent_idx], c_pred):
        print('- {}, Prediction: {:2.2f}%'.format(k, 100 * p))


def hand_sentence(text, model):
    print('# Manual Input Sentence:\n `{}`'.format(text))
    list_tokenized = tokenizer.texts_to_sequences(text)
    X_text = pad_sequences(list_tokenized, maxlen=maxlen)
    c_pred = model.predict(X_text[0:1])[0]
    print('## Categories')
    for k, p in zip(list_classes, c_pred):
        print('- {}, Prediction: {:2.2f}%'.format(k, 100 * p))


if __name__ == '__main__':
    train()
    with open('tokenizer.json') as f:
        data = json.load(f)
        tokenizer = tokenizer_from_json(data)
    model = load_model('stin_model_lstm.keras')
    for layer in model.layers:
        print(type(layer))
        if type(layer) == InputLayer:
            print(layer.input_shape[0][1])
    print(model.summary())
    print(model.evaluate(X_te, y_test))
    list_tokenized = tokenizer.texts_to_sequences(["[40.36, 5.97, 18.04, 26.79, 13.73]"])
    xxx = pad_sequences(list_tokenized, maxlen=maxlen)
    res = model.predict(xxx)
    print(res)
    max_res_ind = np.unravel_index(np.argmax(res, axis=None), res.shape)
    print(max_res_ind[1])

# hand_sentence(""" """)
# print(model.evaluate(X_t, y))
# show_sentence(0)
# show_sentence(25)
# show_sentence(50)
