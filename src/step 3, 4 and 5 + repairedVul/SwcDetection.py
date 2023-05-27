#!/usr/bin/env bash
import csv
import collections
from collections import ChainMap
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from getpass import  getpass
import glob
from glob import glob
import json
from json import dumps, loads, JSONEncoder, JSONDecoder
import numpy as np
import os
import pandas as pd
from pandas import json_normalize
import pandas_profiling as pp
import subprocess
#import paramiko
import pathlib
from pathlib import Path
import re
import shutil
import time



######################################--------Functionality  --------#########################################
""""
This script
	- put in a same files the analyses result of the detection tools
	- if you want to add a new tool in the detection tools you have to update the line tools = ["conkas", "mythril","slither"]
	add a function specifik for the format of the tool's output by analogy to the function  "def readConkasRslt(fileName):"
	you have to go to  the file oracle "/reconciliation/SWCVulnerabilitiesOracle.csv"
	check if the tool's name is in the column and if all vulnerabilities in the tool are added
		
"""
####################################################################################################################################################################################################
################################################################################--------variables global  --------##################################################################################

## files
BASE_DIR = Path(__file__).resolve().parent.parent
oracleFile = (f"{BASE_DIR}/reconciliation/SWCVulnerabilitiesOracle.csv")
allRsltDay =  (f"{BASE_DIR}/historical_analysis_results.csv")
maintainFile = (f"{BASE_DIR}/reconciliation/maintenanceFile.csv")
matchAdrName = (f"{BASE_DIR}/dataset/root_files.csv")
proxiesFile = (f"{BASE_DIR}/dataset/part-5-opensource-at-least-two-upgrades.csv")
proxysContractsFilial = (f"{BASE_DIR}/dataset/predecessor-successor-all.txt")
## dir


#OutPut
currentTime = datetime.now().strftime('%d_%m_%Y-%H:%M:%S')
rsltScanJson = (f"{BASE_DIR}/results/Scan/{currentTime}.json")

#input
tools = ["conkas", "mythril","slither"]

#oracle for swc
dfOracl = pd.read_csv(oracleFile, delimiter=';')
dfOracl.fillna('', inplace=True)
totalRows=len(dfOracl.axes[0]) 
oraclMaJ = 0 

#OutPut.design
outExceptTool = ["contract", "SWCName"]
colsOut = outExceptTool + tools
dfOut = pd.DataFrame(columns= colsOut)
numVul = 0 #number of recordingAction
numDefctdFile = 0
#file of all results given by tools
recorByTool = {"dateRecording": currentTime, "results":[{"toolName":"","filiations":[{"proxy": "","contracts":[{"contractVersion":"","contratAddress": "","issue":[{"swcName": "","vulnerabilityName":"", "files":[{"fileName":"","contactsInFile":[{"contractName":"","functions":[{"function": "","defects":[{"lines": "","vulnerableCode":""}]}]}]}]}]}]}]}]}

dfProxies = pd.read_csv(proxiesFile, delimiter=',')
dfProxies.fillna('', inplace=True)
totalContract=len(dfProxies.axes[0]) 

