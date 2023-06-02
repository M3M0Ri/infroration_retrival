import csv
import hazm
import numpy as np
from collections import OrderedDict

def readAndNormalize():
    dataset_file = open('articles.csv', 'r', encoding='utf8')
    dataset = csv.reader(dataset_file, delimiter=',')
    next(dataset)
    normalizer = hazm.Normalizer()
    lemmatizer = hazm.Lemmatizer()
    doc_dict = {}
    for row in dataset:
        id = row[4]
        text = normalizer.normalize(row[5])
        doc_dict[id] = []
        sentences = hazm.sent_tokenize(text)
        words = []
        for s in sentences:
            words = words + hazm.word_tokenize(s)
            for word in words:
                string = lemmatizer.lemmatize(word)
                if '#' in string:
                    token = string.split('#')[0]
                    doc_dict[id].append(token)
                else:
                    doc_dict[id].append(string)
    return doc_dict


def get_all_tokens(doc_dict):
    all_tokens = []
    for token_list in doc_dict.values():
        for token in token_list:
            if not (token in all_tokens):
                all_tokens.append(token)
    return all_tokens


def df(indexed_tokens):
    df_dict = {}
    for token, doc_keys in indexed_tokens.items():
        df_dict[token] = len(doc_keys)
    return df_dict

def idf(n, df_dict):
    idf_dict = {}
    for token in df_dict.keys():
        idf_dict[token] = np.log2((n + 1) / df_dict[token])
    return idf_dict


def tf(all_tokens, doc_dict):
    tf_dict = {}
    for i in doc_dict.keys():
        tf_dict[i] = {}

    for token in all_tokens:
        for i, token_list in doc_dict.items():
            tf_dict[i][token] = token_list.count(token)

    return tf_dict


def tfidf(all_tokens, doc_dict, tf_dict, idf_dict):
    tfidf_dict = {}
    for i in doc_dict.keys():
        tfidf_dict[i] = {}
    for token in all_tokens:
        for i, token_list in doc_dict.items():
            tfidf_dict[i][token] = tf_dict[i][token] * idf_dict[token]
    return tfidf_dict


def indexing(doc_dict, all_tokens):
    indexed_tokens = {}

    for token in all_tokens:
        indexed_tokens[token] = []
        for i, token_list in doc_dict.items():
            if token in token_list:
                indexed_tokens[token].append(i)

    return indexed_tokens


def boolean_retrive(indexed_tokens, q, p, operand):
    normalizer = hazm.Normalizer()
    lemmatizer = hazm.Lemmatizer()
    qp = q + ' ' + p
    n = normalizer.normalize(qp)
    q, p = hazm.word_tokenize(normalizer.normalize(qp))
    q, p = lemmatizer.lemmatize(q), lemmatizer.lemmatize(p)

    def and_operand():
        if q not in indexed_tokens or p not in indexed_tokens:
            print('no docs found !')
            return
        q_docs = indexed_tokens[q]
        p_docs = indexed_tokens[p]
        return list(set(q_docs).intersection(p_docs))

    def or_operand():
        if q not in indexed_tokens:
            p_docs = indexed_tokens[p]
            q_docs = []

        elif p not in indexed_tokens:
            q_docs = indexed_tokens[q]
            p_docs = []

        else:
            p_docs = indexed_tokens[p]
            q_docs = indexed_tokens[q]

        return list(dict.fromkeys(q_docs + p_docs))

    if operand == 'AND':
        result = and_operand()
    elif operand == 'OR':
        result = or_operand()
    else:
        raise Exception

    return result


def vector_retrive(doc_dict, search_query, tfidf_dict):
    search_tokens = []
    normalizer = hazm.Normalizer()
    lemmatizer = hazm.Lemmatizer()
    n = normalizer.normalize(search_query)
    sentences = hazm.sent_tokenize(n)
    words = []
    for s in sentences:
        words = words + hazm.word_tokenize(s)
    for word in words:
        string = lemmatizer.lemmatize(word)
        token = string.split('#')[0]
        search_tokens.append(token)

    search_tokens_list = list(dict.fromkeys(search_tokens))
    search_tokens_score = {}
    for token in search_tokens_list:
        search_tokens_score[token] = search_tokens.count(token)

    relevance_scores = {}
    for i in doc_dict.keys():
        score = 0
        for token in search_tokens_list:
            score += search_tokens_score[token] * tfidf_dict[i][token]
        relevance_scores[i] = score
    sorted_value = OrderedDict(sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True))
    top_5 = {k: sorted_value[k] for k in list(sorted_value)[:5]}
    return top_5


doc_dict = readAndNormalize()
all_tokens = get_all_tokens(doc_dict=doc_dict)
indexed = indexing(all_tokens=all_tokens, doc_dict=doc_dict)
with open('inverted.out', 'w', encoding='utf8') as f:
    for t, l in indexed.items():
        f.write(f"{t} | {l}\n")


search_type = int(input('1 - Boolean search\n2 - Vector search\n Enter search type index: '))
if search_type == 1:
    with open('query_boolean.txt', 'r', encoding='utf8') as f:
        text = f.read()
        text = text.replace('\n', '')
        q, operand, p = text.split()

    result = boolean_retrive(indexed_tokens=indexed, q=q, p=p, operand=operand)
    print(*result, sep='\n')

elif search_type == 2:
    with open('query.txt', 'r', encoding='utf8') as f:
        q = f.read()
        q = q.replace('\n', '')
    idf_dict = idf(len(doc_dict), df(indexed))
    tf_dict = tf(all_tokens=all_tokens, doc_dict=doc_dict)
    tfidf_dict = tfidf(all_tokens=all_tokens, doc_dict=doc_dict, idf_dict=idf_dict, tf_dict=tf_dict)
    result = vector_retrive(doc_dict=doc_dict, search_query=q, tfidf_dict=tfidf_dict)
    print(*result.keys(), sep='\n')
