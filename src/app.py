from flask import Flask , request, jsonify
from flask_pymongo import PyMongo, ObjectId
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from bson.binary import Binary 

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/VERZEL'
mongo = PyMongo(app)

# No seu código Flask
CORS(app, resources={
    r"/anuncio": {"origins": "http://localhost:3000"},
    r"/anuncios": {"origins": "http://localhost:3000"}
})


db = mongo.db.Users
db2 = mongo.db.Anuncios

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = 'caminho/para/o/seu/diretorio/de/upload'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/users', methods=['POST'])
def createUser():
        result = db.insert_one({
            'name': request.json['name'],
            'email': request.json['email'],
            'password': request.json['password']
        })

        inserted_id = str(result.inserted_id)
        print(f"User created with ID: {inserted_id}")
        return jsonify(str(ObjectId(inserted_id)))

@app.route('/users', methods=['GET'])
def getUsers():
    users = []
    for doc in db.find():
        users.append({
            '_id': str(ObjectId(doc['_id'])),
            'name': doc['name'],
            'email': doc['email'],
            'password': doc['password']
        })
    return jsonify(users)

@app.route('/user/<id>', methods=['GET'])
def getUser(id):
    user = db.find_one({'_id': ObjectId(id)})
    print(user)
    return jsonify({
        '_id': str(ObjectId(user['_id'])),
        'name': user['name'],
        'email': user['email'],
        'password': user['password']
    })

@app.route('/users/<id>', methods=['DELETE'])
def deleteUser(id):
    db.delete_one({'_id': ObjectId(id)})
    return jsonify({'msg': 'Usuario Deletado'})

@app.route('/user/<id>', methods=['PUT'])
def updateUser(id):
    db.update_one({'_id': ObjectId(id)}, {'$set': {
        'name': request.json['name'],
        'email': request.json['email'],
        'password': request.json['password']
    }})
    return jsonify({'msg': 'Usuario Updated'}), 200

@app.route('/login', methods=['POST'])
def loginUser():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = db.find_one({'email': email, 'password': password})

    if user:
        return jsonify({
            'email': user['email'],
            'password': user['password']
        })
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/anuncio', methods=['POST'])
def createAnuncio():
    try:
        modelo = request.form['modelo']
        ano = request.form['ano']
        preco = request.form['preco']
        marca = request.form['marca']
        km = request.form['km']

        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        file = request.files['file']

        if file and allowed_file(file.filename):

            image_binary = Binary(file.read())

            db2.insert_one({
                'modelo': modelo,
                'ano': ano,
                'preco': preco,
                'marca': marca,
                'km': km,
                'photo': image_binary 
            })

            return jsonify({'message': 'Anúncio criado com sucesso'}), 201
        else:
            return jsonify({'error': 'Arquivo não permitido'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/anuncios', methods=['GET'])
def getAnuncios():
    anuncios = []
    for doc in db2.find():
        anuncio = {
            '_id': str(ObjectId(doc['_id'])),
            'modelo': doc['modelo'],
            'ano': doc['ano'],
            'preco': doc['preco'],
            'marca': doc['marca'],
            'km': doc['km']
        }
        if 'filename' in doc:
            anuncio['filename'] = doc['filename']
        else:
            anuncio['filename'] = None
        anuncios.append(anuncio)

    return jsonify(anuncios)

if __name__ == "__main__":
    app.run(debug=True)
