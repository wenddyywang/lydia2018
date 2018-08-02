from flask import Flask, render_template, request
import json_coms_categorizer

app = Flask(__name__)
stop_words_list = set()

@app.route('/')
def index():
	stop_words_list = set()
	print("index")
	return render_template('coms_clusters.html')

@app.route('/recluster', methods=['POST'])
def recluster():
	inputs = dict(request.form)
	addStopwordInput = inputs['addStopword'][0]
	print("added stop word: " + addStopwordInput)
	if not addStopwordInput == "":
		stop_words_list.add(addStopwordInput)
	removeStopwordInput = inputs['removeStopword'][0]
	print("removed stop word: " + removeStopwordInput)
	if not removeStopwordInput == "":
		stop_words_list.remove(removeStopwordInput)
	print("list: " + str(stop_words_list))
	json_coms_categorizer.run(added_stop_word=addStopwordInput, removed_stop_word=removeStopwordInput)
	return render_template('coms_clusters.html', stop_words=stop_words_list)

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0', port=3000)