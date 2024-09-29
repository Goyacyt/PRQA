def LLM_analysis(file_config, model):
    for section, options in file_config.items():
        print(f"[{section}]")
        # 遍历各个键值对
        for key, value in options.items():
            print(f"{key}={value}")
            origin_file = "res-%s/%s/%s" % (section, model, value)
            config_dict = {
                "config" : {
                    "mr" : 0,
                    "dataset" : "squad",
                    "compare_threshold" : 0.76
                }
            }
            print(key)
            if key == "mr1":
                config_dict["config"]["mr"] = 1
            elif key == "mr2":
                config_dict["config"]["mr"] = 2
            else:
                config_dict["config"]["mr"] = 3
            config_dict["config"]["dataset"] == section
            answerAnalysis.analysis(origin_file, config_dict)

def QAQA_testing(config_dict, model):
    for section,options in config_dict.items():
        print(f"[{section}]")
        # 遍历各个键值对
        for key, value in options.items():
            print(f"{key}={value}")
            client=connect_to_openai()
            value_list = value.split('/')
            bug_file = "%s/%s/%s/%s" % (value_list[0], value_list[1], model, value_list[3].replace("all.tsv", "bug.tsv"))
            bug_file_f = open(bug_file , 'a+', encoding='utf-8')
            origin_file = value
            datas = pd.read_csv(origin_file, sep='\t', header=None, names=['number', 'context', 'answer', 'type'],   error_bad_lines=False)
            result=[]
            dataset_name = value_list[1]
            if dataset_name=='squad':
                dataset=load_dataset(dataset_name)['validation']
            elif dataset_name=='wiki_trivia':
                path="dataset/wikipedia_dev.json"
                dataset=util.read_json(path)
            elif dataset_name=='race':
                path="dataset/race_dev.json"
                dataset=util.read_json(path)
            elif dataset_name=='hotpotqa':
                dataset=dataLoad.load_hotpot()
            else:
                path="dataset/data_"+dataset_name+"_dev.tsv"
                data = pd.read_csv(path, sep='\t', header=None, names=['q_c', 'a'],error_bad_lines=False)
            
                #得到每一个样例的data,context,question,groundtruth
                
            for _ in range(len(datas)):
                i = int(datas['number'][_])
                if dataset_name=='squad':
                    data=dataset[i]
                    context=data['context']
                    question=data['question']
                    groundTruth=[data['answers']]
                elif dataset_name=='wiki_trivia' or dataset_name=='race':
                    Data=dataset["data"]
                    data=Data[i]
                    para=data["paragraphs"][0]
                    context=para["context"]
                    context=context.replace("\n","")
                    qas=para["qas"][0]
                    if qas["answers"]==[]:
                        groundTruth=[""]
                    else:
                        groundTruth=[qas["answers"]]
                    #race:加上选项的question
                    question=qas["question"]
                    if dataset_name=='race':
                        #单独question
                        s_question=qas['s_question']

                elif dataset_name=="hotpotqa":
                    context,question,groundTruth=dataLoad.split_hotpot(dataset[i])

                else:
                    question_context = data['q_c'][i]
                    question = question_context.split("\\n")[0]
                    context = question_context.split("\\n")[1]
                    groundTruth = data['a'][i]
            
                modContext=datas['context'][_]
                print("==============starting processing data:%d==================" % _)
                
                answer=output_answer(client=client,question=question,context=context,model_name="gpt-3.5-turbo")
                modAnswer=output_answer(client=client,question=question,context=modContext,model_name="gpt-3.5-turbo")
                
                print("answer:", answer)
                print("modanswer:", modAnswer)
                result.append(util.record(_,context,modContext,question,answer,modAnswer,groundTruth,[],[]))
                print("===================finish modified answer%d===============" % _)

            json.dump(result,bug_file_f)
            bug_file_f.close()

def LLM4_testing(config_dict, model):
    for section,options in config_dict.items():
        print(f"[{section}]")
        # 遍历各个键值对
        for key, value in options.items():
            print(f"{key}={value}")
            client=connect_to_openai()
            bug_file = ("res-%s/%s/%s" % (section, model, value))
            bug_file_f = open(bug_file , 'a+', encoding='utf-8')
            origin_file = "res-%s/gpt-3.5/%s" % (section, value)
            origin_file = origin_file.replace(".json", "_bug.json")
            print(f"{key}={origin_file}")
            origin_file_f = open(origin_file, 'r', encoding='utf-8')
            datas = json.load(origin_file_f)
            result=[]
            for _ in range(len(datas)):
                data=datas[_]
                context=data['context']
                question=data['question']
                modContext=data['modContext']
                groundTruth=data['groundTruth']
                delsentence = data['delete sentence number']
                distance = data['distance value']
                print("==============starting processing data:%d==================" % _)
                
                answer=output_answer(client=client,question=question,context=context,model_name="gpt-4")
                modAnswer=output_answer(client=client,question=question,context=modContext,model_name="gpt-4")
                
                print("answer:", answer)
                print("modanswer:", modAnswer)
                result.append(util.record(_,context,modContext,question,answer,modAnswer,groundTruth,delsentence,distance))
                print("===================finish modified answer%d===============" % _)

            json.dump(result,bug_file_f)
            bug_file_f.close()

