import difflib
import csv
#import collections
#from collections import ChainMap
#from datetime import datetime
#from dotenv import load_dotenv
#load_dotenv()
#from fuzzywuzzy import fuzz #pip install fuzzywuzzy
#from fuzzywuzzy import process #pip install fuzzywuzzy
#from getpass import  getpass
import glob
from glob import glob
import json
from json import dumps, loads, JSONEncoder, JSONDecoder
from Levenshtein import distance, ratio #pip install levenshtein
import linecache as lc
import numpy as np
import os
from os import walk
#import pandas as pd
#from pandas import json_normalize
#import pandas_profiling as pp
import subprocess
#import paramiko
import pathlib
from pathlib import Path
import re
#import shutil

############ prerequisite##########
    # pip install levenshtein
    # pip3 install solidity_parser
###################################

######### Algo ########
# (1)Search pairs 'pred/suc) ---> outFolder = contractPred-contractSucc
# (2)Search the m=atched subdiretories and add tthem  to the folders
#########




## 
BASE_DIR = Path(__file__).resolve().parent#.parent
predSuccFile = (f"{BASE_DIR}/dataset/predSuc.csv")
reportDiff = f"{BASE_DIR}/UseCaseOutput/reports/allSolDiff.csv"
vulReport = f"{BASE_DIR}/UseCaseOutput/reports/last.json"
renamedFiles = f"{BASE_DIR}/UseCaseOutput/reports/renamedFiles.csv"
diffAfterLevein = f"{BASE_DIR}/UseCaseOutput/reports/diffAfterLevein.csv"
rsltMainDir = f"{BASE_DIR}/UseCaseOutput/diff"
homeFolder = BASE_DIR = Path(BASE_DIR).resolve().parent
contractsStore= f"{homeFolder}/vinny/contractsDump"
rsltScanJson = (f"{BASE_DIR}/UseCaseOutput/reports/last.json")
proxysContractsFilial = (f"{BASE_DIR}/dataset/predecessor-successor-opensource.txt")
vulVersions = (f"{BASE_DIR}/UseCaseOutput/reports/last.csv")
repairedVersion =  (f"{BASE_DIR}/UseCaseOutput/reports/repair1toolsVul.csv")
#contractsStore = homeFolder
#changeReport = f"{rsltMainDir}/changed/path/staus"




def listFoldersInFolder(folder):
    print("folder == ",  folder)
    return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

###### algo: (1)Search pairs 'pred/suc) ---> outFolder = contractPred-contractSucC ######
def PredSucc ():
    ## The search part is already done done and it gives us the file : predSuccFile
    # create subdir
    filelist = glob.glob(os.path.join(folder, "*"))
    for f in filelist:
        os.remove(f)
    n = 0
    isTitle = 1
    with open (predSuccFile, 'r') as f:
        for line in f:
            currentPred = line.split(";")[1]
            currentSucc = line.split(";")[2]
            nameDir = str(currentPred).strip() + "-" + str(currentSucc).strip()  
            if isTitle == 1:
                isTitle = 0
                continue
            subDir = os.path.join(rsltMainDir, nameDir)
            if not os.path.exists(subDir):
                os.makedirs(subDir)
                n = n +1
                #print("nameDir = ", nameDir)

            # search  contracts project in contractDump 
    print("done ", n, "subdirectories created")
    