############################################################################################################################################################################################
############################################################################################################################################################################################
def AppendToRecordV1(proxy, contract, contractVersion,  swc, tool, lines, vul, contractName, fileName, function, vulnerableCode, numV, recorByTool):
	if numV == 0:
		recorByTool["results"][0]["toolName"] = tool #L1
		recorByTool["results"][0]["filiations"][0]["proxy"] = proxy #L2
		recorByTool["results"][0]["filiations"][0]["contracts"][0]["contratAddress"]= contract #L3
		recorByTool["results"][0]["filiations"][0]["contracts"][0]["contractVersion"]= contractVersion #L3
		recorByTool["results"][0]["filiations"][0]["contracts"][0]["issue"][0]["swcName"] = swc #L4
		recorByTool["results"][0]["filiations"][0]["contracts"][0]["issue"][0]["vulnerabilityName"] = vul #L4

		recorByTool["results"][0]["filiations"][0]["contracts"][0]["issue"][0]["files"][0]["fileName"] = fileName #L5
		recorByTool["results"][0]["filiations"][0]["contracts"][0]["issue"][0]["files"][0]["contactsInFile"][0]["contractName"] = contractName  #L6
		recorByTool["results"][0]["filiations"][0]["contracts"][0]["issue"][0]["files"][0]["contactsInFile"][0]["functions"][0]["function"] = function  #L7
		recorByTool["results"][0]["filiations"][0]["contracts"][0]["issue"][0]["files"][0]["contactsInFile"][0]["functions"][0]["defects"][0]["lines"] = lines #L8
		recorByTool["results"][0]["filiations"][0]["contracts"][0]["issue"][0]["files"][0]["contactsInFile"][0]["functions"][0]["defects"][0]["vulnerableCode"] = vulnerableCode #L8

		numV = numV + 1
		return numV

	#num != 0
	m = 0
	newDefects = {"lines": lines,"vulnerableCode":vulnerableCode}
	recordL0 = recorByTool["results"]
	for i in range(len(recordL0)):
		if tool == recordL0[i]["toolName"]: #recorByTool["results"][i]["toolName"]
			recordL1 = recordL0[i]["filiations"] #recordL1 = recorByTool["results"][i]["filiations"] 
			#recorByTool["results"][i]["filiations"]
			for j in range(len(recordL1)):
				if proxy == recordL1[j]["proxy"]: #recorByTool["results"][i]["filiations"][j]["proxy"]
					recordL2 = recordL1[j]["contracts"]
					print("j= ", j)
					# recorByTool["results"][i]["filiations"][j]["contracts"]
					for k in range(len(recordL2)):	
						if contract == recordL2[k]["contratAddress"]:
							recordL3 = recordL2[k]["issue"] 	
							# recorByTool["results"][i]["filiations][j]["contracts"][k]["issue"] 
							for l in range(len(recordL3)):
								if vul == recordL3[l]["vulnerabilityName"]:
									recordL4 = recordL3[l]["files"]
									# recorByTool["results"][i]["filiations"][j]["contracts"][k]["issue"][l]["files"]
									for m in range(len(recordL4)):
										if fileName == recordL4[m]["fileName"]:
											recordL5 = recordL4[m]["contactsInFile"]
											# recorByTool["results"][i]["filiations"][j]["contracts"][k]["issue"][l]["files"][m]["contactsInFile"]
											for n in range(len(recordL5)):
												if contractName == recordL5[n]["contractName"]:
													recordL6 = recordL5[n]["functions"]
													# recorByTool["results"][i]["filiations"][j]["contracts"][k]["issue"][l]["files"][m]["contactsInFile"][n]["functions"]
													for o in range(len(recordL6)):
														if function == recordL6[o]["function"]:
															recordL7 = recordL6[o]["defects"]
															# recorByTool["results"][i]["filiations"][j]["contracts"][k]["issue"][l]["files"][m]["contactsInFile"][n]["functions"][o]["defects"]
															for q in range(len(recordL7)):
																if recordL7[q]["lines"] == lines and recordL7[q]["vulnerableCode"] == vulnerableCode:
																	 return numVul # 0 #, numvul #already recorded
															## new defects
															recorByTool["results"][i]["filiations"][j]["contracts"][k]["issue"][l]["files"][m]["contactsInFile"][n]["functions"][o]["defects"].append(newDefects)
															numV = numV + 1
															return numV
													## new functions
													toAddList = {"function": function,"defects":[newDefects]}
													recorByTool["results"][i]["filiations"][j]["contracts"][k]["issue"][l]["files"][m]["contactsInFile"][n]["functions"].append(toAddList)
													numV = numV + 1
													return numV
											## new contractInFile
											toAddList = {"contractName":contractName, "functions":[{"function": function,"defects":[newDefects]}]}
											recorByTool["results"][i]["filiations"][j]["contracts"][k]["issue"][l]["files"][m]["contactsInFile"].append(toAddList)
											numV = numV + 1
											return numV
									## new file
									toAddList = {"fileName":fileName,"contactsInFile":[{"contractName":contractName, "functions":[{"function": function,"defects":[newDefects]}]}]}
									recorByTool["results"][i]["filiations"][j]["contracts"][k]["issue"][l]["files"].append(toAddList)
									numV = numV + 1
									return numV

									#"files":[{"fileName":fileName,"contactsInFile":[{"contractName":contractName, "functions":[{"function": function,"defects":[newDefects]}]}]}]
							## new issue ie new vul
							toAddList = {"swcName": swc, "vulnerabilityName": vul, "files":[{"fileName":fileName,"contactsInFile":[{"contractName":contractName, "functions":[{"function": function,"defects":[newDefects]}]}]}]}
							recorByTool["results"][i]["filiations"][j]["contracts"][k]["issue"].append(toAddList)
							numV = numV + 1
							return numV 
					# new contracts ie new contract
					toAddList = {"contractVersion": contractVersion,"contratAddress": contract,"issue":[{"swcName": swc,"vulnerabilityName": vul, "files":[{"fileName":fileName,"contactsInFile":[{"contractName":contractName, "functions":[{"function": function,"defects":[newDefects]}]}]}] }]}
					recorByTool["results"][i]["filiations"][j]["contracts"].append(toAddList)
					numV = numV + 1
					return numV
			# new filliation ie new proxy
			toAddList = {"proxy": proxy, "contracts": [{"contractVersion": contractVersion,"contratAddress": contract,"issue":[{"swcName": swc,"vulnerabilityName": vul, "files":[{"fileName":fileName,"contactsInFile":[{"contractName":contractName, "functions":[{"function": function,"defects":[newDefects]}]}]}]}]}]}
			recorByTool["results"][i]["filiations"].append(toAddList)
			numV = numV + 1
			return numV
	# new result ie new tool
	toAddList= {"toolName": tool, "filiations": [{"proxy": proxy, "contracts": [{"contractVersion": contractVersion,"contratAddress": contract,"issue":[{"swcName": swc,"vulnerabilityName": vul, "files":[{"fileName":fileName,"contactsInFile":[{"contractName":contractName, "functions":[{"function": function,"defects":[newDefects]}]}]}]}]}]}]}
	recorByTool["results"].append(toAddList)
	numV = numV + 1
	return numV
										