def chatgpt_check(config_dict, date):
    #其他模型生成的违反样例，先输入给gpt3.5
    tmp_config_dict = config_dict["gpt_check"]
    judge = 0
    if tmp_config_dict["mr"]=="mr3":
        judge=1
    tmp_file_name, datas=get_res_json(tmp_config_dict["dataset"], tmp_config_dict["mr"])
    output_file_1 = ("res-%s/gpt3.5/bug_" % (tmp_config_dict["dataset"])) + tmp_file_name.split("/")[-1].replace\
        (".json", date + ".json")
    output_file_1_all = ("res-%s/gpt3.5/all_" % (tmp_config_dict["dataset"])) + tmp_file_name.split("/")[-1].replace\
        (".json", date + ".json")
    output_file_1_f = open(output_file_1, 'a+', encoding='utf-8')
    output_file_1_all_f = open(output_file_1_all, '+a', encoding='utf-8')
    client=connect_to_openai()
    result=[]
    bug = []
    for _ in range(len(datas)):
        data=datas[_]
        context=data['context']
        question=data['question']
        modContext=data['modContext']
        groundTruth=data['groundTruth']
        print("==============starting processing data:%d==================" % _)
        
        answer=output_answer(client=client,question=question,context=context,model_name="gpt-3.5-turbo")
        modAnswer=output_answer(client=client,question=question,context=modContext,model_name="gpt-3.5-turbo")
        
        print("answer:", answer)
        print("modanswer:", modAnswer)
        if (not answerMatch(answer,modAnswer,_))^judge:
            bug.append(util.record(_,context,modContext,question,answer,modAnswer,groundTruth,[],[]))
        result.append(util.record(_,context,modContext,question,answer,modAnswer,groundTruth,[],[]))
        print("===================finish modified answer%d===============" % _)

    json.dump(result,output_file_1_all_f)
    json.dump(bug,output_file_1_f)
    output_file_1_f.close()
    
    """#gpt3.5的生成的违法样例，喂给gpt4
    output_file_2_all = output_file_1_all.replace("gpt3.5", "gpt4")
    output_file_2_all_f = open(output_file_2_all, 'a+', encoding='utf-8')
    output_file_2 = output_file_1.replace("gpt3.5", "gpt4")
    output_file_2_f = open(output_file_2, '+a', encoding='utf-8')
    datas=[]
    with open(output_file_1,'r',encoding='utf-8') as file:
        datas=json.load(file)
    result=[]
    bug = []
    for _ in range(len(datas)):
        data=datas[_]
        context=data['context']
        question=data['question']
        modContext=data['modContext']
        groundTruth=data['groundTruth']
        print("==============starting processing data:%d==================" % _)
        
        answer=output_answer(client=client,question=question,context=context,model_name="gpt-4")
        modAnswer=output_answer(client=client,question=question,context=modContext,model_name="gpt-4")
        
        if (not answerMatch(answer,modAnswer,_))^judge:
            bug.append(util.record(_,context,modContext,question,answer,modAnswer,groundTruth,[],[]))
        result.append(util.record(_,context,modContext,question,answer,modAnswer,groundTruth,[],[]))
        print("===================finish modified answer%d===============" % _)
    json.dump(bug,output_file_2_f)
    json.dump(result,output_file_2_all_f)"""
    
 
def LLM_restore(config_dict, model):
    for section,options in config_dict.items():
        print(f"[{section}]")
        # 遍历各个键值对
        for key, value in options.items():
            print(f"{key}={value}")
            client=connect_to_openai()
            bug_file = ("res-%s/%s/%s" % (section, model, value))
            bug_file_f = open(bug_file , 'r', encoding='utf-8')
            bug_datas = json.load(bug_file_f)
            new_bug_file = bug_file.replace(".json", "_new.json")
            new_bug_file_f = open(new_bug_file, '+a', encoding='utf-8')
            print(new_bug_file)
            origin_file = "res-%s/res-%s/%s" % (section, key, value)
            origin_file_f = open(origin_file, 'r', encoding='utf-8')
            datas = json.load(origin_file_f)
            result=[]
            for _ in range(len(datas)):
                data=datas[_]
                context=data['context']
                question=data['question']
                modContext=data['modContext']
                groundTruth=data['groundTruth']
                delsentence = data['delete sentence number']
                distance = data['distance value']
                print("==============starting processing data:%d==================" % _)
                
                answer=output_answer(client=client,question=question,context=context,model_name="gpt-3.5-turbo")
                modAnswer=output_answer(client=client,question=question,context=modContext,model_name="gpt-3.5-turbo")
                
                print("answer:", answer)
                print("modanswer:", modAnswer)
                result.append(util.record(_,context,modContext,question,answer,modAnswer,groundTruth,delsentence,distance))
                print("===================finish modified answer%d===============" % _)

            json.dump(result,bug_file_f)
            bug_file_f.close()


def LLM_testing(config_dict, model):
    for section,options in config_dict.items():
        print(f"[{section}]")
        # 遍历各个键值对
        for key, value in options.items():
            print(f"{key}={value}")
            client=connect_to_openai()
            bug_file = ("res-%s/%s/%s" % (section, model, value))
            bug_file_f = open(bug_file , 'a+', encoding='utf-8')
            origin_file = "res-%s/res-%s/%s" % (section, key, value)
            origin_file_f = open(origin_file, 'r', encoding='utf-8')
            datas = json.load(origin_file_f)
            result=[]
            for _ in range(len(datas)):
                data=datas[_]
                context=data['context']
                question=data['question']
                modContext=data['modContext']
                groundTruth=data['groundTruth']
                delsentence = data['delete sentence number']
                distance = data['distance value']
                print("==============starting processing data:%d==================" % _)
                
                answer=output_answer(client=client,question=question,context=context,model_name="gpt-3.5-turbo")
                modAnswer=output_answer(client=client,question=question,context=modContext,model_name="gpt-3.5-turbo")
                
                print("answer:", answer)
                print("modanswer:", modAnswer)
                result.append(util.record(_,context,modContext,question,answer,modAnswer,groundTruth,delsentence,distance))
                print("===================finish modified answer%d===============" % _)

            json.dump(result,bug_file_f)
            bug_file_f.close()