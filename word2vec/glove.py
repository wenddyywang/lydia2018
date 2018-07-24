#IF WANT TO RERUN, MUST GET GLOVE VECTORS FIRST
#UNCOMMENT LINE 43

#from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.models.keyedvectors import KeyedVectors
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
	        	filtered_words = [word.lower() for word in arr if word not in stopwords.words('english')]
	        	documents.extend(filtered_words)
	return set(documents)

def write_similar_words(fileName, model, documents):
	word_vectors = model.wv
	with open(fileName, 'w') as f, open('glove_missing_vocab.txt', 'w') as g:
		f.write("Similar words to COMS4170 Repsonses according to glove Word2Vec: \n\n")
		g.write("Words missing from glove Word2Vec vocabulary: \n\n")
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

documents = read_documents("../clustering/COMS4170Responses.csv")
print("doc loaded.")

#transformed GloVe vectors to word2vec vectors
#glove2word2vec(glove_input_file="glove.42B.300d.txt", word2vec_output_file="gensim_glove_vectors.txt")
glove_model = KeyedVectors.load_word2vec_format("gensim_glove_vectors.txt", binary=False)
print("model loaded.")

print("writing to file...")
write_similar_words("glove_test.txt",glove_model, documents)

print("done.")





