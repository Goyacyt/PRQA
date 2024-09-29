from openai import OpenAI
import httpx
import sys
sys.path.append(".")
sys.path.append("./tools")

def connect_to_openai():
    client = OpenAI(
        base_url="https://oneapi.xty.app/v1", 
        api_key="sk-mCq1swP7HCfy8yB122B8838926414f9aA9829e22E5Ed2cC6",
        http_client=httpx.Client(
            base_url="https://oneapi.xty.app/v1",
            follow_redirects=True,
        ),
    )
    return client

def askGPT4(client,messages):
    MODEL = "gpt-4"
    completion = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )
    return completion['choices'][0]['message']['content']

if __name__=='__main__':

    messages=[
        {"role": "system", "content": ""},
        {"role": "user", "content": ""}
    ]
    client=connect_to_openai()
    print(askGPT4(client,messages))