import os
import sqlite3
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, text

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photos.db'
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

DATABASE = os.path.join(os.path.dirname(__file__), 'photos.db')
CORS(app)

def get_db():
    """Establece la conexión con la base de datos y la reutiliza en cada petición"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.route('/', methods=['GET'])
def test_connection():
    connection = False
    if get_db:
        connection = True

    response = {
        'message': 'Conexión exitosa',
        'db_connection': connection
        }
    
    return jsonify(response)

@app.route('/galleries', methods=['GET'])
def get_all_galleries():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
                    SELECT 
                        galleries.id AS gallery_id,
                        galleries.name AS gallery_name,
                        photos.url AS cover_photo_url
                    FROM 
                        galleries
                    JOIN 
                        photos ON photos.id = galleries.photo_id;
                       ''')
        # Convertimos cada registro en un diccionario con las keys esperadas
        galleries = [
            {
                'gallery_id': row[0],
                'gallery_name': row[1], 
                'cover_photo_url': row[2]
            }  
            for row in cursor.fetchall()
        ]
        
        return jsonify(galleries)
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # 500 para indicar error de servidor interno

@app.route('/carrousel', methods=['GET'])
def get_carrousel_images():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
                    SELECT 
                        PHOTOS.id AS photo_id,
                        PHOTOS.url AS photo_url,
                        PHOTOS.carrousel AS photo_carrousel,
                        GALLERIES.name AS gallery_name
                    FROM 
                        PHOTOS
                    JOIN 
                        GALLERIES ON PHOTOS.gallery_id = GALLERIES.id
                    WHERE
                        PHOTOS.carrousel = 1;
                       ''')

        # Almacena los resultados de fetchall() en una variable y úsala
        rows = cursor.fetchall()

        # Crear la lista con los resultados
        carrousel_images = [
            {
                'photo_id': row[0],
                'photo_url': row[1],
                'photo_carousel': row[2],
                'gallery_name': row[3]
            }
            for row in rows
        ]
        
        return jsonify(carrousel_images)
    except Exception as e:
        return jsonify({'error': 'Error al obtener imagenes del carrousel', 'details': str(e)}), 500

@app.route('/all_photos', methods=['GET'])
def get_all_photos():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM photos;')
        
        respuesta = cursor.fetchall()
        # print("Respuesta completa:", respuesta)

        
        for row in respuesta:
            print('entrando al loop')
            # print(row)
        
        # Convertimos cada registro en un diccionario con las keys esperadas
        photos = [
            {
                'id': row[0],
                'url': row[1],
                'carrousel': row[2],
                'gallery_id': row[3]
            }
            for row in respuesta
            
        ]
        
        return jsonify(photos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # 500 para indicar error de servidor interno

@app.route('/photos_from_<gallery_name>', methods=['GET'])
def get_photos_from_gallery(gallery_name):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(f'''
                        SELECT
                            GALLERIES.photo_id,
                            PHOTOS.id,
                            PHOTOS.url
                        FROM
                            PHOTOS
                        JOIN
                            GALLERIES ON PHOTOS.gallery_id = GALLERIES.id
                        WHERE
                            GALLERIES.name = "{gallery_name}";
                        ''')
        
        respuesta = cursor.fetchall()
        # print("Respuesta completa:", respuesta)
        
        return_json = {"cover_photo": respuesta[0][2]}

        # Convertimos cada registro en un diccionario con las keys esperadas
        photos = [
            {
                'photo_id': row[1],
                'photo_url': row[2]
            }
            for row in respuesta
        ]
        
        return_json['gallery_photos'] = photos
        
        return jsonify(return_json)
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # 500 para indicar error de servidor interno


if __name__ == '__main__':
    app.run(debug=True)