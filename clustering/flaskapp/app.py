from flask import Flask, render_template, request
import json_coms_categorizer

app = Flask(__name__)
stop_words_list = set()
k = json_coms_categorizer.true_k
n_top_words = json_coms_categorizer.num_top_words

@app.route('/')
def index():
	stop_words_list = set()
	json_coms_categorizer.run()
	return render_template('coms_clusters.html')

@app.route('/recluster', methods=['POST'])
def recluster():
	global k
	global n_top_words
	
	inputs = dict(request.form)

	addStopwordInput = inputs['addStopword'][0]
	print("added stop word: " + addStopwordInput)
	if not addStopwordInput == "":
		stop_words_list.add(addStopwordInput)

	removeStopwordInput = inputs['removeStopword'][0]
	print("removed stop word: " + removeStopwordInput)
	if not removeStopwordInput == "":
		stop_words_list.remove(removeStopwordInput)

	if not inputs['k'][0] == "":
		k_input = int(inputs['k'][0])
		k = k_input
		print("new k: " + str(k_input))

	if not inputs['nTopWords'][0] == "":
		n_top_words_input = int(inputs['nTopWords'][0])
		n_top_words = n_top_words_input
		print("new n: " + str(n_top_words_input))

	print("list: " + str(stop_words_list))
	print(request.form['reclusterBtn'])
	if request.form['reclusterBtn'] == 'recalcDiffSeed':
		json_coms_categorizer.new_seed()
		print("RESEEDEDEDED")
	json_coms_categorizer.run(true_k=k, num_top_words=n_top_words, added_stop_word=addStopwordInput, removed_stop_word=removeStopwordInput)
	return render_template('added_stopwords.html', stop_words=stop_words_list)

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0', port=3000)