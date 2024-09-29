import sys
import numpy as np
#from askchatGPT import *
from paraphrase import paraphrase
import random
import time
import re
from tools.util import split_context
import sys
sys.path.append(".")
sys.path.append("./tools")

lastContext=""
rewrite_context=[]


def MR1(context,proportion,lastContext,rewrite_context):#MR1重写暂不需要distance
    change=True
    context=split_context(context=context)

    if context!=lastContext:
        print("!=")
        #context!=lastContext 新的一个context
        lastContext=context
        rewrite_context=[]
        for sentence in context:
            paraphrases=paraphrase(sentence)
            change=True
            rewrite_context.append(paraphrases)
        
    part_number=[i for i in range(len(context))]
    part_number=random.sample(part_number,int(len(context)*proportion))
    if int(len(context)*proportion)==0:
        change=False
    
    res_context=[]

    for i in range(len(context)):
        if i in part_number:
            res_context.append(rewrite_context[i])
        else:
            res_context.append(context[i])

    #从数组转为字符串
    res_context="".join(res_context)
    return res_context,change,lastContext,rewrite_context

def take_second(elem):
    return elem[1]

def MR2(context,q_distance,a_distance,pattern,threshold,proportion=0.25,qproprotion=0.25,aproportion = 0.5):#默认参数

    q_distance.sort(key=take_first)
    a_distance.sort(key=take_first)
    distance=[]
    delsentence=[]

    length=len(q_distance)
    for i in range(len(q_distance)):
        distance.append([i,(q_distance[i][1]+a_distance[i][1])/2])

    distance.sort(key=take_second,reverse=True)

    q_distance.sort(key=take_second,reverse=True)
    a_distance.sort(key=take_second,reverse=True)

    context=split_context(context)
    delnum=[]
    delsentence=[]
    if pattern=="leastone":
        if len(q_distance)>1:
            del context[q_distance[len(q_distance)-1][0]]
    
    elif pattern=="threshold":
        print(q_distance)
        for i in range(len(q_distance)):
            if q_distance[i][1] < threshold:
                delsentence.append(q_distance[i][0])
                #del context[q_distance[i][0]]
        delsentence.sort(reverse=True)
        print(delsentence)
        for i in range(len(delsentence)):
            del context[delsentence[i]]

    elif pattern=="proportion":
        #删掉最不相关的一定比例的句子

        #按照相关度排序
        q_distance.sort(key=take_second,reverse=True)
        todeletenum=int(len(q_distance)*proportion)
        length=len(q_distance)

        #收集要被删除的句子序号
        for i in range(todeletenum):
            delnum.append(q_distance[length-1-i][0])
        
        #记录删除的句子
        delnum.sort()
        for i in range(len(delnum)):
            delsentence.append(context[delnum[i]])

        delnum.sort(reverse=True)
        for i in range(len(delnum)):
            del context[delnum[i]]
    
    elif pattern=="relative_similarity":
        #最多删除propertion比例的句子，但是每个被删除的句子的问题相关度不能在前q_proportion,问题相关度不能在前a_proportion
        q_thre=q_distance[int(length*qproprotion)][1]
        a_thre=a_distance[int(length*aproportion)][1]

        todeletenum=int(length*proportion)
        q_distance.sort(key=take_first)
        a_distance.sort(key=take_first)
        #print(f"qthre:{q_thre} athre:{a_thre}")
        #收集要被删除的句子序号
        for i in range(todeletenum):
            #print(f"num:{i} qdistance:{q_distance[distance[length-1-i][0]][1]} adistance:{a_distance[distance[length-1-i][0]][1]}")
            if (q_distance[distance[length-1-i][0]][1]<=q_thre) and (a_distance[distance[length-1-i][0]][1]<=a_thre):
                #print("delete")
                delnum.append(distance[length-1-i][0])
        
        #记录删除的句子
        delnum.sort()
        for i in range(len(delnum)):
            delsentence.append(context[delnum[i]])

        delnum.sort(reverse=True)
        for i in range(len(delnum)):
            #print(f"delete:{delnum[i]}")
            del context[delnum[i]]

    elif pattern=="withinSentence":
        pass
    else:
        print("MR type not realized or wrong spelled")
        sys.exit()
    context=''.join(context)
    #print(context)
    return context,delsentence, distance

