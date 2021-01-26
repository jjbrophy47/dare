"""
Preprocesses dataset but keep continuous variables.
"""
import os

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder


def dataset_specific(random_state, test_size):

    # retrieve dataset
    df = pd.read_csv('KaggleV2-May-2016.csv')

    # remove nan rows
    nan_rows = df[df.isnull().any(axis=1)]
    print('nan rows: {}'.format(len(nan_rows)))
    df = df.dropna()

    # transform timestamps into separate year, month, and day columns
    scheduled_date = pd.to_datetime(df['ScheduledDay'])
    df['scheduled_day'] = scheduled_date.dt.day
    df['scheduled_month'] = scheduled_date.dt.month
    df['scheduled_year'] = scheduled_date.dt.year
    df['scheduled_hour'] = scheduled_date.dt.hour

    appointment_date = pd.to_datetime(df['AppointmentDay'])
    df['appointment_day'] = appointment_date.dt.day
    df['appointment_month'] = appointment_date.dt.month
    df['appointment_year'] = appointment_date.dt.year
    df['appointment_hour'] = appointment_date.dt.hour

    # remove columns
    remove_cols = ['PatientId', 'AppointmentID', 'ScheduledDay', 'AppointmentDay']
    df = df.drop(remove_cols, axis=1)

    # split into train and test
    indices = np.arange(len(df))
    n_train_samples = int(len(indices) * (1 - test_size))

    np.random.seed(random_state)
    train_indices = np.random.choice(indices, size=n_train_samples, replace=False)
    test_indices = np.setdiff1d(indices, train_indices)

    train_df = df.iloc[train_indices]
    test_df = df.iloc[test_indices]

    # categorize attributes
    columns = list(df.columns)
    label = ['No-show']
    numeric = ['Age', 'Scholarship', 'Hipertension', 'Diabetes',
               'Alcoholism', 'Handcap', 'SMS_received',
               'scheduled_day', 'scheduled_month', 'scheduled_year', 'scheduled_hour',
               'appointment_day', 'appointment_month', 'appointment_year', 'appointment_hour']
    categorical = list(set(columns) - set(numeric) - set(label))

    return train_df, test_df, label, numeric, categorical


def main(random_state=1, test_size=0.2, out_dir='continuous'):

    train_df, test_df, label, numeric, categorical = dataset_specific(random_state=random_state,
                                                                      test_size=test_size)

    # binarize inputs
    ct = ColumnTransformer([('kbd', 'passthrough', numeric),
                            ('ohe', OneHotEncoder(sparse=False, handle_unknown='ignore'), categorical)])
    train = ct.fit_transform(train_df)
    test = ct.transform(test_df)

    # binarize outputs
    le = LabelEncoder()
    train_label = le.fit_transform(train_df[label].to_numpy().ravel()).reshape(-1, 1)
    test_label = le.transform(test_df[label].to_numpy().ravel()).reshape(-1, 1)

    # combine binarized data
    train = np.hstack([train, train_label]).astype(np.int32)
    test = np.hstack([test, test_label]).astype(np.int32)

    print('train.shape: {}, label sum: {}'.format(train.shape, train[:, -1].sum()))
    print('test.shape: {}, label sum: {}'.format(test.shape, test[:, -1].sum()))

    # save to numpy format
    print('saving...')
    os.makedirs(out_dir, exist_ok=True)
    np.save(os.path.join(out_dir, 'train.npy'), train)
    np.save(os.path.join(out_dir, 'test.npy'), test)


if __name__ == '__main__':
    main()