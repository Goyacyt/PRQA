from datasets import load_dataset
import model
from tqdm import tqdm
import util
import json
import sys
import pandas as pd
sys.path.append(".")
sys.path.append("./tools")

def write_json_to_file(json_object, json_file, mode='w', encoding='utf-8'):
    with open(json_file, mode, encoding=encoding) as outfile:
        json.dump(json_object, outfile, indent=4, sort_keys=True, ensure_ascii=False)

def load_RACE():
    datasets=load_dataset("race","high")["validation"]
    print(datasets[0])
    return datasets

def load_newsqa():
    datasets=load_dataset("newsqa",)["validation"]
    return datasets

def load_hotpot():
    datasets=load_dataset("hotpot_qa","distractor")["validation"]
    print(datasets[0])
    return datasets

def split_hotpot(data):
    context=data["context"]['sentences']
    paragraph=''
    for i in range(len(context)):
        for j in range(len(context[i])):
            paragraph=paragraph+context[i][j]

    question=data['question']
    answer=data['answer']
    return paragraph,question,answer

def hotpot_to_squad(squad_file):
    datasets=load_dataset("hotpot_qa","distractor")["train"]

    data = []
    for qad in tqdm(datasets):

        selected_text,question,groundtruth=split_hotpot(qad)
        answer=[{"text":groundtruth}]

        para = {'context': selected_text, 'qas': [{'question': question, 'answers': answer,'title':qad['supporting_facts']['title']}]}
        data.append({'paragraphs': [para]})

    squad = {'data': data}
    write_json_to_file(squad, squad_file)
    print ('Added', len(data))
    return data

def race_to_squad(squad_file):
    datasets=load_dataset("race","high")["validation"]
    data=[]
    for dataset in tqdm(datasets):
        question=dataset['question']+"choose between the following alphabet:"
        options=dataset['options']
        abcd=['A','B','C','D','E','F','G','H']
        for i in range(len(options)):
            question=question+abcd[i]+'.'+options[i]+'.'
        context=dataset['article']
        answernum=ord(dataset['answer'])-ord('A')
        if answernum>len(options):
            continue
        groundTruth=[options[answernum]]
        para = {'context': context, 'qas': [{'s_question':dataset['question'],'question': question, 'answers': groundTruth,'title':''}]}
        data.append({'paragraphs': [para]})

    squad = {'data': data}
    write_json_to_file(squad, squad_file)
    print ('Added', len(data))
    return data

def load_dataset_by_name(dataset_name):
    if dataset_name == 'squad':
        return load_dataset(dataset_name)['validation']
    elif dataset_name == 'wiki_trivia':
        path = "dataset/wikipedia_dev.json"
        return util.read_json(path)
    elif dataset_name == 'race':
        path = "dataset/race_dev.json"
        return util.read_json(path)
    elif dataset_name == 'hotpotqa':
        return load_hotpot()
    else:
        path = f"dataset/data_{dataset_name}_dev.tsv"
        return pd.read_csv(path, sep='\t', header=None, names=['q_c', 'a'], error_bad_lines=False)

def get_sample_data(dataset_name, dataset, i):
    if dataset_name == 'squad':
        data = dataset[i]
        context = data['context']
        question = data['question']
        groundTruth = [data['answers']]
    
    elif dataset_name in ['wiki_trivia', 'race']:
        Data = dataset["data"]
        data = Data[i]
        para = data["paragraphs"][0]
        context = para["context"].replace("\n", "")
        qas = para["qas"][0]
        
        if qas["answers"] == []:
            groundTruth = [""]
        else:
            groundTruth = [qas["answers"]]
        
        question = qas["question"]
        
        if dataset_name == 'race':
            s_question = qas.get('s_question', question)  # 如果没有's_question'，则使用原来的question
    
    elif dataset_name == 'hotpotqa':
        context, question, groundTruth = split_hotpot(dataset[i])
    
    else:
        question_context = dataset['q_c'][i]
        question = question_context.split("\\n")[0]
        context = question_context.split("\\n")[1]
        groundTruth = dataset['a'][i]

    return context, question, groundTruth


if __name__=='__main__':
    #hotpot_to_squad('dataset/hotpot_train.json')
    race_to_squad('dataset/race_dev.json')
    #load_RACE()