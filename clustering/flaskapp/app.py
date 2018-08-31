from flask import Flask, render_template, request, jsonify
import json_coms_categorizer
import json
from flask_wtf import FlaskForm
from wtforms import StringField


app = Flask(__name__)
stop_words_list = set()
true_k = json_coms_categorizer.true_k
n_top_words = json_coms_categorizer.num_top_words
home_clusters = dict()

@app.route('/', methods=['GET', 'POST'])
def index():
	global home_clusters

	stop_words_list = set()
	if not home_clusters:
		home_clusters = json_coms_categorizer.run()
	return render_template('coms_clusters.html', clusters=home_clusters)

# @app.route('/test', methods=['GET', 'POST'])
# def test():
# 	global true_k
# 	global n_top_words

# 	inputs = dict(request.form)

# 	new_stop_word = inputs['addStopword']
# 	new_k = inputs['k']

# 	return json.dumps({'status':'OK','stop_word': new_stop_word,'k':new_k})

@app.route('/recluster', methods=['POST'])
def recluster():
	global true_k
	global n_top_words

	inputs = dict(request.form)
	clusters = dict()
	docs = inputs['docs']

	print(inputs)
	addStopwordInput = inputs['addStopword'][0]
	if not addStopwordInput == "":
		print("added stop word: " + addStopwordInput)
		stop_words_list.add(addStopwordInput)

	removeStopwordInput = inputs['removeStopword'][0]
	if not removeStopwordInput == "" and removeStopwordInput in stop_words_list:
		print("removed stop word: " + removeStopwordInput)
		stop_words_list.remove(removeStopwordInput)

	if not inputs['k'][0] == "":
		k_input = int(inputs['k'][0])
		true_k = k_input
		print("new k: " + str(true_k))

	if not inputs['nTopWords'][0] == "":
		n_top_words_input = int(inputs['nTopWords'][0])
		n_top_words = n_top_words_input
		print("new n: " + str(n_top_words))


	# if 'reclusterBtn' in request.form:
	# 	if request.form['reclusterBtn'] == 'recalcDiffSeed':
	# 		json_coms_categorizer.new_seed()
	# 	clusters = json_coms_categorizer.run(k=true_k, n=n_top_words, added_stop_word=addStopwordInput, removed_stop_word=removeStopwordInput)
	# elif 'reclusterBadBtn' in request.form:
	# 	json_coms_categorizer.new_seed()
	# 	doc_str = request.form['reclusterBadBtn']
	# 	docs = list(doc_str.splitlines())
	# 	temp_k = true_k
	# 	while len(docs) <= temp_k*3 and temp_k > 1:
	# 		temp_k -= 1
			# if temp_k == 0:
			# 	return render_template('coms_clusters.html', alert='Too few documents to cluster.')
		# clusters = json_coms_categorizer.run(doc_source=docs, k=temp_k, n=n_top_words, added_stop_word=addStopwordInput, removed_stop_word=removeStopwordInput)

	# return render_template('coms_clusters.html', clusters=clusters, stop_words=stop_words_list)
	clusters = json_coms_categorizer.run(doc_source=docs, k=true_k, n=n_top_words, added_stop_word=addStopwordInput, removed_stop_word=removeStopwordInput)

	return json.dumps(clusters)

@app.route('/reclusterNewSeed', methods=['POST'])
def recluster_new_seed():
	global true_k
	global n_top_words

	inputs = dict(request.form)
	clusters = dict()
	docs = inputs['docs']

	print(inputs)
	addStopwordInput = inputs['addStopword'][0]
	if not addStopwordInput == "":
		print("added stop word: " + addStopwordInput)
		stop_words_list.add(addStopwordInput)

	removeStopwordInput = inputs['removeStopword'][0]
	if not removeStopwordInput == "" and removeStopwordInput in stop_words_list:
		print("removed stop word: " + removeStopwordInput)
		stop_words_list.remove(removeStopwordInput)

	if not inputs['k'][0] == "":
		k_input = int(inputs['k'][0])
		true_k = k_input
		print("new k: " + str(true_k))

	if not inputs['nTopWords'][0] == "":
		n_top_words_input = int(inputs['nTopWords'][0])
		n_top_words = n_top_words_input
		print("new n: " + str(n_top_words))

	json_coms_categorizer.new_seed()
	clusters = json_coms_categorizer.run(doc_source=docs, k=true_k, n=n_top_words, added_stop_word=addStopwordInput, removed_stop_word=removeStopwordInput)

	return json.dumps(clusters)

