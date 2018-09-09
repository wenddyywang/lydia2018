
from flask import render_template, Flask, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField

app = Flask(__name__)
app.secret_key = 'example'

class OurForm(FlaskForm):
    foo = StringField('foo')

@app.route('/')
def home():
    form = OurForm()
    return render_template('example.html', form=form)

@app.route('/something/', methods=['post'])
def something():
    form = OurForm()
    if form.validate_on_submit():
        print("this code is stupid")
        # return jsonify(data={'message': 'hello {}'.format(form.foo.data)})
        return 'hi'
    return jsonify(data=form.errors)

if __name__ == '__main__':
    app.run(debug=True)
