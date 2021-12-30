# EMBARGOED TILL 31 MAY 2022

# Indiegogo Scraper and CSV generator

* Authoor - Camille Chin Rui Bin

Scraper for a very specific and niche project for ████████ ███████████ ██████  
Scrapes the public api every 10 minutes and saves the json. Converts the json into csv for further analysis  
  
Config files are left empty to leave out sensitive details  
Empty templates provided in place  
  
## Usage

scraper.py - Runs the basic scraper  
> Was not originally made to run on a server or as a service  
> Default interval is 600 seconds (10 minutes)  
> Not built with cron in mind

convert_to_csv.py - Converts the json files in dump to 3 csv files for analysis

```
usage: scraper.py [-h] [-r] [-at START_AT START_AT]

Scrape Indiegogo's community projects trending top 36

optional arguments:
  -h, --help            show this help message and exit
  -r, --run             run continously
  -at START_AT START_AT, --start-at START_AT START_AT
                        time to start at in the format YYYY-MM-DD HH:MM

PS C:\Users\████████\indiegogo-scraper>  python .\scraper.py -at 2021-12-30 22:07          
PID: 1234
start time: 2021-12-30 22:04:00

sleeping  0 days   9 seconds 2021-12-30 22:06:51 PID 1234
2021-12-30 22:07:54.42108
2021-12-30 2207
sleeping 581 seconds PID 1234 [^C]
Programme have stopped
```

## Azure infra set up

Specific to ████████ ███████████ ██████'s use case.  
  
In this case it sets up a very basic VM in Korea Central. ARM template provided  
  
No config management or fancy Ansible / provisioning stuff as its out of the scope of this project

### Az CLI in Powershell

```
Set-Variable RG NAME_OF_RG

az group create `
  --name $RG `
  --location "koreacentral"


az deployment group create `
  --name ScraperDeployment `
  --resource-group $RG `
  --template-file azure-template.json `
  --parameters azure-parameters.json
```

### Quick start on VM

```
# Set timezone
$ sudo timedatectl set-timezone Region/Timezone

# Run in tmux shell
$ tmux

# Mkdir dumps directory
$ mkdir dumps

$ python .\scraper.py -r 
```