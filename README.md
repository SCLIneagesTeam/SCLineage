# SCLineage
SCLineage is an ifrastructure for collecting smart contract lineages

![Alt text](./images/allSteps.png?raw=true "allSteps")

### Data sources: Levraging Etherscan and Bigquery to get contracts.
### Lineages classification (Step 1 and Step 2)
#### Step1 Collect proxies contract and their callee contracts
#### Step2 is contract versionning
### An analysys of lineages:Step 3, Step 4 and Step 5), vulnearbilities ( in contracts lineages)



For each "step i" we have in <a href="dataset">dataset</a>, a folder containing the data obtained at this step and in <a href="src">src</a> a folder containing the source code executed at this step.
In case of need to remove a rule from step 2, just continue with the dataset generated before the rule execution in the parts following the rule execution.



