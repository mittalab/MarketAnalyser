from nse_daily import NSEDaily
import bhavcopy
import os
import datetime

# Place data need to be stored.

data_storage = "C:\\Users\\Abhishek\\Trading_Projects\\MarketAnalyser\\storage\\HISTORICAL_DATA"

# Define working directory, where files would be saved

os.chdir(data_storage)

# Define start and end dates, and convert them into date format

start_date = datetime.date(2025, 12, 29)

end_date = datetime.date(2026, 1, 13)

# Define wait time in seconds to avoid getting blocked

wait_time = [0, 1]

# Instantiate bhavcopy class for equities, indices, and derivatives

# nse = bhavcopy("indices", start_date, end_date, data_storage, wait_time)
#
# nse.get_data()

nse = bhavcopy.bhavcopy("derivatives", start_date, end_date, data_storage, wait_time)

nse.get_data()

nse = bhavcopy.bhavcopy("equities", start_date, end_date, data_storage, wait_time)

nse.get_data()



# nd = NSEDaily()
# res= nd.download_by_date('20260113')
# print(res)
# res2 = nd.download_by_date_range(date_start='20251229',date_end='20260113',num_workers=1)
# print(res2)