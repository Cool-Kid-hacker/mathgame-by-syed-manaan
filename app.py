from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

basedir = os.path.abspath(os.path.dirname(__file__))

# Use a public-host database when DATABASE_URL is set, with local SQLite as a fallback.
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///' + os.path.join(basedir, 'game_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    created = db.Column(db.String(120), nullable=False) # Store as ISO string
    users = db.relationship('User', backref='server', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Server {self.name} ({self.code})>'

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'created': self.created,
            'user_count': len(self.users)
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, default=0)
    color = db.Column(db.String(7), default='#0000FF') # Hex color code
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('server_id', 'name', name='unique_user_per_server'),)

    def __repr__(self):
        return f'<User {self.name} (Server: {self.server_id})>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'score': self.score,
            'color': self.color
        }

# --- API Endpoints ---

@app.route('/', methods=['GET'])
def index():
    return send_from_directory(basedir, 'PythonCarGame.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/servers', methods=['GET'])
def get_servers():
    servers = Server.query.all()
    return jsonify({s.code: s.to_dict() for s in servers})

@app.route('/api/servers/<string:server_code>', methods=['GET'])
def get_server(server_code):
    server = Server.query.filter_by(code=server_code).first()
    if not server:
        return jsonify({'message': 'Server not found'}), 404
    users_data = {u.name: u.to_dict() for u in server.users}
    return jsonify({'server': server.to_dict(), 'users': users_data})

@app.route('/api/servers', methods=['POST'])
def create_server():
    data = request.get_json()
    code = data.get('code')
    name = data.get('name')
    created = data.get('created')

    if not code or not name or not created:
        return jsonify({'message': 'Missing server code, name or creation date'}), 400

    if Server.query.filter_by(code=code).first():
        return jsonify({'message': 'Server with this code already exists'}), 409

    new_server = Server(code=code, name=name, created=created)
    db.session.add(new_server)
    db.session.commit()
    return jsonify({'message': 'Server created', 'server': new_server.to_dict()}), 201

@app.route('/api/servers/<string:server_code>', methods=['DELETE'])
def delete_server(server_code):
    server = Server.query.filter_by(code=server_code).first()
    if not server:
        return jsonify({'message': 'Server not found'}), 404
    
    if server_code == 'default':
        return jsonify({'message': 'Cannot delete default server'}), 403

    db.session.delete(server)
    db.session.commit()
    return jsonify({'message': 'Server deleted'}), 200

@app.route('/api/servers/<string:server_code>/users', methods=['GET'])
def get_server_users(server_code):
    server = Server.query.filter_by(code=server_code).first()
    if not server:
        return jsonify({'message': 'Server not found'}), 404
    users_data = {u.name: u.to_dict() for u in server.users}
    return jsonify(users_data)

@app.route('/api/servers/<string:server_code>/users', methods=['POST'])
def create_user(server_code):
    server = Server.query.filter_by(code=server_code).first()
    if not server:
        return jsonify({'message': 'Server not found'}), 404

    data = request.get_json()
    name = data.get('name')
    score = data.get('score', 0)
    color = data.get('color', '#0000FF')

    if not name:
        return jsonify({'message': 'Missing user name'}), 400

    if User.query.filter_by(server_id=server.id, name=name).first():
        return jsonify({'message': 'User with this name already exists in this server'}), 409

    new_user = User(name=name, score=score, color=color, server=server)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created', 'user': new_user.to_dict()}), 201

@app.route('/api/servers/<string:server_code>/users/<string:user_name>', methods=['PUT'])
def update_user(server_code, user_name):
    server = Server.query.filter_by(code=server_code).first()
    if not server:
        return jsonify({'message': 'Server not found'}), 404

    user = User.query.filter_by(server_id=server.id, name=user_name).first()
    if not user:
        return jsonify({'message': 'User not found in this server'}), 404

    data = request.get_json()
    
    # Handle name change
    new_name = data.get('name')
    if new_name and new_name != user_name:
        if User.query.filter_by(server_id=server.id, name=new_name).first():
            return jsonify({'message': 'New username already exists in this server'}), 409
        user.name = new_name

    # Update score and color
    user.score = data.get('score', user.score)
    user.color = data.get('color', user.color)

    db.session.commit()
    return jsonify({'message': 'User updated', 'user': user.to_dict()}), 200

@app.route('/api/servers/<string:server_code>/users/<string:user_name>', methods=['DELETE'])
def delete_user(server_code, user_name):
    server = Server.query.filter_by(code=server_code).first()
    if not server:
        return jsonify({'message': 'Server not found'}), 404

    user = User.query.filter_by(server_id=server.id, name=user_name).first()
    if not user:
        return jsonify({'message': 'User not found in this server'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200

def initialize_database():
    with app.app_context():
        db.create_all()
        if not Server.query.filter_by(code='default').first():
            default_server = Server(code='default', name='Default Server', created='initial')
            db.session.add(default_server)
            db.session.commit()

initialize_database()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