def take_first(elem):
    return elem[0]

def MR3(context,q_distance,q_postion,a_distance,a_position,pattern,threshold=0.7,proportion1=0.4,proportion2=0.2):
    context=split_context(context)
    delnum=[]
    #先计算修正后的distance值
    q_distance.sort(key=take_first)
    a_distance.sort(key=take_first)
    distance=[]
    delsentence=[]
    length=len(q_distance)
    for i in range(len(q_distance)):
        distance.append([i,(q_distance[i][1]+a_distance[i][1])/2])
    
    #从大到小排序
    distance.sort(key=take_second,reverse=True)
    q_distance.sort(key=take_second,reverse=True)
    a_distance.sort(key=take_second,reverse=True)
    for i in range(int(length*proportion2)):
        delnum.append(q_distance[i][0])
        delnum.append(a_distance[i][0])

    #删去一定比例的
    if pattern=="proportion":
        if length<=1:
            pass
        else:
            for i in range(length):
                if i < (int(length*proportion1)):
                    delnum.append(distance[i][0])
                else:
                    if distance[i][1]>=threshold:
                        delnum.append(distance[i][0])
            
            delnum=set(delnum)
            delnum=list(delnum)
            delnum.sort()
            for i in range(len(delnum)):
                delsentence.append(context[delnum[i]])
            delnum.sort(reverse=True)
            for i in range(len(delnum)):
                del context[delnum[i]]
    
    elif pattern=="superposition_proportion":
        if length<=1:
            pass
        else:
            delnum = delnum + a_position #把和答案有重叠的删掉
            for i in range(length):
                #要留下至少一个句子，因为删除的顺序是从高到低的（相关度）
                if len(delnum) >= length - 1:
                    continue
                if i < (int(length*proportion1)):
                    delnum.append(distance[i][0])
                else:
                    if distance[i][1]>=threshold:
                        delnum.append(distance[i][0])
            
            delnum=set(delnum)
            delnum=list(delnum)
            delnum.sort()
            for i in range(len(delnum)):
                delsentence.append(context[delnum[i]])
            delnum.sort(reverse=True)
            for i in range(len(delnum)):
                del context[delnum[i]]
    
    context=''.join(context)
    return context,delsentence, distance

#squad,squad2:proportion 0.75
def MR4(context,q_distance, a_distance, proportion = 0.75):
    q_distance.sort(key=take_first)
    a_distance.sort(key=take_first)
    distance=[]

    for i in range(len(q_distance)):
        distance.append([i,(q_distance[i][1]+a_distance[i][1])/2])
    #调整相关度低于50%的句子的顺序
    #从低到高排序
    distance.sort(key=take_second)
    
    to_change_length = int(proportion*len(distance))
    context=split_context(context)
    to_change_index = []
    for i in range(to_change_length):
        to_change_index.append(distance[i][0])
    new_list_context = [context[i] for i in to_change_index]
    random.shuffle(new_list_context)
    for i,idx in enumerate(to_change_index):
        context[idx] = new_list_context[i]
    context = ''.join(context)
    return context, distance

import tools.distance as distance
import tools.model as model
if __name__=='__main__':
    context = "Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi\'s Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the \"golden anniversary\" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as \"Super Bowl L\"), so that the logo could prominently feature the Arabic numerals 50."
    question = "Which NFL team represented the AFC at Super Bowl 50?"
    q_distance=distance.semanticMatch(oriContext=context,question=question)
    q_postion=distance.superpositon(context,question)
    test_model="t5-small"
    test_answer=model.output_answer(None,question,context,test_model)
    a_distance=distance.semanticMatch(context,test_answer)
    a_position=distance.superpositon(context,question)
    MR2(context,q_distance,a_distance,"threshold",0.4)
    
    