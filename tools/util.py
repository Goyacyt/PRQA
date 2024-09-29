import json
import re
import stanza

import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize
import sys
sys.path.append(".")
sys.path.append("./tools")
import ast

from configparser import ConfigParser

def parse_config(config_file):
    # 创建配置解析器
    config = ConfigParser()
    
    # 读取配置文件
    config.read(config_file, encoding="utf-8")
    
    # 将配置文件中的参数存储在字典中
    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for option in config.options(section):
            config_dict[section][option] = config.get(section, option)
    
    return config_dict

def write_json_to_file(json_object, json_file, mode='w', encoding='utf-8'):
    with open(json_file, mode, encoding=encoding) as outfile:
        json.dump(json_object, outfile, indent=4, sort_keys=True, ensure_ascii=False)

def get_file_contents(filename, encoding='utf-8'):
    #print(filename)
    with open(filename, encoding=encoding) as f:
        content = f.read()
    return content

def read_json(filename, encoding='utf-8'):
    contents = get_file_contents(filename, encoding=encoding)
    return json.loads(contents)

def split_context(context):
    context=re.split(r"([.!?;+])", context)
    context.append("")
    context = ["".join(i) for i in zip(context[0::2],context[1::2])]
    context=context[:-1]
    return context

def constituency(sentence):
    nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency')
    doc = nlp(sentence)
    res=[]
    for sen in doc.sentences:
        res.append(sen.constituency)
    return res

def get_postag_real(sentence):
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger') 
    words = word_tokenize(sentence)

    # 对分词后的单词进行词性标注
    pos_tags = pos_tag(words)

    real_set=['NNP','CD','JJ','NN','VBD','VBN','NNS','VBG',]

    res=[]

    for word,pos in pos_tags:
        if pos in real_set:
            res.append(word)

    return res

def record(_,context,modContext,question,answer,modAnswer,groundTruth,delsentence,distance):
    info_dict={}
    info_dict['test case number']=_
    info_dict['context']=context
    info_dict['modContext']=modContext
    info_dict['question']=question
    info_dict['groundTruth']=groundTruth
    info_dict['answer']=answer
    info_dict['modAnswer']=modAnswer
    info_dict['delete sentence number']=delsentence
    info_dict["distance value"]=distance
    return info_dict

def beauty(file):
    f=open(file,'r',encoding='utf-8')
    result=f.read()
    result=result.split('}{')
    wf=open(file,'w',encoding='utf-8')
    for i in range(len(result)):
        if i==0:
            result[i]=result[i]+'}\n'
        elif i==len(result)-1:
            result[i]='{'+result[i]
        else:
            result[i]='{'+result[i]+'}\n'
        print(result[i],file=wf)
        #result[i]=ast.literal_eval(result[i])
    #print(result[0]['groundTruth'],result[0]['answer'])
    print(result,file=wf)

def otherbeauty(file):
    f=open(file,'r',encoding='utf-8')
    result=f.read()
    result=ast.literal_eval(result)
    wf=open(file,'w',encoding='utf-8')
    for key in result:
        print(key+':'+str(result[key]),file=wf)