@app.route('/recluster_valid', methods=['POST'])
def recluster_valid():
	global true_k
	global n_top_words

	inputs = dict(request.form)
	v_n_top_words = n_top_words
	docs = inputs['docs']
	v_k = int(inputs['numClusters'][0])

	warning = ""

	addStopwordInput = inputs['addStopword'][0]
	if not addStopwordInput == "":
		print("added stop word: " + addStopwordInput)
		stop_words_list.add(addStopwordInput)

	removeStopwordInput = inputs['removeStopword'][0]
	if not removeStopwordInput == "" and removeStopwordInput in stop_words_list:
		print("removed stop word: " + removeStopwordInput)
		stop_words_list.remove(removeStopwordInput)

	if not inputs['k'][0] == "":
		k_input = int(inputs['k'][0])
		if k_input > len(docs):
			warning = "Number of clusters must be less than total number of documents."
		else:
			v_k = k_input
			print("new k: " + str(true_k))

	if not inputs['nTopWords'][0] == "":
		n_top_words_input = int(inputs['nTopWords'][0])
		v_n_top_words = n_top_words_input
		print("new n: " + str(v_n_top_words))

	print("list: " + str(stop_words_list))

	if 'reclusterBtn' in request.form:
		if request.form['reclusterBtn'] == 'recalcDiffSeed':
			json_coms_categorizer.new_seed()
		clusters = json_coms_categorizer.run(doc_source=docs, k=v_k, n=v_n_top_words, added_stop_word=addStopwordInput, removed_stop_word=removeStopwordInput)

		recalculated_clusters = dict();

		clusters.pop('Document count', None)
		for cluster in clusters:
			cluster_dict = clusters[cluster]
			word_counter = 1
			words_list = list()
			sentence_list = list()
			for d in cluster_dict:
				one_word = ""
				one_sentence = ""
				for key, val in d.items():
					if key == 'word':
						one_word += str(word_counter) + ". <b>" + val + "</b> "
						word_counter += 1
					elif key == 'word_weight':
						one_word += "(" + val + ") <br>"
						words_list.append(one_word)
						one_word = ""
					elif key == 'sentence':
						one_sentence += val
					elif key == 'sent_weight':
						one_sentence += " (" + val + ')'
						sentence_list.append(one_sentence)
						one_sentence = ""
			sub_dict = dict()
			sub_dict['top_words'] = words_list
			sub_dict['sentences'] = sentence_list
			recalculated_clusters[cluster] = sub_dict
	if warning:
		return render_template('verified_clusters.html', clusters=recalculated_clusters, stop_words=stop_words_list, alert=warning)
	else:
		return render_template('verified_clusters.html', clusters=recalculated_clusters, stop_words=stop_words_list)