######
### Now we search for each tool its results
######
######################################--------Function for each tool  --------#########################################
#####
### add all proxies and their contracts in the files 
def preparFilliation(proxy,contract):
	print("we search version of (proxy,contract) == (",proxy," , ", contract,")")
	with open (proxysContractsFilial, 'r') as f:
		for line in f:
			proxi = line.split(":")[0]	
			if proxy == proxi:
				contracts = line.split(":")[1].split("->") 		
				for contractVersion in range(len(contracts)):			
					if contracts[contractVersion].strip() == contract:
						print("match with contractVersion = ", contractVersion)
						return contractVersion
		return -1
#####
def readConkasRslt(fileName):
	vul = ""
	contract = getFileName(fileName)   #C1
	proxy = SearchProxy(contract)
	contractVersion = preparFilliation(proxy,contract)
	numV = numVul
	lastAnalisingLine = ""
	contractName = ""
	function = ""
	
	with open(fileName, "r") as f:
		for line in f:
			if "Analysing" in line:
				lastAnalisingLine = line
			if "Vulnerability:" in line:
				recup = line.split(':')
				vul = recup[1].split('.')[0]
				lines = recup[-1].split('.')[0].strip() 
				swc = vulToSwcName(vul, "conkas")
				detailsAna = lastAnalisingLine.split(":")
				nameFile = detailsAna[0].split("Analysing")[1].strip()
				try:
					contractName = detailsAna[1].split("...")[0].strip()
				except:
					pass
				try:
					function = line.split("in function:")[1].split(".")[0]
					
				except:
					pass
				numV =  AppendToRecordV1(proxy, contract, contractVersion, swc, "conkas", lines, vul, contractName, nameFile, function, "", numV, recorByTool)
	
			contractName = ""
			function = ""
		
	return numV
    