def answerAnalysis(args):

    judge=0
    if (int)(args.mr)==3:
        judge=1

    whWord=[['what','which'],['what year','what month','what day','when','in what year','in which year'],['how many'],['how'],['who'],['where'],['why'],['if'],['other wh']]
    whWordNum=[0 for i in range(len(whWord))]
    whWordNumBug=[0 for i in range(len(whWord))]
    whWordNumBugRate=[0 for i in range(len(whWord))]

    thisresfile=args.filename[:-5]+'result_'+'threshold_'+str(args.simThreshold)[-2:]+'.json'
    f=open(args.filename,'r',encoding='utf-8')
    logfilename=thisresfile[:-5]+'_'+args.matchlogfile
    logfile=open(logfilename,'w+',encoding='utf-8')
    bugfilename=thisresfile[:-5]+'_'+args.buglogfile
    bugfile=open(bugfilename,'w+',encoding='utf-8')
    resultList=f.read()
    resultList=ast.literal_eval(resultList)
    simThreshold=(float)(args.simThreshold)
    totalNum=0
    bugNum=0#modified answer is different from original answer
    oEqualg=0
    mEqualg=0
    bugRate=0
    fp=0#the number of false positive
    fpRate=0
    contextNum=-1#the number of different context
    contextList=[]#different cotext
    questionNumPerContext=[]#the number of question asking each context
    questionPerContext=[]#the question list of each context
    bugPerContext=[]#the number of each context bugs
    fpPerContext=[]
    bugRateofContext=[]#the rate
    fpRateofContext=[]
    bugfpRateofContext=[]
    lastContext=''
    print(len(resultList))
    for i in range(len(resultList)):
        thisResult=resultList[i]
        caseNum=thisResult['test case number']
        context=thisResult['context']
        modContext=thisResult['modContext']
        question=thisResult['question'].strip().lower()
        groundTruth=thisResult['groundTruth']
        answer=thisResult['answer']
        modAnswer=thisResult['modAnswer']
        dsn=thisResult['delete sentence number']
        dv=thisResult['distance value']
        
        findwh=0
        whtype=-1
        for i in range(len(whWord)-1):
            wh=whWord[i]
            for j in range(len(wh)):
                w=wh[j]
                if question.startswith(w):
                    whWordNum[i]+=1
                    findwh=1
                    whtype=i
                    break
            if findwh:
                break

        if not findwh:
            #print(question)
            whWordNum[len(whWord)-1]+=1
            whtype=len(whWord)-1
        
        totalNum+=1
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
                if bugPerContext[contextNum]!=0:
                    temp_dict['FP Rate']=fpPerContext[contextNum]/bugPerContext[contextNum]
                    fpRateofContext.append(fpPerContext[contextNum]/bugPerContext[contextNum])
                bugfpRateofContext.append(temp_dict)
            
            lastContext=context
            contextNum+=1
            questionPerContext.append([])
            questionNumPerContext.append(0)
            bugPerContext.append(0)
            fpPerContext.append(0)
            contextList.append([caseNum,context])
        
        questionNumPerContext[contextNum]+=1
        questionPerContext[contextNum].append([caseNum,question,modContext])

        #MR2:
        if (not answerMatch(answer,modAnswer,caseNum))^judge:
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
            json.dump(bug_dict,bugfile)

            #discover a bug
            bugNum+=1
            bugPerContext[contextNum]+=1

            whWordNumBug[whtype]+=1

            """#为squad以外的其他数据集准备
            text=groundTruth
            if (text not in modContext)^judge:
                fp+=1
                fpPerContext[contextNum]+=1"""
            
            #为squad准备
            text=groundTruth['text']
            for t in range(len(text)):
                if (text[t] not in modContext)^judge:
                    fp+=1
                    fpPerContext[contextNum]+=1
                    break
            
            for t in range(len(text)):
                if answerMatch(text[t],modAnswer,caseNum):
                    mEqualg+=1
                    break

            for t in range(len(text)):
                if answerMatch(answer,text[t],caseNum):
                    oEqualg+=1
                    break
        
    bugRate=bugNum/totalNum
    fpRate=fp/bugNum
    for i in range(len(whWord)):
        if whWordNum[i]!=0:
            whWordNumBugRate[i]=whWordNumBug[i]/whWordNum[i]

    whBug=[]
    for i in range(len(whWord)):
        tem_dict={}
        tem_dict['wh-word']=whWord[i]
        tem_dict['total number']=whWordNum[i]
        tem_dict['bug number']=whWordNumBug[i]
        tem_dict['bug rate']=whWordNumBugRate[i]
        whBug.append(tem_dict)

    wf=open(thisresfile,'w+',encoding='utf-8')
    info_dict={}
    info_dict['Total Number']=totalNum
    info_dict['Bug Number']=bugNum
    info_dict['Bug Rate']=bugRate
    info_dict['False Positive Number']=fp
    info_dict['FP Rate']=fpRate
    info_dict['original answer=standard answer']=oEqualg
    info_dict['modified answer=standard answer']=mEqualg
    info_dict['original answer!=standard answer && modified answer!=standard answer']=bugNum-oEqualg-mEqualg

    whBugs=''
    for i in range(len(whBug)):
        whBugs=whBugs+str(whBug[i])+'\n'

    info_dict['bug rate related to the wh-word of a question']=whBugs

    info_dict['Bug Rate of Context']=bugRateofContext
    info_dict['FP Rate of Context']=fpRateofContext
    info_dict['Bug Rate and FP Rate of Context']=bugfpRateofContext
    info_dict['Context list']=contextList
    info_dict['Question and ModContext']=questionPerContext
    json.dump(info_dict,wf)
    wf.close()
    logfile.close()
    bugfile.close()
    beauty(logfilename)
    otherbeauty(thisresfile)

if __name__=='__main__':
    sentence="Ed Wood is a 1994 American biographical period comedy-drama film directed and produced by Tim Burton, and starring Johnny Depp as cult filmmaker Ed Wood."

    sentence="An acid is a molecule or ion capable of donating a hydron ( proton or hydrogen ion H+ ) , or , alternatively , capable of forming a covalent bond with an electron pair ( a Lewis acid ) .   The first category of acids is the proton donors or Br\u00f8nsted acids . In the special case of aqueous solutions , proton donors form the hydronium ion H3O+ and are known as Arrhenius acids ."

    """res=constituency(sentence)
    for i in range(len(res)):
        print(res[i])"""
    
    print(get_postag_real(sentence))