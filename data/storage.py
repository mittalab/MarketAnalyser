import os
import csv
import pandas as pd
import logging

logger = logging.getLogger(__name__)

BASE_PATH = "storage"

def ensure_dir(path):
    if not os.path.exists(path):
        logger.debug(f"Creating directory at {path}")
        os.makedirs(path)

# def save_csv(df, path, filename):
#     ensure_dir(path)
#     full_path = os.path.join(path, filename)
#     df.to_csv(full_path, index=False)

# def load_csv(path, filename):
#     full_path = os.path.join(path, filename)
#     if os.path.exists(full_path):
#         return pd.read_csv(full_path)
#     return None

def save_csv(data_list, path, filename):
    """
    data_list: List[Dict]
    """
    logger.info(f"Saving data to {filename} in {path}")
    if not data_list:
        logger.warning("Data list is empty, nothing to save.")
        return

    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, filename)

    fieldnames = list(data_list[0].keys())

    with open(file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_list)

def load_csv(path, filename):
    logger.info(f"Loading data from {filename} in {path}")
    file_path = os.path.join(path, filename)

    if not os.path.exists(file_path):
        logger.warning(f"File not found at {file_path}")
        return None

    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            data.append(dict(row))

    return data