#############################################

def readMythrilRslt(fileName):
	numV = numVul
	findFile = 0
	contract = getFileName(fileName)
	proxy = SearchProxy(contract)
	contractVersion = preparFilliation(proxy,contract)
#
	nameContract =""
	with open(matchAdrName, 'r') as fRoot:
		for line in fRoot:
			if contract == line.split(",")[0]:
				nameContract = line.split(",")[1].split("\n")[0]
				fRoot.close()
				break;
	print("the contract name = ", nameContract)
	###
	error = 0
	jsonStart = 0
	anyException = 0

	with open(fileName,"r") as f:
		print("in file: ",fileName)
		try: 
			data1 = json.load(f)
		except:
			error = 1
			print("we have exception with current file")
			# fix it

		lineOri = f.read()
		print("lineOri = == ", lineOri, "finText")
		f.close()

	with open(fileName, 'r') as f2:
		try:
			data = json.load(f2)
		except:
			dstPath = f"{BASE_DIR}/results/mythril/invalidJson/{contract}.json"
			shutil.move(fileName, dstPath)
			return 0

		if not data["success"]:
			dstPath = f"{BASE_DIR}/results/mythril/fileErrors/{contract}.json"
			shutil.move(fileName, dstPath)
			return 0

		issues = data['issues']
		if issues == []:
			dstPath = f"{BASE_DIR}/results/mythril/safe/{contract}.json"
			shutil.move(fileName, dstPath)
			return 0
		## now we treat vulnerable files
		anyException = 1
		vulnerableCode = ""
		contractName  =""	
		# lets check issue one by one
		for issueItem in issues:
			swcId, vul, posiLine, filename, fct = issueItem["swc-id"], issueItem["title"],issueItem["lineno"], issueItem["filename"], issueItem["function"]
			lineEnd = posiLine
			noLine = str(posiLine)

			try:
				vulnerableCode = issueItem["code"]
				if vulnerableCode.strip != "":
					lineEnd = lineEnd + len(vulnerableCode.split("\n")) - 1
					noLine = noLine + "-" + str(lineEnd)
			except:
				pass
			try: 
				contractName = issueItem["contract"]
			except:
				pass
		
			#we record the iussue in toRecord 
			swcName = ""
			for iterLiigne in range(totalRows): # We search in Oracle the matched SWC with the current tool,vul
				if str(dfOracl["SWCId"][iterLiigne]) == swcId or vul.lower() in dfOracl["mythril"][iterLiigne].lower() :
					swcName = dfOracl["SWCName"][iterLiigne].strip()
					if  dfOracl["mythril"][iterLiigne].strip() == "":
						## we update our oracle file 
						dfOracl["mythril"][iterLiigne] = vul
						oraclMaJ = 1
					break;
			if swcName == "":
				add = addMaintainOracleLine ("mythril", vul)
			##
			numV =  AppendToRecordV1(proxy, contract,contractVersion, swcName, "mythril", noLine, vul, contractName, filename, fct, vulnerableCode, numV, recorByTool)
	
		return numV
			


