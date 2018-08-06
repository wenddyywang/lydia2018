from flask import Flask, render_template, request
import json_coms_categorizer

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
	if not removeStopwordInput == "":
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
	return render_template('added_stopwords.html', stop_words=stop_words_list, count=counter)

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0', port=3000)