####
def searchContractFolder():
    listPredSuc = listFoldersInFolder(rsltMainDir) ## return all folder pred-succ
    listContracts = listFoldersInFolder(contractsStore) # return list folders of project contrac version
    os.chdir(contractsStore) # cd contractsStore 
    dirPred = ""
    dirSucc = ""
    dirPred
    status = ""
    diffPath = ""
    diffPath2record = ""
    report = ""
    data = []
    header = ["Upgrade", 'Path', 'Action', 'numFileSolidity', 'totalNumLines']
    data.append(header)
    numFiles = 0
    locFiles = 0
    for predSuc in  listPredSuc:
        dirPredFound = 0 
        dirSuccFound = 0
        for projectDir in listContracts:
            if dirPredFound == 0:
                if projectDir.strip().startswith(predSuc.split("-")[0].strip()):
                    dirPredFound = 1
                    dirPred = projectDir
            if dirSuccFound == 0:
                if projectDir.strip().startswith(predSuc.split("-")[1].strip()):
                    dirSuccFound = 1
                    dirSucc = projectDir
            if dirPredFound == 1 and dirSuccFound == 1:
                break;
        
        if dirPredFound == 1 and dirSuccFound == 1:
            #copute diff dirPred and dirSucc
            #cmd = "diff -qr " + str(contractsStore) +"/" + dirPred +" " + str(contractsStore) +"/" + dirSucc
            cmd = "diff -qr "   + dirPred + " " + dirSucc
            print("cmd = ", cmd)
            x = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
            diffOutput = x.stdout.read().decode('utf-8')
            print(diffOutput)
            # analyse diffOutput
            for line in diffOutput.splitlines():
                #print("line ==", line)
                if line.startswith("Only in"):
                    print("only in line cripted")
                    diffPathDir = line.split("Only in ")[1]
                    diffPath = diffPathDir.split(": ")[0] + "/" + diffPathDir.split(": ")[1]
                    print("line diff =", line)
                    #print("diffPath = ", diffPath)
                    # Add path in fileDiff with statut created or deleted depending it's only in psucc or pred
                    if predSuc.split("-")[0].strip() in diffPath:
                        status = "deleted"
                    if predSuc.split("-")[1].strip() in diffPath:
                        status = "added"
                    diffPath2record =  diffPath.split("/", 1)[1]
                    #cmd = "pygount --format=summary  --suffix=sol" + diffPath
                    cmd = "pygount  " + diffPath
                    x = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
                    numFiles = 0
                    locFiles = 0
                    reportChange = x.stdout.read().decode('utf-8')
                    print("report changed file = ", reportChange)
                    
                    for lineReport in reportChange.splitlines():
                        if "Solidity" in lineReport:
                            numFiles = numFiles + 1
                            locFiles = locFiles+ int(lineReport.split("\t")[0])
                            print("impacted solidity file num ", numFiles, " = ", lineReport)

                if line.startswith("Files") and line.endswith("differ"):
                    if ".sol" in line:
                        cmd = "diff -y --suppress-common-lines "+ line.split("Files ")[1].split(" and ")[0] + " " + line.split(" and ")[-1].split(" differ")[0] + "| wc -l"
                        x = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
                        locFiles = int(x.stdout.read().decode('utf-8'))
                        diffPath = line.split("Files ")[1].split(" and ")[0]
                        diffPath2record =  diffPath.split("/", 1)[1]
                        status = "edited"
                        numFiles = 1
                        #copy the file in /diff/pred-suc/.....
                        cmd = "diff -u  " + line.split("Files ")[1].split(" and ")[0] + " " + line.split(" and ")[-1].split(" differ")[0] 
                        x = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
                        filesDiff = x.stdout.read().decode('utf-8')
                        print("filesDiff is ", filesDiff)
                        pathF1 = str(rsltMainDir) + "/" + predSuc + "/" + diffPath2record
                        f1 = Path(pathF1)
                        f1.parent.mkdir(parents=True, exist_ok=True)
                        f1.write_text(filesDiff)
                   
                if numFiles > 0:
                    print("report: ", )
                    print("impacted path: ",diffPath2record, "; Action: ", status, "; numFilesSolidity: ", numFiles, "; impactedLocFilesSolidity:", locFiles)
                    ##to save in the report file
                    data.append([predSuc.strip(), diffPath2record, status, numFiles, locFiles])
                numFiles = 0
                locFiles = 0
        
    print("data = ", data)
    
    with open(reportDiff, 'w', encoding='UTF8', newline='') as f:
        #print("in the recording part")
        writer = csv.writer(f)
        writer.writerows(data)


