import argparse
from datasets import load_dataset
from tools.answerCompare import *
import json
from tools.util import beauty, otherbeauty, parse_config
import sys

def analysis(input_file, config_dict):
    dataset=load_dataset('squad')['validation']
    
    res_all_file = open(input_file, 'r', encoding='utf-8')
    ismr3=0
    if int(config_dict["config"]["mr"])==3:
        ismr3=1
    
    match_threshold = float(config_dict["config"]["compare_threshold"])
    
    output_ana = input_file.replace(".json", "_ana.json")
    output_ana_f = open(output_ana,'a+',encoding='utf-8')
    logfilename = input_file.replace(".json", ".log")
    logfile=open(logfilename,'w+',encoding='utf-8')
    bugfilename = input_file.replace(".json", "_bug.json")
    bugfile=open(bugfilename,'w+',encoding='utf-8')
    
    resultList = json.load(res_all_file)
    """resultList=json.load(f)["data"]"""
    
    totalNum=0
    contextChangeNum = 0
    #违反MR
    bugNum=0
    bugRate=0
    #false positive
    fp=0
    fpRate=0
    contextNum=-1#the number of different context
    contextList=[]#different context

    questionNumPerContext=[]#the number of question asking each context
    questionPerContext=[]#the question list of each context

    bugPerContext=[]#the number of each context bugs
    bugRateofContext=[]#the rate

    lastContext=''

    #print("Add : ",len(resultList))

    lastCasenum=-1

    for i in range(len(resultList)):
        thisResult=resultList[i]
        caseNum=thisResult['test case number']
        if caseNum==lastCasenum:
            continue
        else:
            lastCasenum=caseNum
            totalNum+=1

    lastCasenum=-1

    json_bug=[]
    count = 0
    for i in range(len(resultList)):
        thisResult=resultList[i]
        caseNum=thisResult['test case number']
        context=thisResult['context']
        modContext=thisResult['modContext']
        question=thisResult['question'].strip().lower()
        groundTruth=thisResult['groundTruth']
        if config_dict["config"]["dataset"] == "squad":
            groundTruth = dataset[caseNum]["answers"]["text"][0]
        elif config_dict["config"]["dataset"] == "race":
            groundTruth = groundTruth[0][0]
        elif config_dict["config"]["dataset"] == "wiki_trivia":
            #print(config_dict["config"]["dataset"])
            if groundTruth[0] != "":
                groundTruth = groundTruth[0][0]["text"]
            else:
                groundTruth = ""
        groundTruth = groundTruth.rstrip('.').lower()
        answer=thisResult['answer'].rstrip('.').lower()
        modAnswer=thisResult['modAnswer'].rstrip('.').lower()
        dsn=thisResult['delete sentence number']
        dv=thisResult['distance value']
        if context != modContext:
            contextChangeNum +=1
        
        if context!=lastContext:
            if contextNum>=0:
                temp_dict={}
                temp_dict['End case number']=caseNum
                temp_dict['context number']=contextNum
                temp_dict['Bug rate']=0
                temp_dict['FP Rate']=0
                if questionNumPerContext[contextNum]!=0:
                    temp_dict['Bug rate']=bugPerContext[contextNum]/questionNumPerContext[contextNum]
                    bugRateofContext.append(bugPerContext[contextNum]/questionNumPerContext[contextNum])
            
            lastContext=context
            contextNum+=1
            questionPerContext.append([])
            questionNumPerContext.append(0)
            bugPerContext.append(0)
            contextList.append([caseNum,context])
        
        questionNumPerContext[contextNum]+=1
        questionPerContext[contextNum].append([caseNum,question,modContext])

        # print(ismr3)
        # MR2:
        if (not answerMatch(answer,modAnswer,caseNum, match_threshold))^ismr3:
            # print((not answerMatch(answer,modAnswer,caseNum, match_threshold))^ismr3)
            # print("bug")
            if caseNum==lastCasenum:
                continue
            else:
                lastCasenum=caseNum
                bug_dict={}
                bug_dict['test case number']=caseNum
                bug_dict['context']=context
                bug_dict['modContext']=modContext
                bug_dict['question']=question
                bug_dict['groundTruth']=groundTruth
                bug_dict['answer']=answer
                bug_dict['modAnswer']=modAnswer
                bug_dict['delete sentence number']=dsn
                bug_dict["distance value"]=dv
                
                json_bug.append(bug_dict)

                #discover a bug
                bugNum+=1
                bugPerContext[contextNum]+=1

                if config_dict["config"]["dataset"] == "squad":
                    if (groundTruth not in modContext)^ismr3:
                        fp+=1
                
    json.dump(json_bug,bugfile)
    print(contextChangeNum)
    bugRate=bugNum/contextChangeNum
    if bugNum != 0:
        fpRate = fp/bugNum
    else:
        fpRate = 0
    
    info_dict={}
    info_dict['Total Number']=totalNum
    info_dict['Context changed'] = contextChangeNum
    info_dict['Bug Number'] = bugNum
    info_dict['Bug Rate']=bugRate
    info_dict['False Positive Number']=fp
    info_dict['FP Rate']=fpRate

    info_dict['Bug Rate of Context']=bugRateofContext
    
    info_dict['Context list']=contextList
    info_dict['Question and ModContext']=questionPerContext
    json.dump(info_dict,output_ana_f)
    output_ana_f.close()
    logfile.close()
    bugfile.close()
    otherbeauty(output_ana)

if __name__=='__main__':
    if len(sys.argv) < 2:
        print("use like this : python answerAnalysis.py config.ini")

    config_file = sys.argv[1]
    config_dict = parse_config(config_file)
    input_file = config_dict["analysis"]["filepath"]
    
    analysis(input_file, config_dict)