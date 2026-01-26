import logging
from nse_daily import NSEDaily
import bhavcopy
import os
import datetime

logger = logging.getLogger(__name__)

def fetch_historical_data():
    logger.info("Starting historical data fetch...")
    # Place data need to be stored.

    data_storage = "C:\\Users\\Abhishek\\Trading_Projects\\MarketAnalyser\\storage\\HISTORICAL_DATA"

    # Define working directory, where files would be saved

    os.chdir(data_storage)

    # Define start and end dates, and convert them into date format

    start_date = datetime.date(2025, 12, 29)
    logger.debug(f"Start date: {start_date}")

    end_date = datetime.date(2026, 1, 13)
    logger.debug(f"End date: {end_date}")

    # Define wait time in seconds to avoid getting blocked

    wait_time = [0, 1]

    # Instantiate bhavcopy class for equities, indices, and derivatives

    # nse = bhavcopy("indices", start_date, end_date, data_storage, wait_time)
    #
    # nse.get_data()
    try:
        logger.debug("Fetching derivatives data...")
        nse = bhavcopy.bhavcopy("derivatives", start_date, end_date, data_storage, wait_time)
        nse.get_data()
        logger.debug("Derivatives data fetched successfully.")

        logger.debug("Fetching equities data...")
        nse = bhavcopy.bhavcopy("equities", start_date, end_date, data_storage, wait_time)
        nse.get_data()
        logger.debug("Equities data fetched successfully.")
    except Exception as e:
        logger.error(f"An error occurred during historical data fetch: {e}")


    # nd = NSEDaily()
    # res= nd.download_by_date('20260113')
    # logger.info(res)
    # res2 = nd.download_by_date_range(date_start='20251229',date_end='20260113',num_workers=1)
    # logger.info(res2)
    logger.info("Historical data fetch completed.")

if __name__ == "__main__":
    fetch_historical_data()