def compareFiles(reportFile):
    #Take the report and test file which have similar name
    # the file is sorted
    #upgrade, Path, Action, numFileSolidity,totalNumLines
    # We assume for each file replaced by another one with a different name we have: 
        # the files has the same upgrade
        # the files has the same path.split(fileName)[0]
        #each replaced file has as Action deleted and it new version has as Action added
        # the files has similarName
    # browe lines report
    # for each line l if action 
        #search in all line l+1 : line with Version or Path different or last line
        # the line which have same versions such as distance(path1, path2) == 1 and action are differents and not equal edited
        # save in file of replaceFiles --> renamedFiles
        #upgrade, path, replaced, replacing, changedLines
    header = ["upgrade", "directories", "replaced", "replacing", "changedLines"]
    data = []
    data.append(header)
    numCurrentLine = 0
    browsedLine = ""
    lastCheckedLine= 0
    os.chdir(contractsStore)

    with open (reportFile, 'r') as f:
        totalLines = len(f.readlines())
        f.close
    with open (reportFile, 'r') as f:
        print("totalLines = ", totalLines)
        for line in f:
            numCurrentLine = numCurrentLine + 1
            print("num current line = ", numCurrentLine, "and numLastCheckedLine = ", lastCheckedLine)
            print("current line = ", line)
            if numCurrentLine < lastCheckedLine or numCurrentLine == 1:
                continue
            
            upgrade = line.split(",")[0]
            path = line.split(",")[1]
            action = line.split(",")[2]
            numFile = int(line.split(",")[3])
            print("upgrade = ", upgrade, "path = ", path, "action = ", action, "numFile = ", numFile)
            if numFile == 1 and action != "edited":
                print("possible renamed file")
                directories = path.rsplit("/", 1)[0]
                solFile = path.rsplit("/", 1)[-1]
                if totalLines > numCurrentLine + 1:
                    for numLine in range(numCurrentLine + 1, totalLines +1) :
                        browsedLine = lc.getline(reportFile, numLine)
                        print("num currentChecked line = ", numLine, "currentChecked line = ", browsedLine)
                        print(" current checked line = ", browsedLine)
                        browsedUpgrade = browsedLine.split(",")[0]
                        browsedNumFile = int(browsedLine.split(",")[3])
                        #browsedDirectories = browsedLine.split(",")[1].rsplit("/", 1)[0]
                        if browsedUpgrade.strip() != upgrade or browsedNumFile != 1:# or directories != browsedDirectories:
                            lastCheckedLine = numLine
                            break;
                        browsedPath = browsedLine.split(",")[1]
                        browsedDirectories = browsedPath.rsplit("/", 1)[0]
                        if directories != browsedDirectories:
                            lastCheckedLine = numLine
                            break;
                            
                        browsedAction = browsedLine.split(",")[2]
                        if browsedAction != "edited" and browsedAction != action and (distance(path, browsedPath) < 3):
                            print("we think that the files ", path, " and ", browsedPath, " match. Their action are : ",action, "and ", browsedAction)
                            browsedSolFile = browsedLine.split(",")[1].rsplit("/", 1)[-1]

                            cmd = "find . -type d -name " + upgrade.split("-")[0] + "-*"
                            print("cmdPred = ", cmd)
                            x = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
                            filePred = x.stdout.read().decode('utf-8').split("\n")[0] + "/" 
                            print("rsltPred = ", filePred)
                            
                            cmd = "find . -type d -name " + upgrade.split("-")[1].strip() + "-*"
                            print("cmdSucc = ", cmd)
                            x = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
                            fileSucc = x.stdout.read().decode('utf-8').split("\n")[0]  + "/"
                            print("rsltSucc = ", fileSucc)

                            if action == "deleted":
                                filePred = filePred + path
                                fileSucc = fileSucc + browsedPath
                            else:
                                filePred = filePred + browsedPath
                                fileSucc = fileSucc + path

                            cmd = "diff -y --suppress-common-lines  " + filePred + " " + fileSucc + " | wc -l"
                            print("cmd = ", cmd)
                            x = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
                            locDiff = int(x.stdout.read().decode('utf-8'))
                            data.append([upgrade, directories, solFile, browsedSolFile, locDiff])

                            #copy the file in /diff/pred-suc/.....
                            cmd = "diff -u  " + filePred  + " " + fileSucc
                            x = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
                            filesDiff = x.stdout.read().decode('utf-8')
                            #print("filesDiff is ", filesDiff)
                            diffPath2record = solFile.split(".sol")[0] + "-" + browsedSolFile
                            pathF1 = ""
                            if directories.strip() != "":
                                pathF1 = str(rsltMainDir) + "/" + upgrade + "/" +  directories + "/" + diffPath2record
                            else:
                                pathF1 = str(rsltMainDir) + "/" + upgrade + "/"  + diffPath2record
                            print("pathF1 = ", pathF1)
                            f1 = Path(pathF1)
                            f1.parent.mkdir(parents=True, exist_ok=True)
                            f1.write_text(filesDiff)
    print("all data are ", data)
    with open(renamedFiles, 'w', encoding='UTF8', newline='') as f:
        #print("in the recording part")
        writer = csv.writer(f)
        writer.writerows(data)

