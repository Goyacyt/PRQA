from sentence_transformers import SentenceTransformer,util
import re
from datasets import load_dataset
import sys
sys.path.append(".")
sys.path.append("./tools")

from tools.util import split_context
from tools.util import get_postag_real

from nltk.corpus import wordnet

import nltk
from nltk.tokenize import word_tokenize

#model = SentenceTransformer('all-MiniLM-L6-v2')
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def sentenceTransformerRun(oriContext,question,topk):
    """sentence_embeddings=model.encode(context)
    question_embeddings=model.encode(question)

    cos_sim=util.cos_sim(sentence_embeddings,question_embeddings)
    sentence_distance=[]
    for i in range(len(cos_sim)):
        if not sentence_context[i]:
            continue
        sentence_distance.append([question,sentence_context[i],cos_sim[i][0].item()])
    return cos_sim[0][0]"""
    return 

def semanticMatch(oriContext,question):
    context=split_context(oriContext)
    # Context embeddings
    context_embeddings = model.encode(context)

    # Question embeddings
    question_embeddings = model.encode(question)

    # Find the top k context sentence matching the question
    hits = util.semantic_search(question_embeddings,context_embeddings,top_k=len(context))
    hits=hits[0]
    # Print and save results
    results=[]
    #print(f"Question: {question}")
    for hit in hits:
        #print(hit['corpus_id'],type(hit['corpus_id']))
        #print(context[hit['corpus_id']], "(Score: {:.4f})".format(hit['score']))
        results.append([hit['corpus_id'],hit['score']])
    
    return results

def superpositon(context,question):
    #给出和问题中的单词有重合的句子

    nltk.download('punkt')
    context=context.strip().lower()
    question=question.strip().lower()

    words=get_postag_real(question)
    context=split_context(context)

    superpositonnum=[]

    for i in range(len(context)):
        for j in range(len(words)):
            if words[j] in context[i]:
                superpositonnum.append(i)
                break
    
    return superpositonnum


def calculate_semantic_similarity(word1, word2):
    synsets1 = wordnet.synsets(word1)
    synsets2 = wordnet.synsets(word2)

    if synsets1 and synsets2:
        # 选择两个词汇项中的第一个
        synset1 = synsets1[0]
        synset2 = synsets2[0]

        # 计算词汇项之间的路径相似度
        similarity_score = synset1.path_similarity(synset2)
        return similarity_score if similarity_score is not None else 0.0
    else:
        return 0.0

def calculate_semantic_similarity_for_sentence(sentence, question):
    nlp_sentence = sentence.split()
    nlp_question = question.split()

    # 计算句子中每个词与整个问题句的路径相似度
    similarity_scores = []
    for word_sentence in nlp_sentence:
        max_similarity_score = 0.0
        for word_question in nlp_question:
            similarity_score = calculate_semantic_similarity(word_sentence, word_question)
            max_similarity_score = max(max_similarity_score, similarity_score)
        similarity_scores.append((word_sentence, max_similarity_score))

    return similarity_scores

if __name__=='__main__':
    context="Soon they are fighting over the cloak and criticizing the author and the spectators as well.In the play proper, the goddess Diana, also called Cynthia, has ordained a \"solemn revels\" in the valley of Gargaphie in Greece. The gods Cupid and Mercury appear, and they too start to argue. Mercury has awakened Echo, who weeps for Narcissus, and states that a drink from Narcissus's spring causes the drinkers to \"Grow dotingly enamored of themselves.\" The courtiers and ladies assembled for the Cynthia's revels all drink from the spring.Asotus, a foolish spendthrift who longs to become a courtier and a master of fashion and manners, also drinks from the spring; Two symbolic masques are performed within the play for the assembled revelers. At their conclusion, Cynthia (representing Queen Elizabeth) has the dancers unmask and shows that vices have masqueraded as virtues. She sentences them to make reparation and to purify themselves by bathing in the spring at Mount Helicon.The figure of Actaeon in the play may represent Robert Devereux, 2nd Earl of Essex, while Cynthia's lady in waiting Arete may be Lucy, Countess of Bedford, one of Elizabeth's ladies in waiting as well as Jonson's patroness.The play is notably rich in music, as is typical for the theatre of the boys' companies, which originated as church choirs."
    question="Virtues VIRTUES you"
    print(superpositon(context,question))
