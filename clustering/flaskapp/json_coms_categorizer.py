from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from operator import itemgetter
import csv
import re
import string
import pandas as pd
from sklearn.externals import joblib
from stop_words import get_stop_words
from nltk.stem.snowball import SnowballStemmer
import json
import os.path
import random

#https://stackoverflow.com/questions/11122291/python-find-char-in-string-can-i-get-all-indexes?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
def find_all_indices(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

def match_words(Y, terms):

    Y_arr = Y.toarray()
    words = []
    max_words = 15
    for row in range(len(Y_arr)):
        col = 0;
        word_count = 0;
        while col < len(Y_arr[row]) and word_count < max_words:
            if not Y_arr[row][col] == 0:
                word = terms[col]
                coord = "(" + str(row) + ", " + str(col) + ")"
                tfidf = Y_arr[row][col]
                words.append((word, coord, tfidf))
                word_count += 1
            col += 1

    words = sorted(words, key=itemgetter(2), reverse=True)
    return words

def to_string(tup_list):
    s = ""
    for tup in tup_list:
        s += "{0:<20} {1:<12} {2:>20} \n".format(tup[0], tup[1], str(tup[2]))
        #s += tup[0] + ": " + tup[1] + "\t" + str(tup[2]) +"\n"
    return s

def read_stop_words(file_name):
    with open(file_name) as f:
        reader = csv.reader(f)
        next(reader) #skip first line
        stop_words = []
        for row in reader:
            stop_words.append(row[0])
        f.close()
    return stop_words

def add_stop_word(word):
    if word in stop_words:
        return False;
    else:
        stop_words.append(word)
        return word

def remove_stop_word(word):
    if word in stop_words:
        stop_words.remove(word)
        return word
    else:
        return False;

def reset_stop_words():
    with open("stopwords.csv") as f:
        reader = csv.reader(f)
        next(reader) #skip first line
        stop_words = []
        for row in reader:
            stop_words.append(row[0])
    f.close()

def save_stop_words():
    with open("stopwords.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["English Stop Words"])
        for sw in stop_words:
            writer.writerow([sw])
    f.close()    

def read_documents(file_name):
    with open(file_name, 'r') as f:
        documents = []
        for line in f:
            if len(line) > 0:
                documents.append(line.strip())
        f.close()
    return documents

def process_documents(documents):
    en_stop = get_stop_words('en')
    stemmer = SnowballStemmer("english")
    # remove stop words from tokens and stem
    new_doc = []
    for line in documents:
        line = line.lower()
        line = line.translate(str.maketrans('','', string.digits))
        line = line.translate(str.maketrans('','',string.punctuation))
        stopped_tokens = [i for i in line.split() if not i in en_stop]
        stemmed_tokens = [stemmer.stem(i) for i in stopped_tokens]
        cleaned_up_line = [i for i in stemmed_tokens if i not in ["i", "ll", "'m", "im", "n't", "ve", "import", "sometim"]]
        new_line = " ".join(cleaned_up_line)
        new_doc.append(new_line)
    return new_doc

def get_token_dict(documents):
    en_stop = get_stop_words('en')
    stemmer = SnowballStemmer("english")
    # remove stop words from tokens and stem
    token_dict = dict()
    for line in documents:
        line = line.lower()
        line = line.translate(str.maketrans('','', string.digits))
        line = line.translate(str.maketrans('','',string.punctuation))
        stopped_tokens = [i for i in line.split() if not i in en_stop]
        stemmed_tokens = [stemmer.stem(i) for i in stopped_tokens]
        cleaned_up_line = [i for i in stemmed_tokens if i not in ["i", "ll", "'m", "im", "n't", "ve", "import", "sometim"]]
        subset_dict = dict(zip(stemmed_tokens, stopped_tokens))
        for key in subset_dict:
            if key not in token_dict:
                token_dict[key] = set()
            token_dict[key].add(subset_dict[key])
        new_line = " ".join(cleaned_up_line)
    return token_dict    

def sorted_words_by_weight(cluster_centers, terms):
    sorted_terms = []
    for row in range(len(cluster_centers)):
        terms_dict = {}
        for col in range(len(cluster_centers[row])):
            if not cluster_centers[row][col] == 0:
                terms_dict[terms[col]] = cluster_centers[row][col]
        sorted_dict = dict(sorted(terms_dict.items(), key=itemgetter(1), reverse=True))
        sorted_terms.append(sorted_dict)
    return sorted_terms

def categorize_into_clusters(k, sorted_terms):
    current_clusters = [dict() for x in range(k)]
    for i in range(k):
        for key in sorted_terms[i].keys():
            current_clusters[i][key] = sorted_terms[i][key]
    return current_clusters

def calculate_document_score(document_word_scores):
    sum = 0
    for word in document_word_scores:
        sum += document_word_scores[word][0] * document_word_scores[word][1]
    return sum

def match_top_sentences_to_cluster(k, clusters, sentences, sorted_terms, num_sentences_shown=10):
    lowest_weight_threshold = 0.01
    frame = pd.DataFrame(sentences, index = [clusters] , columns = ['documents', 'cluster'])
    # print("-----FRAME-----")
    # print(frame.to_string())
    matched_sentences = [list() for x in range(k)]
    for i in range(k):
        document_indicators = [] #[document, doc_score, indicator_sentences, indicator_words]
        # print("---------\nlength: " + str(len(frame.ix[i])))
        # print(frame.ix[i])
        # print("---------\n")
        doc_subframe = frame.ix[i]['documents']
        if len(frame.ix[i]) <= 2:
            # print(frame.ix[i]['documents'])
            #doc_subframe = pd.Series(frame.ix[i]['documents'])
            return False
        for document in doc_subframe.values.tolist():
            sentences = document.split(". ")
            document_word_scores = dict() #a dict mapping word to freq and weight {"word": [frequency, weight]}
            indicator_words = set()
            indicator_sentences = set()
            for sentence in sentences:
                is_indicator = False
                words = sentence.split()
                for word in words:
                    word_no_punc = re.sub(r'[^\w\s]','',word)
                    if word_no_punc.lower() in sorted_terms[i]: #and sorted_terms[i][word_no_punc.lower()] > lowest_weight_threshold:
                        if sorted_terms[i][word_no_punc.lower()] > lowest_weight_threshold:
                            indicator_words.add(word_no_punc)
                            is_indicator = True
                        # maps frequency and weight of each word to the dictionary
                        if word_no_punc.lower() in document_word_scores:
                            document_word_scores[word_no_punc.lower()][0] += 1
                        else:
                            document_word_scores[word_no_punc.lower()] = [1, sorted_terms[i][word_no_punc.lower()]]
                if is_indicator:
                    indicator_sentences.add(sentence.strip())

            doc_score = calculate_document_score(document_word_scores)
            # score, indicator sentences, and indicator words to document dictionary
            document_indicators.append((document, doc_score, indicator_sentences, indicator_words))

        #sort documents in descending order by score
        sorted_documents = sorted(document_indicators,key=itemgetter(1), reverse=True)

        #append top documents in cluster to matched_sentences
        for n in range(num_sentences_shown):
            if n<len(sorted_documents): 
                matched_sentences[i].append(sorted_documents[n])

    return matched_sentences

def match_all_sentences_to_cluster(k, clusters, sentences, sorted_terms, num_sentences_per_cluster):
    lowest_weight_threshold = 0.01
    frame = pd.DataFrame(sentences, index = [clusters] , columns = ['documents', 'cluster'])
    # print("-----FRAME-----")
    # print(frame.to_string())
    matched_sentences = [list() for x in range(k)]
    for i in range(k):
        document_indicators = [] #[document, doc_score, indicator_sentences, indicator_words]
        # print("---------\nlength: " + str(len(frame.ix[i])))
        # print(frame.ix[i])
        # print("---------\n")
        doc_subframe = frame.ix[i]['documents']
        if len(frame.ix[i]) <= 2:
            # print(frame.ix[i]['documents'])
            #doc_subframe = pd.Series(frame.ix[i]['documents'])
            return False
        for document in doc_subframe.values.tolist():
            sentences = document.split(". ")
            document_word_scores = dict() #a dict mapping word to freq and weight {"word": [frequency, weight]}
            indicator_words = set()
            indicator_sentences = set()
            for sentence in sentences:
                is_indicator = False
                words = sentence.split()
                for word in words:
                    word_no_punc = re.sub(r'[^\w\s]','',word)
                    if word_no_punc.lower() in sorted_terms[i]: #and sorted_terms[i][word_no_punc.lower()] > lowest_weight_threshold:
                        if sorted_terms[i][word_no_punc.lower()] > lowest_weight_threshold:
                            indicator_words.add(word_no_punc)
                            is_indicator = True
                        # maps frequency and weight of each word to the dictionary
                        if word_no_punc.lower() in document_word_scores:
                            document_word_scores[word_no_punc.lower()][0] += 1
                        else:
                            document_word_scores[word_no_punc.lower()] = [1, sorted_terms[i][word_no_punc.lower()]]
                if is_indicator:
                    indicator_sentences.add(sentence.strip())

            doc_score = calculate_document_score(document_word_scores)
            # score, indicator sentences, and indicator words to document dictionary
            document_indicators.append((document, doc_score, indicator_sentences, indicator_words))

        #sort documents in descending order by score
        sorted_documents = sorted(document_indicators,key=itemgetter(1), reverse=True)

        #append top documents in cluster to matched_sentences
        for n in range(num_sentences_per_cluster[i]):
            if n<len(sorted_documents): 
                matched_sentences[i].append(sorted_documents[n])

    return matched_sentences


def append_mark_tag(sentence, keys, token_dict, highlight_colors):
    appended_sent = ""
    stemmer = SnowballStemmer("english")
    for word in sentence.split():
        stemmed_word = stemmer.stem(word).translate(str.maketrans('','',string.punctuation)).translate(str.maketrans('','', string.digits))
        if stemmed_word in keys:
            i = keys.index(stemmed_word)
            appended_sent += "<mark style='background-color:" + highlight_colors[i] + "'> <b>" + word + "</b></mark> "
        else:
            appended_sent += word + " "
    return appended_sent.strip()

def sort_clusters_by_weight(data):
    sorted_data = {}
    sorted_data['Document count'] = data['Document count']
    cluster_to_weight = dict()
    for i in range(true_k):
        cluster_to_weight['Cluster %d' % i] = float(data['Cluster %d' % i][0]['word_weight'])
    #[(4, 34), (1, 39), (2, 87), (7, 110)]
    sorted_cluster_to_weight = sorted(cluster_to_weight.items(), key=lambda x: x[1], reverse=True)
    for i in range(true_k):
        sorted_data['Cluster %d' % i] = data[sorted_cluster_to_weight[i][0]]
    return sorted_data



'''
def get_top_words(k, sorted_terms):
    top_words = {}
    for i in range(k):
        for j in range(len(sorted_terms[i])):
            if sorted_terms[i][j][1] == 0.0:
                break
            top_words[sorted_terms[i][j][0].lower()] = sorted_terms[i][j][1]
    return top_words
'''
stop_words = read_stop_words("stopwords.csv")
rand_int = random.randint(0, 1000)
true_k = 5
num_top_words = 7

def new_seed():
    global rand_int
    rand_int = random.randint(0, 1000)
    print("new seed: " + str(rand_int))

def run(k=5, n=7, added_stop_word="", removed_stop_word=""):
    global true_k
    true_k = k
    global num_top_words
    num_top_words = n

    print(rand_int)
    if not added_stop_word == "":
        print("added " + added_stop_word)
        add_stop_word(added_stop_word)
    if not removed_stop_word == "":
        print("removed " + removed_stop_word)
        remove_stop_word(removed_stop_word)

    raw_docs = read_documents("COMS4170Insight.txt")

    documents = process_documents(raw_docs)

    original_docs = read_documents("COMS4170Insight.txt")

    doc_dict = dict(zip(documents, original_docs))
    token_dict = get_token_dict(raw_docs)

    user_in = ''
    previous_clusters = dict()

    data = {}
    opacity = str(.8)
    highlight_colors = ["rgba(37,101,222,"+opacity+")", "rgba(70,124,227,"+opacity+")", "rgba(76,129,228,"+opacity+")", "rgba(83,133,229,"+opacity+")", "rgba(102,147,232,"+opacity+")", "rgba(109,152,233,"+opacity+")", "rgba(142,175,238,"+opacity+")", "rgba(148,180,239,"+opacity+")", "rgba(155,184,240,"+opacity+")", "rgba(187,207,245,"+opacity+")", "rgba(220,230,250,"+opacity+")"]

    # while not user_in.upper() == 'Q':
    matched_sentences = False
    while not matched_sentences:
        vectorizer = TfidfVectorizer(stop_words=stop_words, ngram_range=(1,3), min_df=2)
        X = vectorizer.fit_transform(documents)
        # true_k = 5
        model = KMeans(n_clusters=true_k, init='k-means++', max_iter=1000, n_init=1, random_state=rand_int)
        model.fit(X)
        order_centroids = model.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()

        sorted_terms = sorted_words_by_weight(model.cluster_centers_, terms)

        #can use this pickle thing to save KMeans model/centroids? idk
        #http://brandonrose.org/clustering says something about reloading the model/reassigning the labels as the clusters
        #joblib.dump(model, 'doc_cluster.pkl')

        #model = joblib.load('doc_cluster.pkl')

        #create DataFrame to match sentence with the cluster it belongs to
        clusters = model.labels_.tolist()
        sentences = {'documents': documents, 'cluster': clusters}
        frame = pd.DataFrame(sentences, index = [clusters] , columns = ['documents', 'cluster'])

        #display how many sentences there are in each cluster
        num_per_cluster = frame['cluster'].value_counts()
        num_sentences_per_cluster = num_per_cluster.to_dict()

        words_per_cluster = num_top_words #words are sorted, so this is number of top (heaviest weight) words
        num_sentences_shown = 3 #number of sentences to display per cluster
        #num_words_shown = 10 #number of words to display per sentence in cluster (can try to do this but is v hard)
        current_clusters = categorize_into_clusters(true_k, sorted_terms)
        #matched_sentences = match_top_sentences_to_cluster(true_k, clusters, sentences, sorted_terms, num_sentences_shown)
        matched_sentences = match_all_sentences_to_cluster(true_k, clusters, sentences, sorted_terms, num_sentences_per_cluster)
        if matched_sentences == False:
            print(str(matched_sentences) + ": CLUSTERS WERE INVALID")
            new_seed()

    #WRITE TO JSON FILE
    data['Document count'] = len(documents)
    for i in range(true_k):
        #print("Cluster %d:" % i)
        data['Cluster %d' % i] = []
        keys = []
        for key in list(current_clusters[i].keys())[:words_per_cluster]:
            keys.extend(key.split())
            weight = "{:4.2f}".format(current_clusters[i][key]*100) #make decimal into a percentage and format
            #print("{}: {}%".format(key, weight))
            original_key = ""
            for word in key.split():
                shortest_word = list(token_dict[word])[0]
                for val in list(token_dict[word])[1:]:
                    if len(val) < len(shortest_word):
                        shortest_word = val
                original_key += shortest_word + " "
            if len(keys)-1 < len(highlight_colors):
                original_key = "<mark style='background-color:" + highlight_colors[len(keys)-1] + "'>" + original_key.strip() + "</mark>"
            else:
                original_key = "<mark style='background-color:rgba(220,230,250,"+opacity+")>" + original_key.strip() + "</mark>"

            data['Cluster %d' % i].append({  
                'word': original_key,
                'word_weight': weight
            })
            #print(key + ": " + str(current_clusters[i][key]))
        #print()

        #print("Cluster %d sentences:" % i)
        data['Cluster %d' % i].append({ 
                'doc_count': str(num_sentences_per_cluster[i]),
            })
        for doc_values in matched_sentences[i]:
            #print(doc_dict[doc_values[0]])
            weight = "{:4.2f}".format(doc_values[1]*100)
            sentence = doc_dict[doc_values[0]]
            marked_sentence = append_mark_tag(sentence, keys, token_dict, highlight_colors)
            data['Cluster %d' % i].append({ 
                'sentence': marked_sentence,
                'sent_weight': weight,
                'indicatorSentences': list(doc_values[2]),
                'indicatorWords': list(doc_values[3])
            })
    #print()
    sorted_data = sort_clusters_by_weight(data)
    #print(os.path.abspath("~"))
    #path = os.path.join(os.path.abspath("~"), "/static/coms_cluster_data.js")
    path = "./static/coms_cluster_data.js"
    with open(path, 'w') as outfile:  
        outfile.write("data=")
        json.dump(sorted_data, outfile)

    # if(user_in.upper() == 'A' or user_in.upper() == 'R'):
    #     print("Previous Clusters: ")
    #     for cluster_number in range(len(previous_clusters)):
    #         print("Cluster %d: " % cluster_number, end="")
    #         for key in list(previous_clusters[cluster_number].keys())[:words_per_cluster]:
    #             print(key, end=" ")
    #         print()
    #     print()
    #     print("New Clusters: ")
    #     for cluster_number in range(len(current_clusters)):
    #         print("Cluster %d: " % cluster_number, end="")
    #         for key in list(current_clusters[cluster_number].keys())[:words_per_cluster]:
    #             print(key, end=" ")
    #         print()
    #     print()
       
    # user_in = ''
    # while not (user_in.upper() == 'A' or user_in.upper() == 'R' or user_in.upper() == 'S' or user_in.upper() == 'Q'):
    #     user_in = input("Add stop word (A), remove stop word (R), save and quit (S) or quit (Q): ")

    # if user_in.upper() == 'A':
    #     s_word = input("Input new stop word: ")
    #     add_stop_word(s_word)
    #     previous_clusters = current_clusters
    # elif user_in.upper() == 'R':
    #     s_word = input("Input stop word to remove: ")
    #     remove_stop_word(s_word)
    #     previous_clusters - current_clusters
    # elif user_in.upper() == 'S':
    #     save_stop_words()
    #     user_in = 'Q'
 
    





