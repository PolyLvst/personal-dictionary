from flask import request,Flask,render_template,jsonify,redirect,url_for,jsonify
import requests
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path=join(dirname(__file__),'.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("DB_URI")
DB_NAME = os.environ.get("DB_NAME")
M_API_KEY = os.environ.get("API_KEY")
# Merriam webster dictionaries api key

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)
@app.route('/')
def index():
    bunch_of_words = list(db.words.find({},{'_id':False}))
    words = []
    for word in bunch_of_words:
        definition = word['definitions'][0]['shortdef']
        # Jadi kadang kadang data definisi dapat hanya berupa string, jadi untuk memastikan ditambahlah if argument
        if type(definition) is str:
            definition = definition  
        else:
            definition[0]
        words.append({
            'word': word['word'], # Mengakses judul atau kata saja
            'definition': definition,
        })
        if word['word'] == 'detail':
            detail = 'saved'
        else:
            detail = 'new'
    msg = request.args.get('msg')
    return render_template('index.html',saved=words,msg=msg,detail=detail)

@app.route('/detail/<keyword>')
def detail(keyword):
    status = request.args.get('status_give','new')
    api_key = M_API_KEY
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()
    if not definitions:
        # return redirect(url_for('index',msg=f'Could not find the word, you looking for. "{keyword}" does not exist'))
        return redirect(url_for('erno',word=keyword))
    if type(definitions[0]) is str:
        suggestions = ','.join(definitions)
        # return redirect(url_for('index',msg=f'Could not find the word, you looking for. Did you mean {suggestions}'))
        return redirect(url_for('erno',word=keyword,suggests=suggestions))
    return render_template('detail.html',word=keyword,definitions=definitions,status=status)

@app.route('/api/save_word',methods=['POST'])
def save_word():
    today = datetime.now().strftime('%A_%d_%m_%Y %H:%M:%S')
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')
    doc = {
        'word': word,
        'definitions': definitions,
        'date': today,
    }
    db.words.insert_one(doc)

    return jsonify({'msg':f'the word, {word}, was saved','status':'success'})

@app.route('/api/del_word',methods=['POST'])
def del_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word':word})
    db.examples.delete_many({'word':word})
    return jsonify({'msg':f'the word, {word}, was deleted successfully','status':'success'})

@app.route('/error')
def erno():
    word = request.args.get('word')
    if 'suggests' not in request.args:
        return render_template('error.html',word=word)
    else:
        suggestions = request.args.get('suggests')
        suggests = suggestions.split(',')
        return render_template('error.html',word=word,suggests=suggests)

@app.route('/api/get_ex',methods=['GET'])
def get_ex():
    word = request.args.get('word')
    example_data = db.examples.find({'word':word})
    examples = []
    for example in example_data:
        examples.append({
            'example':example.get('example'),
            'id':str(example.get('_id')),
        })
    return jsonify({'status':'success','examples':examples})

@app.route('/api/save_ex',methods=['POST'])
def save_ex():
    word = request.form.get('word')
    example = request.form.get('example')
    doc = {
        'word':word,
        'example':example,
    }
    db.examples.insert_one(doc)
    return jsonify({'status':'success','msg':f'example of the word {word}, was saved'})

@app.route('/api/del_ex',methods=['POST'])
def del_ex():
    word = request.form.get('word')
    id = request.form.get('id')
    db.examples.delete_one({'_id':ObjectId(id)})
    return jsonify({'status':'success','msg':f'example of the word {word}, was deleted'})

@app.errorhandler(404)
def page_not_found(e):
    message = 'Oops, you are not supposed to be here'
    return render_template('error.html',message=message)

# @app.route('/practice')
# def practice():
#     return render_template('practice.html')

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000,debug=True)