##################################################
def readSlitherRslt(fileName):
	#  #results.detectors.elements 
	#results.detectors.first_markdown_element = "fileName.sol#LineStartBlock-LineSEndBlock"
	##results.detectors.markdown = "something [nameContract.nameBlockOr SignatureACheck]." 

	print("in file: ",fileName)

	numV = numVul
	contract = getFileName(fileName)
	proxy = SearchProxy(contract)
	contractVersion = preparFilliation(proxy,contract)
	
	
	with open(fileName, 'r') as f: #results.detectors.check is the vulnerability
		try:	
			rows = json.load(f)
			r = rows["results"]
			rr = r ["detectors"] #results.detector
		
			for i in range(len(rr)):
				print("\n \n \n i =", i)
				rrr = rr[i]
				vul = rrr["check"]
				print("check =", vul )# vulnerability
				vulcode1 = ""				
				elements = rrr["elements"]
				kj = 0
				issuesInElement =  []
				for j in range(len(elements)):
					kj = kj +1
					vulcode1 = ""
					function = ""
					contractName = ""
					# we search all node
					arg = elements[j]
					linesV= arg["source_mapping"]["lines"]
					vulcode1 = arg["name"]	
					fileName = 	arg["source_mapping"]["filename_relative"]
					if arg["type"] == "function":
						arg = arg["type_specific_fields"]
						function = arg["signature"]
						arg = arg["parent"]
					else:
						print("the type is =", arg["type"])
						if arg["type"] != "contract" and arg["type"] != "pragma":
							if arg["type_specific_fields"]["parent"]["type"] == "function":
								arg = arg["type_specific_fields"]["parent"]["type_specific_fields"]
								function = arg["signature"]
								arg = arg["parent"]
						
					if arg["type"] == "contract":
						contractName= arg["name"]
					try:
						if  arg["type_specific_fields"]["parent"]["type"] == "contract":
							contractName= arg["name"]
					except:
						pass
					print("issues ", kj)
					print("contractName == ", contractName)
					print("function == ", function)
					print("vulcode1 ==", vulcode1)
					print("lines ==", linesV)
					print("fileName ==", fileName)
				
					newListissu =  {"contractName": contractName, "function":function, "vulnerability": vulcode1, "fileName": fileName, "lineStart":linesV[0],"lineEnd":linesV[-1]}
					issuesInElement.append(newListissu)
				# delete element parents from issues
				for numIss in range(len(issuesInElement)-1):
					if  numIss < len(issuesInElement) -1:
						debut = numIss + 1
					else:
					 	debut = numIss 

					if issuesInElement[numIss] != {}:
						for parc in range(debut, len(issuesInElement)):
							if  issuesInElement[parc]!= {} and issuesInElement[numIss]["contractName"] == issuesInElement[parc]["contractName"] and (issuesInElement[numIss]["function"] == issuesInElement[parc]["function"] or issuesInElement[numIss]["function"] == "" or issuesInElement[parc]["function"]== ""):
								if issuesInElement[numIss]["lineStart"] <= issuesInElement[parc]["lineStart"]:
									if issuesInElement[numIss]["lineEnd"] >= issuesInElement[parc]["lineEnd"]:
										issuesInElement[numIss] = {}
										break;

								else:
									if issuesInElement[parc]["lineEnd"] >= issuesInElement[numIss]["lineEnd"]:
										issuesInElement[parc] = {}
									
				print("\n #################################################")
				print(" issue: ")
				for numIss in range(0, len(issuesInElement)):
					if (issuesInElement[numIss] !=  {}):
						print("issue = ", issuesInElement[numIss])
						noLine = str(issuesInElement[numIss]["lineStart"]) + "-" + str(issuesInElement[numIss]["lineEnd"])
						# we record now the vul in our result
						swcName = vulToSwcName(vul, "slither")
						numV =  AppendToRecordV1(proxy, contract, contractVersion, swcName, "slither", noLine, vul, issuesInElement[numIss]["contractName"], issuesInElement[numIss]["fileName"], issuesInElement[numIss]["function"], issuesInElement[numIss]["vulnerability"], numV, recorByTool)
			
			
		except:
			print("except in file ", fileName)
			return 0
	return 1
##############################################################################################################

######################################--------Other functions  --------#########################################
##
def getFileName(directory):
	pathname, extension = os.path.splitext(directory)
	filename = pathname.split('/')[-1]
	return filename
###

