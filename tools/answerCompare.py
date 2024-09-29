from sentence_transformers import SentenceTransformer
import torch
from torch import nn
import json
import sys
sys.path.append(".")
sys.path.append("./tools")

model_path='whaleloops/phrase-bert'
phrase_sim_model=SentenceTransformer(model_path)

cos_sim=nn.CosineSimilarity(dim=0)

def answerMatch(answer,modAnswer,count,threshold=0.76):
    # print(answer)
    # print(modAnswer)
    if "no" in answer and "no" in modAnswer:
        # print("no")
        return 1
    elif "yes" in answer and "yes" in modAnswer:
        # print("yes")
        return 1
    # print("=============")
    answer=answer.strip().lower()
    modAnswer=modAnswer.strip().lower()
    #simple == match:
    if (answer==modAnswer) or (answer in modAnswer) or (modAnswer in answer):
        return 1

    res=phrase_sim_model.encode([answer,modAnswer])
    [e1,e2]=res
    sim=(float)(cos_sim(torch.tensor(e1),torch.tensor(e2)))
    info_dict={
        'test case number':count,
    }
    info_dict['answer']=answer
    info_dict['modAnswer']=modAnswer
    info_dict['similarity']=sim
    #info_dict['test case number']=count
    #json.dump(info_dict,logfile)
    #print(f"{answer} | {modAnswer} | {sim}",file=logfile)
    #print(f"similarity of {answer} and {modAnswer} : {sim}")
    if sim>threshold:
        return 1
    else:
        return 0

if __name__=="__main__":
    filepath = "res-narrative/gpt3.5/narrative_MR2_relative_similarity_threshold_76_buglogfile20240414.json"
    bugpath = "res-narrative/gpt3.5/bug_narrative_MR2_relative_similarity_threshold_76_buglogfile20240414.json"
    bug_f = open(bugpath, 'w', encoding='utf-8')
    with open(filepath,'r',encoding='utf-8') as file:
        datas=json.load(file)
    res=[]
    for _ in range(len(datas)):
        data=datas[_]
        answer = data['answer']
        modAnswer = data['modAnswer']
        if not answerMatch(answer, modAnswer, _):
            res.append(data)
    json.dump(res,bug_f)