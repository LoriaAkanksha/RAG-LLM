from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, jsonify, request, session
from functools import wraps
from src.components.filters import filters
from src.components.variables import df_path
from src.components.generate import Generate_response
from src.components.qa_training import QA_training
from src.components.qa_inferences import QA_inferenece
import pandas as pd
import jwt
from datetime import datetime, timedelta, timezone
from flask_cors import CORS  
import os
import shutil
import warnings
 
warnings.filterwarnings('ignore')
 
df = pd.read_csv(df_path)
 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app)
 
db = SQLAlchemy(app)
 
filter_instance = filters(df)
 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    vector_db_path = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.String(30), default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
 
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            session['username'] = data['username']
        except:
            return jsonify({'error': 'Invalid token'}), 401
 
        return f(*args, **kwargs)
 
    return decorated
 
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
 
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        expiration_time = datetime.now(timezone.utc) + timedelta(seconds=7200)
        token_payload = {'username': username, 'exp': expiration_time}
        token = jwt.encode(token_payload, app.secret_key, algorithm='HS256')
 
        if user.is_admin:
            return jsonify({'message': 'Admin login successful', 'token': token, 'admin': True}), 200
        else:
            return jsonify({'message': 'Login successful', 'token': token, 'admin': False}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401
 
@app.route('/create_user', methods=['POST'])
def create_users():
    admin_token = request.headers.get('Authorization')
    if not admin_token:
        return jsonify({'error': 'Admin token is missing'}), 401
 
    try:
        admin_token = admin_token.split(' ')[1]  # Remove 'Bearer ' prefix
        admin_data = jwt.decode(admin_token, app.secret_key, algorithms=['HS256'])
        admin_username = admin_data['username']
        admin_user = User.query.filter_by(username=admin_username, is_admin=True).first()
        if not admin_user:
            return jsonify({'error': 'Admin authentication failed'}), 401
    except:
        return jsonify({'error': 'Invalid admin token'}), 401
 
    data = request.json
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin')  
 
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400
 
    vector_db_path = f'temp_vector_db_{username}'
    os.makedirs(vector_db_path)
 
    new_user = User(username=username, password=generate_password_hash(password), vector_db_path=vector_db_path, is_admin=is_admin)
    db.session.add(new_user)
    db.session.commit()
 
    return jsonify({'message': 'Signup successful'}), 200
 
 
@app.route('/usernames', methods=['GET'])
def get_usernames():
    admin_token = request.headers.get('Authorization')
    if not admin_token:
        return jsonify({'error': 'Admin token is missing'}), 401
    
    try:
        admin_token = admin_token.split(' ')[1]  # Remove 'Bearer ' prefix
        admin_data = jwt.decode(admin_token, app.secret_key, algorithms=['HS256'])
        admin_username = admin_data['username']
        admin_user = User.query.filter_by(username=admin_username, is_admin=True).first()
        if not admin_user:
            return jsonify({'error': 'Admin authentication failed'}), 401
    except:
        return jsonify({'error': 'Invalid admin token'}), 401
    
    users = User.query.with_entities(User.id, User.username, User.is_admin, User.created_date).all()
    user_data = [{'id': user.id,
                  'username': user.username,
                  'is_admin': user.is_admin,
                  'created_date': user.created_date} for user in users]
    return jsonify({'users': user_data}), 200
 
@app.route('/job_titles', methods=['GET'])
@token_required
def job_titles():
    try:
        job_titles = filter_instance.get_job_titles()
        return job_titles
 
    except Exception as e:
        return jsonify({'error': str(e)})
 
@app.route('/filtered_jobs', methods=['POST'])
@token_required
def filtered_jobs():
    try:
        selected_job_titles = request.json.get('selected_job_titles', [''])
        selected_countries = request.json.get('selected_countries', [''])
        selected_states = request.json.get('selected_states', [''])
        selected_cities = request.json.get('selected_cities', [''])
        selected_autho = request.json.get('selected_authorization',[''])
        selected_start_date = request.json.get('start_date','')
        selected_end_date = request.json.get('end_date','')   
        
        filteredCountries = filter_instance.get_countries_name(selected_job_titles)
        filteredStates = filter_instance.get_states_names(selected_countries)
        filteredCities = filter_instance.get_cities_names(selected_states)
        filteredAuthorizations = filter_instance.get_work_authorization(selected_cities)
        filter_instance.filter_data_authorization(selected_autho)
        start_date,end_date = filter_instance.get_date()
        filtered_data = filter_instance.get_filterd_data(selected_start_date, selected_end_date)
        output_list = filter_instance.get_output_list()
        result = {
            'countries': filteredCountries,
            'states': filteredStates,
            'cities': filteredCities,
            'authorizations': filteredAuthorizations,
            'start_date' : start_date,
            'end_date' : end_date,
            'filtered_data' : filtered_data,
            'output_list' : output_list
        }
        
        return result
 
    except Exception as e:
        return jsonify({'error': str(e)})
 
@app.route('/Generate', methods=['POST'])
@token_required
def generate_response():
    try:
        outputList = request.json.get('output_list')
        query = request.json.get('query','')
    
        Job_description = request.json.get('Job_description','')
        username = session.get('username')
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
 
        folder_path = user.vector_db_path
        
        if not query:
            if os.path.exists(folder_path):
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
 
                    if os.path.isdir(item_path) and item != 'chroma.sqlite3':
                        shutil.rmtree(item_path)
                    
            generate_instance = Generate_response(outputList)
            result, temp_docs = generate_instance.process_rag_system(Job_description)
            qa_train = QA_training(temp_docs, folder_path)
            qa_train.create_temp_vectorDB()
            
        else:
            qa_infer = QA_inferenece(query, folder_path)
            query_result = qa_infer.load_temp_vector_db()
            result = {'query_result': query_result}
        
        return jsonify(result)
                
    except Exception as e:
        return jsonify({'error': str(e)})
 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='10.20.20.67', port="5007")