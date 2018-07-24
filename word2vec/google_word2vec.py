import gensim 
import os
import gensim
from gensim import models
#from gensim.models import Word2Vec, KeyedVectors
from gensim.models.word2vec import Word2Vec
from nltk.corpus import stopwords
import csv
import re

def read_documents(fileName):
	with open(fileName) as f:
	    reader = csv.reader(f)
	    documents = []
	    for row in reader:
	        if len(row) > 0:
	        	arr = re.compile('\w+').findall(row[0])
	        	filtered_words = [word for word in arr if word not in stopwords.words('english')]
	        	documents.extend(filtered_words)
	print(len(set(documents)))
	return set(documents)

def write_similar_words(fileName, model, documents):
	word_vectors = model.wv
	with open(fileName, 'w') as f, open('google_missing_vocab.txt', 'w') as g:
		f.write("Similar words to COMS4170 Repsonses according to Google Word2Vec: \n\n")
		g.write("Words missing from Google Word2Vec vocabulary: \n\n")
		m_count = 0
		for word in documents:
			if word in word_vectors:
				f.write(word)
				f.write("\n")
				f.write(str([model.most_similar(positive=[word], topn = 5)]))
			else:
				f.write("{} not in vocabulary".format(word))
				g.write("{} \n".format(word))
				m_count += 1
			f.write("\n\n")	
	print(m_count) 

#Load Google's pre-trained Word2Vec 
model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
print("model loaded.")

documents = read_documents("../COMS4170Responses.csv")
print("doc loaded.")

print("writing to file...")
write_similar_words("google_w2v_test.txt", model, documents)
# print("Does it include the stop words like \'a\', \'and\', \'the\'? %d %d %d" % ('a' in model.vocab, 'and' in model.vocab, 'the' in model.vocab))

# print(model.doesnt_match("breakfast cereal dinner lunch".split()))

# # get everything related to stuff on the bed
# w1 = ["bed",'sheet','pillow']
# w2 = ['couch']
# print(model.wv.most_similar (positive=w1,negative=w2,topn=10))

print("done")