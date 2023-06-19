# SCLineage
SCLineage is an ifrastructure for collecting smart contract lineages

![Alt text](./images/allSteps.png?raw=true "allSteps")

### Data sources: Levraging Etherscan and Bigquery to get contracts.
### Lineages classification (Step 1 and Step 2)
#### Step1 Collect proxies contract and their callee contracts
#### Step2 is contract versionning
### An analysis of lineages:Step 3, Step 4 and Step 5), vulnearbilities ( in contracts lineages) to identify vulnerabilities that disappear in certain versions.
#### Step3 analyses vulnerabilites in the lineage
#### Step4 is for vulnerabilities label reconciliation  
#### Step5 is for vulnerabilites which were in a version and disappear in its an upgraded versions
#### Refer to the paper for other possible cases of lineage analysis.
### In case of use of our infrastructure, please add below the link to your usersecase



For each "step i" we have in <a href="dataset">dataset</a>, a folder containing the data obtained at this step and in <a href="src">src</a> a folder containing the source code executed at this step.
In case of need to remove a rule from step 2, just continue with the dataset generated before the rule execution in the parts following the rule execution.



