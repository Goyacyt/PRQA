from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import pipeline,AutoModelForQuestionAnswering
import torch
import os
from tools.askchatGPT import askGPT4
from openai import OpenAI
import httpx
os.environ['CURL_CA_BUNDLE'] = ''
import sys
sys.path.append(".")
sys.path.append("./tools")


def connect_to_openai():
    client = OpenAI(
        base_url="https://oneapi.xty.app/v1", 
        api_key="",
        http_client=httpx.Client(
            base_url="https://oneapi.xty.app/v1",
            follow_redirects=True,
        ),
    )
    return client

def output_answer(client,question,context,model_name):
    if model_name!="gpt-4" and model_name!='gpt-3.5-turbo':
        name='./model/unifiedqa-'+model_name
        model=AutoModelForSeq2SeqLM.from_pretrained(name)
        tokenizer=AutoTokenizer.from_pretrained(name)
        device = torch.device("cuda")
        inputs = tokenizer(question, context, return_tensors="pt",max_length=1024).input_ids.to(device)
        model.to(device)
        with torch.no_grad():
            outputs = model.generate(inputs)
        #print(outputs)
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    else:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You should answer the question in a short sentence according only to the context given."},
                {"role": "user", "content": f"context:{context};question:{question}"}
            ]
        )
        return completion.choices[0].message.content


if __name__=='__main__':
    question='Why is model conversion important?',
    context='The option to convert models between FARM and transformers gives freedom to the user and let people easily switch between frameworks.'
    print(output_answer(question,context,"gpt-4"))