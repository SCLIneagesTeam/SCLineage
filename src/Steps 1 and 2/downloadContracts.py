
from etherscan.contracts import Contract
import json
import redis
import sys
import time
import os

## set your params
ETHERSCAN_API_KEY = ""
REDIS = redis.Redis(host="", port=, db=, password="")
PREFIX = ""
SUFFIX = ""
REDIS_POP = f"{PREFIX}:{SUFFIX}:pop"
REDIS_ALREADY_DONE = f"{PREFIX}:{SUFFIX}:done"
REDIS_FOUND = f"{PREFIX}:{SUFFIX}:found"


BASE_DIR = "/home/contractsDump/"

def retrieve_source_codes(address: str):
    if len(address) != 42:
        return None

    api = Contract(address=address, api_key=ETHERSCAN_API_KEY)
    info = api.get_sourcecode()[0]
    sourcecode = info['SourceCode']
    contract_name = info['ContractName']
    files = []
    try:
        contract_object = json.loads(sourcecode[1:-1])
        files = [(name, code['content']) for name, code in contract_object.get('sources', {}).items()]
        # the file at index 0 is the root
        root = files[0][0]
    except json.JSONDecodeError:
        lines = sourcecode.splitlines()
        indices = [i for i, line in enumerate(lines) if line.startswith("// Dependency file:") or line.startswith("// Root file:")]
        files = [(lines[start].split(":")[1].strip(), '\n'.join(lines[start+1:end])) for start, end in zip(indices, indices[1:] + [len(lines)])]
        if len(files) == 0:
            files = [(f"{contract_name}.sol", sourcecode)]
            root = contract_name
        # the last file should be the root file
        root = files[-1][0]
    return (root.replace(" ", "_").replace("\\", "/").replace(".sol", "")).split("/")[-1], contract_name, files

while True:
    pop = REDIS.spop(REDIS_POP)
    if pop is None:
        time.sleep(30)
        continue
    try:
        address = pop.decode("utf8")
        # Check if already done
        if REDIS.sismember(REDIS_ALREADY_DONE, address):
            continue
        root, name, sources = retrieve_source_codes(address)
        assert len(sources) > 0
        for filename, code in sources:

            filename = filename.replace(" ", "_").replace("\\", "/")
            # here we save the files
            directory = f"{BASE_DIR}/{address}-{name}/{'/'.join(filename.split('/')[:-1])}"
            if not os.path.exists(directory): 
                os.makedirs(directory)
            with open(f'{BASE_DIR}/{address}-{name}/{filename}', 'w') as f:
                f.write(code)
        REDIS.sadd(REDIS_ALREADY_DONE, address)
        REDIS.sadd(REDIS_FOUND, f"{address},{root}")
        print(f"{address},{root}")
    except Exception as e: 
        print(e)