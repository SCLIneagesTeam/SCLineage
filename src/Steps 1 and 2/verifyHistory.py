import pandas as pd
from pathlib import Path
from datetime import datetime

######################################--------Functionality  --------#########################################
""""
This script
	- take as input  "/datasets/part-2-successor-predecessors-same-owner.csv"
    - give as output "datasets/part-3-correct-pattern-of-calling-delegatecalls.csv"
	- it classifies the contracts of the proxies from the least recent to the most recent
"""
####################################################################################################################################################################################################
###

BASE_DIR = Path(__file__).resolve().parent.parent
print("BASE_DIR =", str(BASE_DIR))
inputFile = (f'{BASE_DIR}/datasets/part-2-successor-predecessors-same-owner.csv')
with open(inputFile, 'r') as f:
    df = pd.read_csv(f, delimiter=",", parse_dates=['updated_on', 'first_delegate_call', 'last_delegate_call', 'created_on', 'first_transaction'])

    # let us loop through each of the proxies
    valid_proxies = []
    # this list will keep all our valid proxies for us
    for proxy in df["proxy"].unique():
        # we want to get them ordered, by date of update first
        sortedUpdates = df.loc[df['proxy'] == proxy].sort_values('updated_on')
        last_call = None
        valid = True
        contracts = []
        for id, update in sortedUpdates.iterrows():

            if last_call is None or last_call <= update['first_delegate_call']:
                # so if the first call happened after the last one of the previous version, then we are good. We assume that since it is a block thing, there should be some margin thus the permissive inequality
                last_call = update['last_delegate_call']
                contracts.append(update["contract"])
            else:
                valid = False
                break
        if valid:
            valid_proxies.append(proxy)
            print(f"{proxy}: {' -> '.join(contracts)}")
    result = df.loc[df['proxy'].isin(valid_proxies)].sort_values(['proxy', 'updated_on'])
    result.to_csv(BASE_DIR / 'datasets/part-3-correct-pattern-of-calling-delegatecalls.csv', index=False, date_format="%Y-%m-%d %H:%M:%S %Z")