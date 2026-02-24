from confluent_kafka import Producer, Consumer
import xgboost as xgb
import warnings
from sklearn.model_selection import train_test_split
import numpy as np
import random

import json
import time
import config


warnings.filterwarnings("ignore", category=UserWarning)  


conf_p = {'bootstrap.servers': config.bootstrap_servers_kafka1}
producer_1 = Producer(conf_p)

conf_c = {'bootstrap.servers': config.bootstrap_servers_kafka0, 'group.id': 'my_consumers'}
consumer_0 = Consumer(conf_c)
consumer_0.subscribe([config.topic_data])


class KafkaCallback(xgb.callback.TrainingCallback):
    def after_iteration(self, model, epoch, evals_log):
        
        metrics = {}
        if 'logloss' in evals_log['eval']:
            metrics['log_loss'] = evals_log['eval']['logloss'][-1]
        if 'rmse' in evals_log['eval']:
            metrics['rmse'] = evals_log['eval']['rmse'][-1]
        if 'mae' in evals_log['eval']:
            metrics['mae'] = evals_log['eval']['mae'][-1]
        if 'error' in evals_log['eval']:
            metrics['error'] = evals_log['eval']['error'][-1]
        if 'auc' in evals_log['eval']:
            metrics['auc'] = evals_log['eval']['auc'][-1]

        data = {'iteration': epoch, **metrics}
        producer_1.produce(config.topic_train_metrics, key='log_loss', value=json.dumps(data))
        producer_1.flush()
        print(f"Sent to Kafka: {data}")
        time.sleep(random.randint(1, 2))
        return False  # Возвращаем False, чтобы продолжить обучение


# Параметры для XGBoost
params = {
    'objective': 'binary:logistic',
    'eval_metric': ['logloss', 'auc', 'rmse', 'mae', 'error'],
    'learning_rate': 0.1,
    'max_depth': 3
}

X_buffer = []
y_buffer = []
batch_size = 50  # Размер батча для обучения

while True:
    message = consumer_0.poll(1000)
    value = message.value()

    if value is None:
        continue

    stock_data = json.loads(value)
    X_buffer.append(stock_data['x'])  # Добавляем в буфер
    y_buffer.append(stock_data['y'])

    # Если накопили batch_size данных, обучаем модель
    if len(X_buffer) >= batch_size:
        X = np.array(X_buffer)
        y = np.array(y_buffer)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=100)
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test, label=y_test)

        if 'bst' in locals():
            # Обновляем существующую модель
            bst = xgb.train(
                params=params,
                dtrain=dtrain,
                num_boost_round=10000,
                xgb_model=bst,
                evals=[(dtest, 'eval')],
                early_stopping_rounds=10,
                callbacks=[KafkaCallback()]
            )
        else:
            # Обучаем новую модель, если её нет
            bst = xgb.train(
                params=params,
                dtrain=dtrain,
                num_boost_round=10000,
                evals=[(dtest, 'eval')],
                early_stopping_rounds=10,
                callbacks=[KafkaCallback()]
            )

        print("Model updated with new batch")

        # Очищаем буфер
        X_buffer.clear()
        y_buffer.clear()
