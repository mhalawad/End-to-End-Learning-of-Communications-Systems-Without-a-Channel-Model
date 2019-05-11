# -*- coding: utf-8 -*-
"""trail_tx_rx_model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/171pZcjO0Zbs_NCAE2RMtRJBKTFvI5DQl
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras.layers import *
from sklearn import preprocessing
import tensorflow.keras.backend as K
from sklearn.metrics import mean_squared_error

msg_total = 8
channel = 4
epochs = 5000
Pert_variance = 1e-4
batch_size = 1024

def perturbation(x):
    w = K.random_normal(shape = (channel,2),
    mean=0.0,stddev=Pert_variance**0.5,dtype=None,seed=None)
    xp = ((1-Pert_variance)**0.5)*x + w
#     policy = -K.sum(w*w)
#     print(w_normed.shape)
    return xp

def loss_tx(y_true, y_pred):
    return -y_true*y_pred

def get_policy(inp):
  xp = inp[0]
  x = inp[1]
  w = xp - ((1-Pert_variance)**0.5)*x
  policy = -K.sum(w*w)
  return policy

tx_inp = Input((1,))
embbedings_layer = Dense(msg_total, activation = 'relu')(tx_inp)
layer_dense = Dense(2*channel, activation = 'relu')(embbedings_layer)
to_complex = Reshape((channel,2))(layer_dense)
x = Lambda(lambda x: keras.backend.l2_normalize(x))(to_complex)
xp = Lambda(perturbation)(to_complex)
policy = Lambda(get_policy)([xp,x])

model_policy = keras.models.Model(inputs=tx_inp, outputs=policy)
model_tx = keras.models.Model(inputs=tx_inp, outputs=xp)

model_policy.compile(loss=loss_tx, optimizer='sgd')
print(model_policy.summary())

rx_inp = Input((channel,2))
to_flat = Reshape((2*channel,))(rx_inp)
fc = Dense(msg_total, activation = 'relu')(to_flat)
softmax = Dense(msg_total, activation = 'softmax')(fc)

model_rx = keras.models.Model(inputs=rx_inp, outputs=softmax)

model_rx.compile(loss='mse', optimizer='sgd')
print(model_rx.summary())

loss_tx = []
loss_rx = []
for epoch in range(epochs):
  raw_input = np.random.randint(0,8,(batch_size))
  label = np.zeros((batch_size, 8))
  label[np.arange(batch_size), raw_input] = 1
  tx_input = raw_input/8.0
  xp = model_tx.predict(tx_input)
  y = xp + np.random.normal(0,1,(batch_size, channel,2))
  pred = model_rx.predict(y)
  loss = np.sum(np.square(label - pred), axis = 1)
  print('epoch: ', epoch)
  history_tx = model_policy.fit(tx_input, loss, batch_size=batch_size, epochs=1, verbose=1)
  loss_tx.append(history_tx.history['loss'][0])
  history_rx = model_rx.fit(xp, label, batch_size=batch_size, epochs=1, verbose=1)
  loss_rx.append(history_rx.history['loss'][0])

plt.figure(figsize = (12,5))
plt.subplot(1,2,1)
plt.plot(loss_tx)
plt.subplot(1,2,2)
plt.plot(loss_rx)
plt.show()

#testing
batch_size = 25
raw_input = np.random.randint(0,8,(batch_size))
print(raw_input)
label = np.zeros((batch_size, 8))
label[np.arange(batch_size), raw_input] = 1
tx_input = raw_input/8.0
xp = model_tx.predict(tx_input)
y = xp + np.random.normal(0,1,(batch_size, channel,2))
pred = model_rx.predict(y)
pred_int = np.argmax(pred, axis = 1)
print(pred_int)

