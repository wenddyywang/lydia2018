from flask import Flask, render_template, request
import json_coms_categorizer
import json

app = Flask(__name__)
stop_words_list = set()
true_k = json_coms_categorizer.true_k
n_top_words = json_coms_categorizer.num_top_words
counter = 0
verified_clusters = dict()

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
	inputs = dict(request.form)
	input_str = inputs['verifyBtn'][0]
	input_arr = input_str.splitlines()

	cluster_data = dict()

	top_words = list()
	for i in range(1, n_top_words + 1):
		top_words.append(input_arr[i])
	cluster_data['top_words'] = top_words

	sentences = list()
	for i in range(n_top_words + 1, len(input_arr)):
		sentences.append(input_arr[i])
	cluster_data['sentences'] = sentences

	verified_clusters[input_arr[0]] = cluster_data
	print(str(verified_clusters))

	js_data = json.dumps(verified_clusters)

	return render_template('verified_clusters.html', clusters=verified_clusters)

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0', port=3000)









