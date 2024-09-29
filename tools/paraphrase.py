from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import sys
sys.path.append(".")
sys.path.append("./tools")

device = "cuda"

tokenizer = AutoTokenizer.from_pretrained("./model/chatgpt_paraphraser_on_T5_base")

model = AutoModelForSeq2SeqLM.from_pretrained("./model/chatgpt_paraphraser_on_T5_base")#.to(device)

def paraphrase(
    question,
    num_beams=5,
    num_beam_groups=5,
    num_return_sequences=1,
    repetition_penalty=10.0,
    diversity_penalty=3.0,
    no_repeat_ngram_size=2,
    temperature=0.7,
    max_length=128
):
    input_ids = tokenizer(
        f'paraphrase: {question}',
        return_tensors="pt", padding="longest",
        max_length=max_length,
        truncation=True,
    ).input_ids#.to(device)
    
    outputs = model.generate(
        input_ids, temperature=temperature, repetition_penalty=repetition_penalty,
        num_return_sequences=num_return_sequences, no_repeat_ngram_size=no_repeat_ngram_size,
        num_beams=num_beams, num_beam_groups=num_beam_groups,
        max_length=max_length, diversity_penalty=diversity_penalty
    )

    res = tokenizer.batch_decode(outputs, skip_special_tokens=True)

    return res[0]


if __name__=='__main__':
    text = 'What are the best places to see in New York?'
    messages=[
        {"role": "system", "content": "Rewrite the context,keep the information unchanged."},
        {"role": "user", "content": "What are the best places to see in New York?"},
    ]
    result=paraphrase(text)
    print(result)