def getProxiesLastVersion(proxy):
    with open (proxysContractsFilial, 'r') as f:
        for line in f:
            if line.split(":")[0].strip() == proxy:
                return len(line.split(":")[1].split("->")) - 1
        return 0

def PatchedVul():
    #### code defined below
    #isPatch == if (Pred,U,T, L)  --> (Succ,U,T, L) such as U = []

    # patched in proxies lev
    header = ["Tool", "Proxy", "Version", "Address"]#, "File", "contractInFile", "VulnerabilityName"]
    #dfOut = pd.DataFrame(columns= header)
    #totalRowsM=len(dfOut.axes[0])
    data = []
    repaired = []
    data.append(header)
    repaired.append(["Tool", "Proxy", "Version"])

    with open(rsltScanJson, 'r' ) as f:
        recorByTool = json.load(f)
        allRslt = recorByTool["results"]
        for i in range(len(allRslt)):
            tool = recorByTool["results"][i]["toolName"]
            filliations = recorByTool["results"][i]["filiations"]
            for j in range(len(filliations)):
                proxy = filliations[j]["proxy"]
                contracts = filliations[j]["contracts"]
                numberVulVersion = len(contracts)
                for k  in range(numberVulVersion):
                    contract = contracts[k]
                    contractAdr = contract["contratAddress"]
                    version = contract["contractVersion"]
                    #issues = contract["issue"]

                    #recorByTool["results"][0]["filiations"][0]["contracts"][0]["issue"][0]["files"][0]["contactsInFile"][0]["functions"][0]["defects"][0]["vulnerableCode"] = vulnerableCode #L8
                    ### add data in file
                    data.append([tool, proxy, version, contractAdr])
                    with open(vulVersions, 'w', encoding='UTF8', newline='') as f1:
                        writer = csv.writer(f1)
                        writer.writerows(data)
                        f1.close
                    #### level files
                    issues = contract["issue"]
                    #for l in range(numberVulVersion):

        f.close

        ###  isPatch == if (Pred,U,T, L)  --> (Succ,U,T, Lp) such as U = [], Lp<L 
            ## case 1 we assume that Pred, succ are contracts, T is used T by a file and L is skiped
            # we have to search which versio  disappear in a tool detection results
        #for each [tool, proxy, version, contractAdr] search if we have [tool, proxy, version, Succ]
        with open (vulVersions, 'r') as f:
            alLines = f.readlines()
            f.close

        numLine = 1
        with open(vulVersions, 'r') as f:
            for line in f:
                if numLine == 1:
                    numLine = 2
                    continue
                print("does line ", line, "corrected?")
                proxy = line.split(",")[1]
                version = line.split(",")[2]
                ### search if we have [tool, proxy, version +1, Succ]
                proxyLastVersion = getProxiesLastVersion(proxy)
                isRepaired = 1
                numL = 1
                if proxyLastVersion > int(version.strip()):
                    for l in alLines:
                        if numL == 1:
                            numL = 2
                            continue
                        print("do lines ", line, " and ", l, " follow ? ",)
                        #print("int(version.strip()) + 1 ==", )
                        if l.split(",")[0] == line.split(",")[0] and l.split(",")[1] == proxy and int(l.split(",")[2].strip()) == int(version.strip()) + 1:
                            isRepaired = 0
                            print("they match, Not repaired ")
                    if isRepaired == 1:
                        print("Yes")
                        repaired.append([line.split(",")[0], proxy, int(version.strip()) + 1])
            
            with open(repairedVersion, 'w', encoding='UTF8', newline='') as f1:
                writer = csv.writer(f1)
                writer.writerows(repaired)
                f1.close
        
        #### case of contract level


