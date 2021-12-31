import requests
import json
import time
import argparse
import os
import logging
from datetime import date, datetime

from scraperparams import url, req_post_data, headers

def scrape():
    r = requests.post(url, data=req_post_data, headers=headers)

    print(r)
    logging.info(r)
    json_data = json.dumps(r.json())
    
    # print(json_data)
    
    current_time: datetime = datetime.now()
    print(current_time)
    file_name = f"{current_time.year}-{current_time.month:02d}-{current_time.day:02d} "\
        f"{current_time.hour:02d}{current_time.minute:02d}"
    print(f"{file_name}")
    if not args.nofile:
        with open(f'dumps/{file_name}.json', 'w', encoding='utf-8') as f:
            f.write(json_data)

parser = argparse.ArgumentParser(description=\
    'Scrape Indiegogo\'s community projects trending top 36')
parser.add_argument('-r', '--run', action="store_true", help="run continously")
parser.add_argument('-at', '--start-at', nargs=2, dest='start_at',
    help="time to start at in the format YYYY-MM-DD HH:MM")
parser.add_argument('-nf', '--no-file', action="store_true", dest='nofile',
    help="Dont write response to file, mainly for testing")
args = parser.parse_args()

# To figure out what the process of the script
pid = os.getpid()
print(f"PID: {pid}")
logging.basicConfig(
    filename=f'scraper-pid-{pid}.log', encoding='utf-8', level=logging.INFO,
    format='%(asctime)s %(message)s'
)

try:
    if args.start_at:
        start_time = datetime.strptime(
            f'{args.start_at[0]} {args.start_at[1]}', '%Y-%m-%d %H:%M')
        print(f'start time: {start_time}')
        logging.info(f'start time {start_time}')
        interval_passed = False
        while not interval_passed:
            time_now = datetime.now()
            if start_time < time_now:
                interval_passed = True
            else:
                time.sleep(0.05)
                c = start_time - time_now
                print(f"sleeping {c.days:2} days {c.seconds:3} seconds " \
                    f"{time_now} PID {str(pid)}\r", end='')

    if args.run: 
        # Future intervals are relative to the first scrape
        # Put this here as the other methods introduces "drift"
        # which can lead to it drifting by up to 40 seconds over a day
        # about 0.00500 second per run
        last_scrape_time = datetime.now().replace(microsecond=0)
        while args.run:
            try:
                print('\n')
                scrape()
                # Because micoseconds exist; we rounded down the microseconds
                # sleep at least one second to prevent running again in the same second
                time.sleep(1)
                scrape_interval_passed = False
                while not scrape_interval_passed:
                    time_now = datetime.now().replace(microsecond=0)
                    if  (time_now - last_scrape_time).seconds % 600 == 0:
                        scrape_interval_passed = True
                    else:
                        c = 600 - ((time_now - last_scrape_time).seconds % 600)
                        print(f"sleeping {c:3} seconds PID {str(pid)}\r", end='')
                        time.sleep(0.05)
                # for i in range(60*10):
                #     time.sleep(1)
                #     print(f"sleeping {i:03}/{60*10} seconds\r", end='')
            except KeyboardInterrupt:
                print("\nProgramme have stopped")
                logging.info('Programme stopped by user')
                args.run = False
                exit
            except Exception as e:
                logging.critical(e)
    else:
        scrape()
except KeyboardInterrupt:
    print("\nProgramme have stopped")
    logging.info('Programme stopped by user')
except Exception as e:
    logging.critical(e)