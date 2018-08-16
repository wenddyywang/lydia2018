from flask import Flask, render_template, request
import json_coms_categorizer
import json
from flask_wtf import FlaskForm
from wtforms import StringField


app = Flask(__name__)
stop_words_list = set()
true_k = json_coms_categorizer.true_k
n_top_words = json_coms_categorizer.num_top_words
counter = 0

@app.route('/')
def index():
	stop_words_list = set()
	json_coms_categorizer.run()
	return render_template('coms_clusters.html', count=counter)

@app.route('/recluster/<int:counter>', methods=['POST'])
def recluster(counter):
	global true_k
	global n_top_words

	counter += 1
	inputs = dict(request.form)

	addStopwordInput = inputs['addStopword'][0]
	print("added stop word: " + addStopwordInput)
	if not addStopwordInput == "":
		stop_words_list.add(addStopwordInput)

	removeStopwordInput = inputs['removeStopword'][0]
	print("removed stop word: " + removeStopwordInput)
	if not removeStopwordInput == "" and removeStopwordInput in stop_words_list:
		stop_words_list.remove(removeStopwordInput)

	if not inputs['k'][0] == "":
		k_input = int(inputs['k'][0])
		true_k = k_input
		print("new k: " + str(true_k))

	if not inputs['nTopWords'][0] == "":
		n_top_words_input = int(inputs['nTopWords'][0])
		n_top_words = n_top_words_input
		print("new n: " + str(n_top_words))

	print("list: " + str(stop_words_list))
	print(request.form['reclusterBtn'])
	if request.form['reclusterBtn'] == 'recalcDiffSeed':
		json_coms_categorizer.new_seed()
		print("RESEEDEDEDED")
	json_coms_categorizer.run(k=true_k, n=n_top_words, added_stop_word=addStopwordInput, removed_stop_word=removeStopwordInput)
	return render_template('coms_clusters.html', stop_words=stop_words_list, count=counter)

# @app.route('/verified', methods=['POST'])
# def verified():
# 	print(request.form.getlist('verifyCheck'))
# 	print("verified")
# 	return render_template('verified_clusters.html')

@app.route('/verified', methods=['POST'])
def verified():
	print("verified:")
	verified_clusters = dict()
	inputs = dict(request.form)
	if len(inputs) > 1:
		inputs.pop('verifyBtn', None)
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
			print(data_arr[0])

		# input_str = inputs['verifyBtn'][0]
		# print(input_str)
		# input_arr = input_str.splitlines()

		# cluster_data = dict()

		# top_words = list()
		# for i in range(1, n_top_words + 1):
		# 	top_words.append(input_arr[i])
		# cluster_data['top_words'] = top_words

		# sentences = list()
		# for i in range(n_top_words + 1, len(input_arr)):
		# 	sentences.append(input_arr[i])
		# cluster_data['sentences'] = sentences

		# verified_clusters[input_arr[0]] = cluster_data
		# return render_template('coms_clusters.html', count=counter)

	return render_template('verified_clusters.html', clusters=verified_clusters)

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0', port=3000)









