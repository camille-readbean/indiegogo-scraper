from datetime import datetime, time, timezone
from os import times, walk

import csv, json
from typing import ChainMap


# To put in rankings_snapshots.csv late
"""
timestamp, camp1id, camp2id, camp3id . . . 

"""
ranking_headers = ["timestamp"]
for i in range(36):
    ranking_headers.append(f"campaign_{i+1:02d}_id")
# rankings_snapshots_list= [ranking_headers]

with open('rankings_snapshots.csv', 'w', newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(ranking_headers)


# To put in campaign_snapshots.csv
"""
timestamp, project_id, ranking, title, project_type,  . . . 

"""
campaign_records_headers = \
[
    "timestamp", "project_id", "rank", "rank delta",
    "funds_raised_amount", "funds raised delta", "dollar per rank raised",
    "funds_raised_percent",
    "currency", "days left",
    "is_indemand", "is_pre_launch",
]
# campaign_snapshots_list = [campaign_records_headers]

with open('campaign_snapshots.csv', 'w', newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(campaign_records_headers)


# To put in campaigns_details.csv
# One table containing campaign details
campaigns_details_csv_headers = \
[
    "project_id", "title(s)",
    "top 6 count", "rank / amt delta list", "average dollar per rank raised",
    "tagline(s)", "cetegory", "tags",
    "currency", "open_date", "close_date", "clickthrough_url",
    "is_indemand", "is_prelaunch", "comments"
]

class Campaign:
    def __init__(self,
        ranking, campaign_rank, timestamp
    ):
        self.project_id: str = str(ranking["project_id"])
        self.title: str = ranking["title"]
        self.last_rank: str = campaign_rank
        self.fund_raised_amount = int(ranking["funds_raised_amount"])
        self.funds_raised_percent = float(ranking["funds_raised_percent"])
        self.tagline = ranking["tagline"]
        self.category = ranking["category"]
        self.tags = ranking["tags"]
        self.currency = ranking["currency"]

        self.open_date: datetime = datetime.strptime(ranking['open_date'], "%Y-%m-%dT%H:%M:%S%z")
        self.close_date: datetime = datetime.strptime(ranking['close_date'], "%Y-%m-%dT%H:%M:%S%z")

        self.clickthrough_url = ranking["clickthrough_url"]
        self.is_indemand = ranking['is_indemand']
        self.is_prelaunch = ranking['is_pre_launch']

        self.rank_delta = 0
        self.funds_raised_delta = 0
        self.dollar_per_rank_raised = 0
        self.dollar_per_rank_raised_list = []
        self.avg_dollar_per_rank_raised = 0
        self.titles_history = [ranking['title']]
        self.taglines_history = [ranking['tagline']]
        # For some reason the included time stamp in the file is parsed to UTC -16HRS
        self.last_timetstamp: datetime = datetime.strptime(
            timestamp, "%Y-%m-%d %H%M").replace(tzinfo=timezone.utc)
        self.days_left = (
            self.close_date - self.last_timetstamp ).days
        self.top_six_count = 0
        self.rank_amt_delta_list = []
        self.comments = []

campaigns_store: dict[str: Campaign] = {}

file_list = next(walk('dumps'))[2]
last_timestamp = None
for file in file_list:
    # Should give in the form of %Y-%m-%d %H%M
    timestamp = ''.join(file.split('.')[:1])

    if last_timestamp == None:
        last_timestamp = timestamp

    # # Use to set range of dates to get
    # if int(file.split(' ')[0].split('-')[2]) < 28:
    #     continue

    # if int(file.split(' ')[0].split('-')[2]) > 30:
    #     continue

    print(f'Processing record: {timestamp}\r', end='')

    with open(f'dumps/{file}', 'r') as file:
        rankings_snapshot_json = json.load(file)['response']['discoverables']

    campaign_rank = 1
    ranking_list = [timestamp]
    for ranking in rankings_snapshot_json:
        campaign = Campaign(ranking, campaign_rank, timestamp)

        ranking_list.append(campaign.project_id)

        
        if campaign.project_id in campaigns_store.keys():
            # Calculate rank_delta, funds_raised_delta
            # Update campaigns_store_keys with newest object
            # Update campaign object's 
            #   self.top_six_count
            #   self.rank_amt_delta_list
            #   self.dollar_per_rank_raised
            #   taglines and titles if changed
            last_campaign: Campaign = campaigns_store[campaign.project_id]
            if last_campaign.title != campaign.title:
                campaign.titles_history.extend(last_campaign.titles_history)
                campaign.titles_history.append(campaign.title)
            if last_campaign.tagline != campaign.tagline:
                campaign.taglines_history.extend(last_campaign.taglines_history)
                campaign.taglines_history.append(last_campaign.title)
            campaign.rank_delta = - (campaign.last_rank - last_campaign.last_rank)
            campaign.funds_raised_delta = int (campaign.fund_raised_amount -
                last_campaign.fund_raised_amount)

            campaign.dollar_per_rank_raised_list.extend(
                last_campaign.dollar_per_rank_raised_list 
            )
            campaign.rank_amt_delta_list.extend(last_campaign.rank_amt_delta_list)
            campaign.comments = last_campaign.comments

            if campaign.funds_raised_delta != 0 and campaign.rank_delta != 0:
                campaign.dollar_per_rank_raised = round(
                    campaign.funds_raised_delta / campaign.rank_delta, 3
                )
                campaign.dollar_per_rank_raised_list.append(campaign.dollar_per_rank_raised)
                campaign.rank_amt_delta_list.append(
                f"{campaign.last_timetstamp} rank +({campaign.rank_delta}) "
                f"by ${campaign.funds_raised_delta}")
            elif campaign.funds_raised_delta > 0 and campaign.rank_delta == 0:
                campaign.comments.append(f"{campaign.last_timetstamp} Contributions of "\
                f"{campaign.funds_raised_delta} did not raise rank ({campaign.last_rank})")
            
            campaign.top_six_count = last_campaign.top_six_count
            if campaign_rank <= 6:
                campaign.top_six_count += 1
            

            campaigns_store[campaign.project_id] = campaign
            
        else:
            campaigns_store.update(
                {
                    campaign.project_id : campaign
                }
            )

        campaign_snapshots = \
            [
                timestamp, campaign.project_id, 
                campaign_rank, campaign.rank_delta,
                campaign.fund_raised_amount, campaign.funds_raised_delta, 
                campaign.dollar_per_rank_raised,
                campaign.funds_raised_percent, campaign.currency, campaign.days_left,
                campaign.is_indemand, campaign.is_prelaunch
            ]
        
        campaign_rank += 1
        with open('campaign_snapshots.csv', 'a', newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(campaign_snapshots)


    with open('rankings_snapshots.csv', 'a', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(ranking_list)

    last_timestamp = timestamp
    
print(f"\nCampaigns: {len(campaigns_store.keys())}")
with open('campaigns_details.csv', 'w', newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(campaigns_details_csv_headers)
    for id, campaign in campaigns_store.items():
        # Caculcate avg dollar per rank raised
        if len(campaign.dollar_per_rank_raised_list) != 0:
            sum = 0
            for avg in campaign.dollar_per_rank_raised_list:
                sum += avg
            campaign.avg_dollar_per_rank_raised = \
                sum / len(campaign.dollar_per_rank_raised_list)
        writer.writerow(
            [
                campaign.project_id, campaign.titles_history, campaign.top_six_count,
                campaign.rank_amt_delta_list, campaign.avg_dollar_per_rank_raised,
                campaign.taglines_history, campaign.category, campaign.tags,
                campaign.currency, campaign.open_date, campaign.close_date,
                campaign.clickthrough_url, campaign.is_indemand, campaign.is_prelaunch,
                campaign.comments
            ]
        )