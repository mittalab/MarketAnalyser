import os
import pandas as pd

BASE_PATH = "storage"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def save_csv(df, path, filename):
    ensure_dir(path)
    full_path = os.path.join(path, filename)
    df.to_csv(full_path, index=False)

def load_csv(path, filename):
    full_path = os.path.join(path, filename)
    if os.path.exists(full_path):
        return pd.read_csv(full_path)
    return None
