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
    # Create target: next-day return
    df['target'] = df.groupby('symbol')['C'].pct_change().shift(-1)
    df.dropna(inplace=True)
    feature_cols = ['O', 'H', 'L', 'C', 'V', 'rsi_14', 'sma_20']
    X = df[feature_cols].values
    y = df['target'].values
    return X, y


def objective(trial):
    # Load data inside the objective
    X, y = load_data()

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
    for train_idx, valid_idx in tscv.split(X):
        X_train, X_valid = X[train_idx], X[valid_idx]
        y_train, y_valid = y[train_idx], y[valid_idx]
        model = LGBMRegressor(**param)
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_valid, y_valid)],
            callbacks=[
                early_stopping(stopping_rounds=50),
                log_evaluation(period=100)
            ],
        )
        preds = model.predict(X_valid)
        rmse = np.sqrt(mean_squared_error(y_valid, preds))
        rmses.append(rmse)

    # Return average RMSE
    return float(np.mean(rmses))


def train_and_save(trials: int = 50, model_path: str = 'models/model.pkl'):
    # Create study
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=trials)

    # Train final model on all data using best params
    X, y = load_data()
    best_params = study.best_params
    best_params.update({'objective': 'regression', 'random_state': 42})
    final_model = LGBMRegressor(**best_params)
    final_model.fit(X, y)

    # Save the tuned model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(final_model, model_path)
    print(f"Tuned model saved to {model_path}")

