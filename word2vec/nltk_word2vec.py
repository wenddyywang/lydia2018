import gensim
import nltk 
from nltk.data import find
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
	return set(documents)

def write_similar_words(fileName, model, documents):
	word_vectors = model.wv
	with open(fileName, 'w') as f, open('nltk_missing_vocab.txt', 'w') as g:
		f.write("Similar words to COMS4170 Repsonses according to nltk Word2Vec: \n\n")
		g.write("Words missing from nltk Word2Vec vocabulary: \n\n")
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

word2vec_sample = str(find('models/word2vec_sample/pruned.word2vec.txt'))
model = gensim.models.KeyedVectors.load_word2vec_format(word2vec_sample, binary=False)

print("writing to file...")

write_similar_words("nltk_w2v_test.txt", model, documents)



# print(len(model.vocab))





# print(model.most_similar(positive=['internship'], topn = 5))