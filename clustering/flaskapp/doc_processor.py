from nltk.stem.snowball import SnowballStemmer


raw_docs = "COMS4170Summaries.txt"
documents = list()
indicator_words = list()

insights = dict()
insights['processed'] = list()
insights['remainder'] = list()

def read_documents(file_name=raw_docs):
    with open(file_name, 'r') as f:
        for line in f:
            if len(line.strip()) > 0:
                documents.append(line.strip())
        f.close()
    insights['remainder'] = documents
    return documents

def slice_insight(words):
	stemmer = SnowballStemmer("english")
	stemmed_words = [stemmer.stem(i) for i in words]
	indicator_words.extend(stemmed_words)
	for i in range(len(insights['remainder'])):
		doc = insights['remainder'][i]
		for word in indicator_words:
			if word in doc:
				insights['processed'].append(doc[doc.index(word):])
				insights['remainder'][i] = ""
				break
	insights['remainder'] = [x for x in insights['remainder'] if not x == ""]

	return insights