def synthesDiff():
    ##### for each corrected contract search diffLines in files 
        ## (1) reportDiff to get edited, added, deleted in lne pred  ---- contract  ##Version,Path,Action,numFileSolidity,totalNumLines
        ### (2)and renamedFiles to check which deleted--added are in reality an edit (replace)

    ### reconcile the 2 files in diffAfterLevein  
    data = []
    header = ["Version", "directories", "Action", "oldFile", "newFile", "numFileSolidity" , "totalNumLines"]
    data.append(header)
    newLine = []
    firstLine = 1
    with open (renamedFiles, 'r') as f:
        replacedFiles = f.readlines()
        f.close
    with open(reportDiff, 'r') as f:
        for line in f:
            if firstLine == 1:
                firstLine = 0
                continue
            upgrade = line.split(",")[0]#.split("-")[1]
            path = line.split(",")[1]
            action = line.split(",")[2]
            numFileSolidity = line.split(",")[3]
            totalNumLines = line.split(",")[4]
            fileName =  path.rsplit("/", 1)[-1]

            ### diffAfterLevein
            directories = path.rsplit("/", 1)[0]
            if ".sol" in directories:
                directories = "./"
            print("path ==", path, " and directories ==", directories) 

            if action == "edited":
                newLine = [line.split(",")[0], directories, action, fileName, fileName, numFileSolidity, int(line.split(",")[4])]
                data.append(newLine)
                continue

            if int(numFileSolidity.strip()) == 1: 
                # i.e adde or deleted file
                #check if the file is in  renamedFiles
                    # deleted and in renamedFiles means: upgrade = upgrade ,directories = path.rsplit("/", 1)[0] ,replaced =  path.rsplit("/", 1)[-1] ,replacing = ?,changedLines
                    # added and in renamedFiles means: upgrade = upgrade ,directories = path.rsplit("/", 1)[0] ,replaced =  ? ,replacing = path.rsplit("/", 1)[-1],changedLines
                isReplaced = 0
                #if action == "deleted":
                for l in replacedFiles:
                    if l.split(",")[0] == upgrade and l.split(",")[1] == directories:
                        if action == "deleted":
                            if l.split(",")[2] == fileName:
                                isReplaced = 1
                                fileName1 = fileName
                                fileName2 = l.split(",")[3]
                                break;
                        if action == "added":
                            if l.split(",")[3] == fileName:
                                isReplaced = 1
                                fileName2 = fileName
                                fileName1 = l.split(",")[2]
                                break;
                if isReplaced == 1:
                    #check if line not in data
                    searchedLine = [upgrade, directories, "edited", fileName1, fileName2, "1", int(l.split(",")[4])]
                    if searchedLine not in data:
                        newLine = searchedLine
                        data.append(newLine)
                        #print(searchedLine, " not in ", data)
                    continue
                
                if action == "deleted":
                    fileName1 = fileName
                    fileName2 = ""
                else:
                    fileName2 = fileName
                    fileName1 = ""
                newLine = [upgrade, directories, action, fileName1, fileName2, "1", int(line.split(",")[4])]
                data.append(newLine)
                continue
                    
            
            # i.e. added or deleted directories
            if action == "deleted":
                fileName1 = "*"
                fileName2 = ""
            else:
                fileName2 = "*"
                fileName1 = ""
            newLine = [line.split(",")[0], path, action, fileName1, fileName2, numFileSolidity, int(line.split(",")[4])]
            data.append(newLine)

        with open(diffAfterLevein, 'w', encoding='UTF8', newline='') as f1:
            writer = csv.writer(f1)
            writer.writerows(data)
            f1.close

        

    def PatchedVulCaseVulLevel():
    #### code defined below
    #isPatch == if (Pred,U,T, L)  --> (Succ,U,T, L) such as U = []

    # patched in proxies lev
    #header = ["Tool", "Proxy", "Version", "Address"]#, "File", "contractInFile", "VulnerabilityName"]
    header = ["Tool", "Proxy", "Version", "Address", "File", "contractInFile", "VulnerabilityName"]
    #dfOut = pd.DataFrame(columns= header)
    #totalRowsM=len(dfOut.axes[0])
    data = []
    repaired = []
    data.append(header)
    repaired.append(["Tool", "Proxy", "Version", "Address", "File", "contractInFile", "VulnerabilityName"])

    with open(rsltScanJson, 'r' ) as f:
        recorByTool = json.load(f)
        allRslt = recorByTool["results"]
        for i in range(len(allRslt)):
            tool = recorByTool["results"][i]["toolName"]
            filliations = recorByTool["results"][i]["filiations"]
            for j in range(len(filliations)):
                proxy = filliations[j]["proxy"]
                contracts = filliations[j]["contracts"]
                numberVulVersion = len(contracts)
                for k  in range(numberVulVersion):
                    contract = contracts[k]
                    contractAdr = contract["contratAddress"]
                    version = contract["contractVersion"]
                    issues = contract["issue"]
                    for j in range(issues):
                        files = issues[files]
                        vulnerabilityName = issues = contract["vulnerabilityName"]

                    #recorByTool["results"][0]["filiations"][0]["contracts"][0]["issue"][0]["files"][0]["contactsInFile"][0]["functions"][0]["defects"][0]["vulnerableCode"] = vulnerableCode #L8
                    ### add data in file
                    data.append([tool, proxy, version, contractAdr])
                    with open(vulVersions, 'w', encoding='UTF8', newline='') as f1:
                        writer = csv.writer(f1)
                        writer.writerows(data)
                        f1.close
                    #### level files
                    issues = contract["issue"]
                    #for l in range(numberVulVersion):

        f.close

        ###  isPatch == if (Pred,U,T, L)  --> (Succ,U,T, Lp) such as U = [], Lp<L 
            ## case 1 we assume that Pred, succ are contracts, T is used T by a file and L is skiped
            # we have to search which versio  disappear in a tool detection results
        #for each [tool, proxy, version, contractAdr] search if we have [tool, proxy, version, Succ]
        with open (vulVersions, 'r') as f:
            alLines = f.readlines()
            f.close

        numLine = 1
        with open(vulVersions, 'r') as f:
            for line in f:
                if numLine == 1:
                    numLine = 2
                    continue
                print("does line ", line, "corrected?")
                proxy = line.split(",")[1]
                version = line.split(",")[2]
                ### search if we have [tool, proxy, version +1, Succ]
                proxyLastVersion = getProxiesLastVersion(proxy)
                isRepaired = 1
                numL = 1
                if proxyLastVersion > int(version.strip()):
                    for l in alLines:
                        if numL == 1:
                            numL = 2
                            continue
                        print("do lines ", line, " and ", l, " follow ? ",)
                        #print("int(version.strip()) + 1 ==", )
                        if l.split(",")[0] == line.split(",")[0] and l.split(",")[1] == proxy and int(l.split(",")[2].strip()) == int(version.strip()) + 1:
                            isRepaired = 0
                            print("they match, Not repaired ")
                    if isRepaired == 1:
                        print("Yes")
                        repaired.append([line.split(",")[0], proxy, int(version.strip()) + 1])
            
            with open(repairedVersion, 'w', encoding='UTF8', newline='') as f1:
                writer = csv.writer(f1)
                writer.writerows(repaired)
                f1.close
        
        #### case of contract level


                    

    ### patched vul 
        ## i.e No vul in Succ which wasn't in pred
        ## A vul disaaapear
    #recorByTool["results"][0]["filiations"][0]["contracts"][0]["issue"][0]["files"][0]["contactsInFile"][0]["functions"][0]["defects"][0]["vulnerableCode"]
    # check vulnerable version 
        # version not in last.json --> 0 vulnerable vulnerabilities = []
        # version in last.json --> vulnerabilites == recorByTool["results"][0]["filiations"][0]["contracts"][0]["issue"][0]["vulnerabilityName"]
    ### 
        ### for each tool we need
            ## unvulnerable version, new unvulnerable files, new unvulnerables contractInFiles
            ### version with no new vulnerabilities compare to preds and les vulnerabilites (a version can be ContractAddress, contractFile, contractInfile)
        
    