@app.route('/recluster_invalid', methods=['POST'])
def recluster_invalid():
	global true_k
	global n_top_words

	inputs = dict(request.form)
	new_n_top_words = n_top_words
	numDocs = int(inputs['numDocs'][0])
	if numDocs < true_k:
		temp_k = numDocs
	else:
		temp_k = true_k

	docs = inputs['docs']

	warning = ""

	addStopwordInput = inputs['addStopword'][0]
	if not addStopwordInput == "":
		print("added stop word: " + addStopwordInput)
		stop_words_list.add(addStopwordInput)

	removeStopwordInput = inputs['removeStopword'][0]
	if not removeStopwordInput == "" and removeStopwordInput in stop_words_list:
		print("removed stop word: " + removeStopwordInput)
		stop_words_list.remove(removeStopwordInput)

	if not inputs['k'][0] == "":
		k_input = int(inputs['k'][0])
		if k_input > len(docs):
			warning = "Number of clusters must be less than total number of documents."
		else:
			temp_k = k_input
			true_k = temp_k
			print("new k: " + str(temp_k))

	if not inputs['nTopWords'][0] == "":
		n_top_words_input = int(inputs['nTopWords'][0])
		print("new n: " + str(n_top_words))

	print("list: " + str(stop_words_list))

	if 'reclusterBtn' in request.form:
		if request.form['reclusterBtn'] == 'recalcDiffSeed':
			json_coms_categorizer.new_seed()

		# while len(docs) <= temp_k*3:
		# 	temp_k -= 1
		# 	if temp_k == 0:
		# 		return render_template('coms_clusters.html', alert='Too few documents to cluster.')
		clusters = json_coms_categorizer.run(doc_source=docs, k=temp_k, n=n_top_words, added_stop_word=addStopwordInput, removed_stop_word=removeStopwordInput)

	# return render_template('invalid_clusters.html', clusters=clusters, stop_words=stop_words_list)

		recalculated_clusters = dict();

		clusters.pop('Document count', None)
		for cluster in clusters:
			cluster_dict = clusters[cluster]
			word_counter = 1
			words_list = list()
			sentence_list = list()
			for d in cluster_dict:
				one_word = ""
				one_sentence = ""
				for key, val in d.items():
					if key == 'word':
						one_word += str(word_counter) + ". <b>" + val + "</b> "
						word_counter += 1
					elif key == 'word_weight':
						one_word += "(" + val + ") <br>"
						words_list.append(one_word)
						one_word = ""
					elif key == 'sentence':
						one_sentence += val
					elif key == 'sent_weight':
						one_sentence += " (" + val + ')'
						sentence_list.append(one_sentence)
						one_sentence = ""
			sub_dict = dict()
			sub_dict['top_words'] = words_list
			sub_dict['sentences'] = sentence_list
			recalculated_clusters[cluster] = sub_dict

	if warning:
		return render_template('invalid_clusters.html', alert=warning, clusters=recalculated_clusters, stop_words=stop_words_list)
	else:
		return render_template('invalid_clusters.html', clusters=recalculated_clusters, stop_words=stop_words_list)

@app.route('/verified', methods=['POST'])
def verified():
	verified_clusters = dict()
	inputs = dict(request.form)

	for key, value in inputs.items():
		data_str = value[0]
		data_arr = data_str.splitlines()

		cluster_data = dict()

		top_words = list()
		for i in range(1, n_top_words + 1):
			top_words.append(data_arr[i])
		cluster_data['top_words'] = top_words

		sentences = list()
		for i in range(n_top_words + 1, len(data_arr)):
			sentences.append(data_arr[i])
		cluster_data['sentences'] = sentences

		verified_clusters[data_arr[0]] = cluster_data

	print(verified_clusters)

	return json.dumps(verified_clusters)

@app.route('/invalids', methods=['POST'])
def invalids():
	invalid_docs = set()
	inputs = dict(request.form)
	for cluster, doc_list in inputs.items():
		for doc in doc_list:
			invalid_docs.add(doc)

	invalid_json = dict()
	invalid_json[str(len(invalid_docs)) + ' docs'] = list(invalid_docs)
	print(invalid_json)
	# inputs = dict(request.form)
	# if len(inputs) > 1:
	# 	inputs.pop('verifyBtn', None)
	# 	for key, value in inputs.items():
	# 		data_str = value[0]
	# 		data_arr = data_str.splitlines()

	# 		cluster_data = dict()

	# 		top_words = list()
	# 		for i in range(1, n_top_words + 1):
	# 			top_words.append(data_arr[i])
	# 		cluster_data['top_words'] = top_words

	# 		sentences = list()
	# 		for i in range(n_top_words + 1, len(data_arr)):
	# 			sentences.append(data_arr[i])
	# 		cluster_data['sentences'] = sentences

	# 		verified_clusters[data_arr[0]] = cluster_data

	# return render_template('invalid_docs.html', data=invalid_json)
	return json.dumps(invalid_json)

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0', port=5000)









