from flask import Flask, render_template
import json_coms_categorizer

app = Flask(__name__)

@app.route('/')
def index():
	print("index")
	return render_template('coms_clusters.html')

@app.route('/recluster/', methods=['POST'])
def recluster():
	print("reclustering")
	json_coms_categorizer.run()
	return render_template('coms_clusters.html')

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0', port=3000)