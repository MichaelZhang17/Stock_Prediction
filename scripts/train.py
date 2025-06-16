import os
import joblib
import numpy as np
import pandas as pd
import optuna
from sqlalchemy import create_engine
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from lightgbm import LGBMRegressor, early_stopping, log_evaluation
from config import DATABASE_URL


def load_data():
    # Load features table from database
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql("SELECT * FROM daily_features ORDER BY date", engine, parse_dates=['date'])
    # Create target: next-day close price
    df['target'] = df.groupby('symbol')['C'].pct_change().shift(-1)
    df.dropna(inplace=True)
    feature_cols = ['O', 'H', 'L', 'C', 'V', 'rsi_14', 'sma_20']
    X = df[feature_cols].values
    y = df['target'].values
    return X, y


def objective(trial):
    # Suggest hyperparameters
    param = {
        'num_leaves': trial.suggest_int('num_leaves', 31, 255),
        'max_depth': trial.suggest_int('max_depth', 5, 20),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'min_child_samples': trial.suggest_int('min_child_samples', 10, 100),
        'feature_fraction': trial.suggest_float('feature_fraction', 0.6, 1.0),
        'bagging_fraction': trial.suggest_float('bagging_fraction', 0.6, 1.0),
        'bagging_freq': trial.suggest_int('bagging_freq', 1, 10),
        'objective': 'regression',
        'random_state': 42
    }

    # Time series cross-validation
    tscv = TimeSeriesSplit(n_splits=5)
    rmses = []
    for train_index, valid_index in tscv.split(X):
        X_train, X_valid = X[train_index], X[valid_index]
        y_train, y_valid = y[train_index], y[valid_index]
        model = LGBMRegressor(**param)
        model.fit(
            X_train, y_train,
            eval_set=[(X_valid, y_valid)],
            callbacks=[
                early_stopping(stopping_rounds=50),
                log_evaluation(period=100)
            ]
        )
        preds = model.predict(X_valid)
        mse = mean_squared_error(y_valid, preds)
        rmse = np.sqrt(mse)
        rmses.append(rmse)

    # Return average RMSE
    return sum(rmses) / len(rmses)


if __name__ == '__main__':
    # Load data once
    X, y = load_data()

    # Create study
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=50, n_jobs=1)

    print("Best RMSE: {:.4f}".format(study.best_value))
    print("Best params:", study.best_params)

    # Train final model on all data
    best_params = study.best_params
    best_params.update({'objective': 'regression', 'random_state': 42})
    final_model = LGBMRegressor(**best_params)
    final_model.fit(X, y)

    # Save the tuned model
    os.makedirs('models', exist_ok=True)
    model_path = 'models/model.pkl'
    joblib.dump(final_model, model_path)
    print(f"Tuned model saved to {model_path}")