def addMaintainOracleLine (tool, vul):	
	path = Path(maintainFile)
	colsMaintain = ["tool", "vulnerability"]
	dfMaintain =  pd.DataFrame(columns= colsMaintain)
	
	try:
		dfMaintain = pd.read_csv(maintainFile)
		dfMaintain.fillna('', inplace=True)

	except:
		pass

	
	totalRowsM=len(dfMaintain.axes[0])
	print("the maintain file have  = ", totalRowsM, "lines") 
	if totalRowsM > 0:
		#we serach if (tool; vul) exist yet in the file
		print("the maintain file exist yet")
	
		for i in range(totalRowsM):
			if dfMaintain["tool"][i].lower() == tool and dfMaintain["vulnerability"][i].lower() == vul.lower():
				print("dfMaintain['tool'][i] = ", dfMaintain['tool'][i], "dfMaintain['vulnerability'][i]  = ", dfMaintain['vulnerability'][i])
				return 0

	with open(maintainFile, 'a', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=colsMaintain)
		if totalRowsM == 0:
			writer.writeheader()
		
		writer.writerow({"tool": tool, "vulnerability":vul})
		f.close()
		print("added", tool," ",vul)
	return 1

###
def vulToSwcName(vul, tool):
	tool = tool.replace(' ',"")
	itMatch = 0 # Have we this peer (tool, vul) in our oracle? Yes/no 1/0?
	for iterLiigne in range(totalRows): # We search in Oracle the matched SWC with the current tool,vul
		vul = vul.strip()
		dfOracl.loc[iterLiigne, tool] = dfOracl[tool][iterLiigne].strip()
		# in the matched column: search in each line
		if(vul.lower() in dfOracl[tool][iterLiigne].lower()):
				# the cells which include the detected vulnerability
			currentSWC = dfOracl["SWCName"][iterLiigne]
			if currentSWC.strip() != "":
        		#Search if we have yet an instance (contract, SWC) in dfOut
        		#weFindInstance = 0 #New SWC or existing? 1/0
				dfOutRows=len(dfOut.axes[0])
				return currentSWC   
	print(" swc not found for ", vul,",", tool)
	add = addMaintainOracleLine (tool, vul)
	currentSWC = ""
	return currentSWC

########
def swcIdToSwc(swcId):
	SWCId = SWCId.strip()
	for iterLiigne in range(totalRows): # We search in Oracle the matched SWC with the cswcID
		dfOracl.loc[iterLiigne, "SWCId"] = dfOracl["SWCId"][iterLiigne].strip()
		if dfOracl.loc[iterLiigne, "SWCId"] == SWCId :
			return dfOracl.loc[iterLiigne, "SWCName"]

######
###

def errorInFIleSacnned(rsltFIle, indiceError):
	file = open(rsltFIle,'r')
	return (indiceError in file.read())

########

 
def SearchProxy(contractAd):
	for iterLiigne in range(totalContract):
		if dfProxies["contract_address"][iterLiigne] == contractAd:
			return dfProxies["proxy"][iterLiigne]
		
	return ""

        
##############################################################################################################

########################################--------  Folders  --------###########################################


numCt = 0
for tool in tools:
	print("current tool = ", tool,"\n")

	
	if tool == "conkas":
		print("tool = ", tool)

		for conkFile in glob(f"{BASE_DIR}/results/{tool}/*.txt"):
			contract = getFileName(conkFile)
			print("contract: ",conkFile)	
			numVul = readConkasRslt(conkFile)	
	## 
	if tool == "mythril":
		for myt in glob(f"{BASE_DIR}/results/{tool}/*.json"):
			contract = getFileName(myt)
			numVul = readMythrilRslt(myt)
			numCt = numCt +1

	if tool == "slither":
		for slFile in glob(f"{BASE_DIR}/results/{tool}/*.json"):
			contract = getFileName(slFile)
			if errorInFIleSacnned(slFile, "Traceback"):
				dstPath = f"{BASE_DIR}/results/slither/fileErrors/{contract}.txt"
				shutil.move(slFile, dstPath)
				#numDefctdFile = numDefctdFile + 1
				continue;
			readSlitherRslt(slFile)
			
		

f = open(rsltScanJson, "w")
json.dump(recorByTool, f)
f.close()
if oraclMaJ == 1:
	dfOracl.to(oracleFile)

print("we make ", numVul, "records")
print("now you can run fillVulCode.py to fill empty vulcode with lines no null")


#######################################################################################
#### test criteria										  #
##  		         	  
## 																	                  #
##############			