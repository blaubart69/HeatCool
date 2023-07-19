# importing datetime module
import logging
import sys
import time
import datetime
import requests
import csv
from collections import namedtuple

# sample CSV data
# -----------
# start                   end                     baseprice     unit
# 17.07.2023 12:00:00     17.07.2023 13:00:00     7.73          Cent/kWh
# 17.07.2023 13:00:00     17.07.2023 14:00:00     7.73          Cent/kWh
# 17.07.2023 14:00:00     17.07.2023 15:00:00     7.91          Cent/kWh
# 17.07.2023 15:00:00     17.07.2023 16:00:00     7.74          Cent/kWh
#
# #csv_string = "start;end;baseprice;unit\n18.07.2023 21:00:00;18.07.2023 22:00:00;15.91;Cent/kWh\n18.07.2023 22:00:00;18.07.2023 23:00:00;13.93;Cent/kWh\n18.07.2023 23:00:00;19.07.2023 00:00:00;11.79;Cent/kWh\n19.07.2023 00:00:00;19.07.2023 01:00:00;10.81;Cent/kWh\n19.07.2023 01:00:00;19.07.2023 02:00:00;10.20;Cent/kWh\n19.07.2023 02:00:00;19.07.2023 03:00:00;9.73;Cent/kWh\n19.07.2023 03:00:00;19.07.2023 04:00:00;9.53;Cent/kWh\n19.07.2023 04:00:00;19.07.2023 05:00:00;9.52;Cent/kWh\n19.07.2023 05:00:00;19.07.2023 06:00:00;10.07;Cent/kWh\n19.07.2023 06:00:00;19.07.2023 07:00:00;12.00;Cent/kWh\n19.07.2023 07:00:00;19.07.2023 08:00:00;12.17;Cent/kWh\n19.07.2023 08:00:00;19.07.2023 09:00:00;11.70;Cent/kWh\n19.07.2023 09:00:00;19.07.2023 10:00:00;9.99;Cent/kWh\n19.07.2023 10:00:00;19.07.2023 11:00:00;8.65;Cent/kWh\n19.07.2023 11:00:00;19.07.2023 12:00:00;8.30;Cent/kWh\n19.07.2023 12:00:00;19.07.2023 13:00:00;8.29;Cent/kWh\n19.07.2023 13:00:00;19.07.2023 14:00:00;8.30;Cent/kWh\n19.07.2023 14:00:00;19.07.2023 15:00:00;8.82;Cent/kWh\n19.07.2023 15:00:00;19.07.2023 16:00:00;8.84;Cent/kWh\n19.07.2023 16:00:00;19.07.2023 17:00:00;8.30;Cent/kWh\n19.07.2023 17:00:00;19.07.2023 18:00:00;7.91;Cent/kWh\n19.07.2023 18:00:00;19.07.2023 19:00:00;7.99;Cent/kWh\n19.07.2023 19:00:00;19.07.2023 20:00:00;10.41;Cent/kWh\n19.07.2023 20:00:00;19.07.2023 21:00:00;10.72;Cent/kWh\n19.07.2023 21:00:00;19.07.2023 22:00:00;11.70;Cent/kWh\n19.07.2023 22:00:00;19.07.2023 23:00:00;12.49;Cent/kWh\n19.07.2023 23:00:00;20.07.2023 00:00:00;11.02;Cent/kWh\n"

SECONDS_IN_A_DAY = 24 * 60 * 60

#------------------------------------------------------------------------------
def fetch_awattar_data_next_48hours(startEpoch : int):
#------------------------------------------------------------------------------
    #                                                start=1689724800000&end=1689811200000
    url = "https://api.awattar.at/v1/marketdata/csv?start={start}&end={end}".format(
          start=startEpoch * 1000
        , end=(startEpoch + (SECONDS_IN_A_DAY*2)) * 1000)

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        return response.text

    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)    

#------------------------------------------------------------------------------
def check_values(tomorrow_values : list[any], tomorrow_str : str):
#------------------------------------------------------------------------------
    count = 0
    for idx,v in enumerate(tomorrow_values):
        count += 1
        time_expected = "{0} {1:02d}:00:00".format(tomorrow_str,idx)
        if v.start != time_expected:
            logging.error("expected: %s, got: %s", time_expected, v.start)
            return False
        
    if count != 24:
        logging.error("expected 24 values, got: %d", count)
        return False 

    return True

#------------------------------------------------------------------------------
def find_starting_index_cheapest_hours(hours : list[any]):
#------------------------------------------------------------------------------
    lowest_sum = float('inf')
    lowest_start_index = -1

    for i in range(len(hours) - 3):
        current_sum = sum( map(lambda x: float(x.baseprice) , hours[i:i+4] ))

        if current_sum < lowest_sum:
            lowest_sum = current_sum
            lowest_start_index = i

    return lowest_start_index

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("START")

#with open('data.csv','r') as infile:
#    csv_string = infile.read()

csv_string = fetch_awattar_data_next_48hours(int(time.time()))


reader = csv.reader(filter(None,csv_string.split('\n')), delimiter=';')
Data = namedtuple("Data", next(reader))
# "Data" is now a type with the fields "start", "end", "baseprice", "unit"
# "rows" is a list of namedtuples
rows = [Data(*line) for line in reader]

tomorrow = datetime.date.today() + datetime.timedelta(days=1)
tomorrow_str = tomorrow.strftime('%d.%m.%Y')

tomorrow_hours = [ row for row in rows if row.start.startswith(tomorrow_str) ]

logging.info("calculated tomorrow: %s", tomorrow_str)
logging.info("tomorrow value count: %d", len(tomorrow_hours) )

if not check_values(tomorrow_hours, tomorrow_str):
    sys.exit(12)

logging.info("CHECKPOINT: check of 24 time values ok")

idx_lowest_hours = find_starting_index_cheapest_hours(tomorrow_hours)

logging.info("idx_lowest_hours: %d, from %s to %s", 
      idx_lowest_hours
    , tomorrow_hours[idx_lowest_hours].start
    , tomorrow_hours[idx_lowest_hours+3].end)