#def PatchedVul():
    #(C,U,T, L)  --> (Cp,U,T, L) 
    #Cp is patch if
        #(1) The contract Cp is not vulnerable to the vulnerabilities in U .
        # (2) Cp passes all tests in TF
        # (3) Cp does not break any test in TP
        # (4) There is no feasible execution path in Cp whose total gas consumption exceeds the bound L
    #CP quality depends on
        #diff (C,Cp ) and cost(C Cp )
    # algo check if patch
        # Cond1: lastVulVersion < sizeLineage (1), (2) and (3)
        # Cond2: minGasVersion = lastVulVersion + 1 (4)
    #algo cond1
        # cond1.1: if by contract we mean  contractName 
        # cond1.2: if by contract we mean fileName.sol
        # cond1.3: if by contract we mean a contratAddress or contractVersion
    
    # code
        # for each lineage 
        #cond1.3: if by contract we mean a contratAddress or contractVersion
            #(1) check if the proxy is in last.json
                # gett all contractVersion 
                # lastVersion = len(line.split(-->) )
                #if len all_contractVersion < lastVersion +1 then lastVersion - all-contractVersion +1 possible patch
                    #browse 0 to astVersion find missing in all_contractVersion and put it in possiblePatchVersion
        # cond1.2: if by contract we mean fileName.sol
            #Browse contractAddress recuperate fileList for pred via cmd find file in contract dir
            # recuperate fileList for succ 
            #select missing files 
            #if missing file edited in report we have probable patched
            # if missing file not edited but is in report and in rplaced: if it replacer is missing then probable patched
            
        # # cond1.1: if by contract we mean  contractName for each file in pred take its contractName
            # Browse contractAddress recuperate fileList in report with statu edited or repalced
            # to get contract we can use cmd "python3 -m solidity_parser parse pathToFile
            # if we have

    

    #Check if vulcode or vulline in last.json are changed in diff/
        #last.json= recorByTool = {"dateRecording": currentTime, "results":[{"toolName":"","filiations":[{"proxy": "","contracts":[{"contractVersion":"","contratAddress": "","issue":[{"swcName": "","vulnerabilityName":"", "files":[{"fileName":"","contactsInFile":[{"contractName":"","functions":[{"function": "","defects":[{"lines": "","vulnerableCode":""}]}]}]}]}]}]}]}]}
        #recorByTool["results"][i]["filiations"][j]["contracts"][k]["issue"][l]["files"][m]["contactsInFile"][n]["functions"][o]["defects"] --> {"lines": lines,"vulnerableCode":vulnerableCode}
    # for each contract
        #open rsltMainDir/
    #browse defects in recorByTool 
    #open rsltMainDir/contratAddress-*/ 

###### algo : (2)Search the m=atched subdiretories and add tthem  to the folders #####
#PredSucc () #to execute 1 time
#searchContractFolder() # run one time
#compareFiles(reportDiff)# run one time
#PatchedVul() # tobe continued
#synthesDiff()


