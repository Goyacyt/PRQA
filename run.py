from datasets import load_dataset
from tools.distance import *
import tools.transformer as transformer
from model import output_answer,connect_to_openai
from tools.answerCompare import answerMatch
import urllib3
import json
import torch
from chatgpt.retest import *
import pandas as pd
import json
import answerAnalysis

import tools.util as util
import tools.dataLoad as dataLoad
import sys
sys.path.append("./tools")
sys.path.append(".")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

output_file = ""

def run(config_dict, date):

    # read config
    mr = config_dict["config"]["mr"]
    model = config_dict["config"]["model"]
    dataset_name = config_dict["config"]["dataset"]
    delete_pattern = config_dict["config"]["deletepattern"]
    proportion = config_dict["config"]["delete_proportion"]
    q_pro = config_dict["config"]["qproportion"]
    a_pro = config_dict["config"]["aproportion"]
    ap_pro = config_dict["config"]["a_pproportion"]
    threshold = config_dict["config"]["threshold"]
    sim_threshold = config_dict["config"]["sim_threshold"]
    rewrite_proportion = config_dict["config"]["rewriteproportion"]
    Start = config_dict["config"]["start"]
    End = config_dict["config"]["end"]

    # name output file
    if int(mr) == 1:
        output_file = "res-%s/res-MR1/%s_MR%s_rewrite%s%s" % (dataset_name, dataset_name, mr, rewrite_proportion, date)
    elif int(mr) == 2:
        if delete_pattern == "relative_similarity":
            output_file = "res-%s/res-MR2/totaldelete%s_qpro%s_apro%s_%s" % (dataset_name, int(float(proportion)*100), int(float(q_pro)*100), int(float(a_pro)*100), date)
        else:
            output_file = "res-%s/res-MR2/threshold%s_%s" % (dataset_name, threshold, date)
    elif int(mr) ==3 :
        output_file = "res-%s/res-MR3/threshold%s_totalpro%s_appro%s_%s" % (dataset_name,int(float(sim_threshold)*100), int(float(proportion)*100), int(float(ap_pro)*100), date)
    else :
        output_file = "res-%s/res-MR%s/%s_MR%s_%s_threshold%s_proportion%s%s" % (dataset_name, mr, dataset_name, mr, delete_pattern, threshold, proportion, date)
    log_file = output_file + ".log"
    output_file = output_file + ".json"
    print("output file:", output_file)
    
    result_file=open (output_file,'a+',encoding='utf-8')
    log_file=open(log_file,'a+',encoding='utf-8')
    result_file.write("[")
    
    dataset = dataLoad.load_dataset_by_name(dataset_name)
    
    all_result = []
    lastContext=[]
    rewrite_context=[]
    lasti=-1    #"adversarial_qa"使用
    print(f"total{End}\n")
    for i in range(int(Start),int(End)):
        _=i
        # read sample data
        context, question, groundTruth = dataLoad.get_sample_data(dataset_name, dataset, i)
        
        print("==============starting processing data:",_,"==================",file=log_file)
        
        modContext=''
        if dataset_name=='race':
            q_distance=semanticMatch(oriContext=context,question=s_question)
            q_postion=superpositon(context,s_question)
        else:
            q_distance=semanticMatch(oriContext=context,question=question)
            q_postion=superpositon(context,question)

        if int(mr)!=1:
            test_model="t5-small"
            test_answer=output_answer(None,question,context,test_model)
            a_distance=semanticMatch(context,test_answer)
            if dataset_name=='race':
                a_position=superpositon(context,test_answer)
            else:
                a_position=superpositon(context,test_answer)

        delsentence=[]

        model_name=model
        answer=output_answer(None,question=question,context=context,model_name=model_name)


        if int(mr)==1:
            #for i in range(5):
            modContext,change,lastContext,rewrite_context=transformer.MR1(context=context,proportion=float(rewrite_proportion),lastContext=lastContext,rewrite_context=rewrite_context)

            modAnswer=''
            
            if change:
                modAnswer=output_answer(None,question=question,context=modContext,model_name=model_name)
                print("Context is modified.",file=log_file)
            else:
                print("Context is not modified",file=log_file)
                modAnswer=answer

            distance = []
            print("Modified answer:",modAnswer)

        if int(mr)==2:
            modContext,delsentence,distance=transformer.MR2(context=context,q_distance=q_distance,a_distance=a_distance,pattern=delete_pattern,threshold=float(threshold),proportion=float(proportion), aproportion=float(a_pro), qproprotion=float(q_pro))
            print("delete sentence:", delsentence)
            print(modContext,file=log_file)

            if delsentence!=[]:
                modAnswer=output_answer(None,question=question,context=modContext,model_name=model_name)
            else:
                modAnswer=answer
            print("Modified answer:",modAnswer,file=log_file)

        if int(mr)==3:
            modContext,delsentence, distance=transformer.MR3(context=context,q_distance=q_distance,q_postion=q_postion,a_distance=a_distance,a_position=a_position,pattern=delete_pattern,threshold=float(sim_threshold))
            if delsentence!=[]:
                modAnswer=output_answer(None,question=question,context=modContext,model_name=model_name)
            else:
                modAnswer=answer

            print("Modified answer:",modAnswer,file=log_file)

        if _ != 0:
            result_file.write(',')
        res_info = util.record(_,context,modContext,question,answer,modAnswer,groundTruth,delsentence,distance)
        json.dump(res_info, result_file)
        print(f"case{_}\n")
        print("===================finish modified answer===============",file=log_file)
    result_file.write("]")
    result_file.close()
    return output_file

if __name__ == '__main__':
    config_file = sys.argv[1]
    model = sys.argv[2]
    # target = sys.argv[3]
    config_dict = util.parse_config(config_file)
    run(config_dict,"")
    # QAQA_testing(config_dict, "gpt-3.5")
    """if target == "test" :
        if model == "gpt-3.5" :
            LLM_testing(config_dict,model)
        else : 
            LLM4_testing(config_dict, model)
    elif target == "analysis" :
        LLM_analysis(config_dict,model)"""