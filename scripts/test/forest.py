"""
Tests the CeDAR forest implementation.
"""
import os
import sys
import time
here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here + '/..')

import numpy as np
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier

import cedar
from experiments.utility import data_util, exact_adv_util

seed = 1
n_remove = 1000
n_add = 1000

n_estimators = 100

add = False
delete = False
adv = True
batch = True

n_samples = -1
n_features = 200

if n_samples == -1:
    X_train, X_test, y_train, y_test = data_util.get_data('mfc19', seed, data_dir='data')
    np.random.seed(seed)

else:
    np.random.seed(1)
    X_train = np.random.randint(2, size=(n_samples, n_features), dtype=np.int32)
    np.random.seed(1)
    y_train = np.random.randint(2, size=n_samples, dtype=np.int32)

    np.random.seed(2)
    X_test = np.random.randint(2, size=(10, n_features), dtype=np.int32)
    np.random.seed(2)
    y_test = np.random.randint(2, size=10, dtype=np.int32)

data = np.hstack([X_train, y_train.reshape(-1, 1)])
print(data.shape)
print('data assembled')

t1 = time.time()
m1 = RandomForestClassifier(n_estimators=n_estimators, max_depth=20, max_features=0.2,
                            bootstrap=False, random_state=1).fit(X_train, y_train)
print('\n[SK] build time: {:.7f}s'.format(time.time() - t1))
preds = m1.predict(X_test)
print('accuracy: {:.3f}'.format(accuracy_score(y_test, preds)))
proba = m1.predict_proba(X_test)[:, 1]
print('auc: {:.3f}'.format(roc_auc_score(y_test, proba)))

mf = int(np.sqrt(X_train.shape[1] * 4))
t1 = time.time()
model = cedar.Forest(epsilon=0.5, lmbda=-1, n_estimators=n_estimators,
                     max_depth=20, max_features=0.2, random_state=1).fit(X_train, y_train)
print('\n[CeDAR] build time: {:.7f}s'.format(time.time() - t1))

preds = model.predict(X_test)
print('accuracy: {:.3f}'.format(accuracy_score(y_test, preds)))
proba = model.predict_proba(X_test)[:, 1]
print('auc: {:.3f}'.format(roc_auc_score(y_test, proba)))

if delete:
    if adv:
        delete_indices = exact_adv_util.exact_adversary(X_train, y_train, n_samples=n_remove, seed=seed, verbose=1)
    else:
        delete_indices = np.random.choice(X_train.shape[0], size=n_remove, replace=False)
    print('\ndeleting {} instances'.format(n_remove))

    if batch:
        t1 = time.time()
        model.delete([delete_indices])
        print('delete time: {:.7f}s'.format(time.time() - t1))

    else:
        for i in range(len(delete_indices)):
            t1 = time.time()
            model.delete(delete_indices[i])
            print('delete time: {:.7f}s'.format(time.time() - t1))

    print(model.get_removal_statistics())
    proba = model.predict_proba(X_test)[:, 1]
    preds = model.predict(X_test)
    print('accuracy: {:.3f}'.format(accuracy_score(y_test, preds)))
    print('auc: {:.3f}'.format(roc_auc_score(y_test, proba)))

if add:
    np.random.seed(seed)
    X_add = np.random.randint(2, size=(n_add, X_train.shape[1]), dtype=np.int32)
    np.random.seed(seed)
    y_add = np.random.randint(2, size=n_add, dtype=np.int32)

    if delete:
        X_add = X_train[delete_indices]
        y_add = y_train[delete_indices]
    print('\nadding {} instances'.format(X_add.shape[0]))

    if batch:
        t1 = time.time()
        model.add(X_add, y_add)
        print('add time: {:.7f}s'.format(time.time() - t1))

    else:
        for i in range(X_add.shape[0]):
            t1 = time.time()
            model.add(X_add[[i]], y_add[[i]])
            print('add time: {:.7f}s'.format(time.time() - t1))

    print(model.get_add_statistics())
    proba = model.predict_proba(X_test)[:, 1]
    preds = model.predict(X_test)
    print('accuracy: {:.3f}'.format(accuracy_score(y_test, preds)))
    print('auc: {:.3f}'.format(roc_auc_score(y_test, proba)))
    print()