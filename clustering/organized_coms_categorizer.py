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
        stopped_tokens = [i for i in line.split() if not i in en_stop]
        stemmed_tokens = [stemmer.stem(i) for i in stopped_tokens]
        cleaned_up_line = [i for i in stemmed_tokens if i not in ["i", "ll", "'m", "n't", "ve", "import"]]
        new_line = " ".join(cleaned_up_line)
        new_line = new_line.translate(str.maketrans('','', string.digits))
        new_line = new_line.translate(str.maketrans('','',string.punctuation))
        new_doc.append(new_line)
    return new_doc    

def sorted_words_by_weight(cluster_centers):
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
        for document in frame.ix[i]['documents'].values.tolist():
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

raw_docs = read_documents("glove_insight_docs.txt")

documents = process_documents(raw_docs)

original_docs = read_documents("COMS4170Insight.txt")

doc_dict = dict(zip(documents, original_docs))

user_in = ''
previous_clusters = dict()

while not user_in.upper() == 'Q':
    vectorizer = TfidfVectorizer(stop_words=stop_words, ngram_range=(1,3))
    X = vectorizer.fit_transform(documents)
    true_k = 5
    model = KMeans(n_clusters=true_k, init='k-means++', max_iter=1000, n_init=1)
    model.fit(X)
    order_centroids = model.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()

    sorted_terms = sorted_words_by_weight(model.cluster_centers_)

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
    print("num_per_cluster")
    print(num_per_cluster)
    

    words_per_cluster = 7 #words are sorted, so this is number of top (heaviest weight) words
    num_sentences_shown = 10 #number of sentences to display per cluster
    #num_words_shown = 10 #number of words to display per sentence in cluster (can try to do this but is v hard)
    current_clusters = categorize_into_clusters(true_k, sorted_terms)
    matched_sentences = match_top_sentences_to_cluster(true_k, clusters, sentences, sorted_terms, num_sentences_shown)

    for i in range(true_k):
        print("Cluster %d:" % i)
        for key in list(current_clusters[i].keys())[:words_per_cluster]:
            weight = "{:4.2f}".format(current_clusters[i][key]*100) #make decimal into a percentage and format
            print("{}: {}%".format(key, weight))
            #print(key + ": " + str(current_clusters[i][key]))
        print()

        print("Cluster %d sentences:" % i)
        for doc_values in matched_sentences[i]:
            print(doc_dict[doc_values[0]])
            weight = "{:4.2f}".format(doc_values[1]*100)
            print("{}: {} | SCORE: {}".format(str(doc_values[2]), str(doc_values[3]), weight))
            #print(str(doc_values[2]) + ": " + str(doc_values[3]) + " | SCORE: " + str(doc_values[1]))
            print()

    print()
    '''
        for i in range(k):
            for key in sorted_terms[i].keys():
                current_clusters[i][key] = sorted_terms[i][key]
    '''

    if(user_in.upper() == 'A' or user_in.upper() == 'R'):
        print("Previous Clusters: ")
        for cluster_number in range(len(previous_clusters)):
            print("Cluster %d: " % cluster_number, end="")
            for key in list(previous_clusters[cluster_number].keys())[:words_per_cluster]:
                print(key, end=" ")
            print()
        print()
        print("New Clusters: ")
        for cluster_number in range(len(current_clusters)):
            print("Cluster %d: " % cluster_number, end="")
            for key in list(current_clusters[cluster_number].keys())[:words_per_cluster]:
                print(key, end=" ")
            print()
        print()
       
    user_in = ''
    while not (user_in.upper() == 'A' or user_in.upper() == 'R' or user_in.upper() == 'S' or user_in.upper() == 'Q'):
        user_in = input("Add stop word (A), remove stop word (R), save and quit (S) or quit (Q): ")

    if user_in.upper() == 'A':
        s_word = input("Input new stop word: ")
        add_stop_word(s_word)
        previous_clusters = current_clusters
    elif user_in.upper() == 'R':
        s_word = input("Input stop word to remove: ")
        remove_stop_word(s_word)
        previous_clusters - current_clusters
    elif user_in.upper() == 'S':
        save_stop_words()
        user_in = 'Q'
 
    





