import json
import os

from app import Server, User, db


def color_to_hex(color):
    if isinstance(color, str):
        return color
    if isinstance(color, list) and len(color) >= 3:
        return '#{:02X}{:02X}{:02X}'.format(*color[:3])
    return '#0000FF'


def import_users(path='users.json', server_code='default'):
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    with open(path, 'r', encoding='utf-8') as file:
        old_users = json.load(file)

    server = Server.query.filter_by(code=server_code).first()
    if not server:
        server = Server(code=server_code, name='Default Server', created='initial')
        db.session.add(server)
        db.session.flush()

    for name, data in old_users.items():
        user = User.query.filter_by(server_id=server.id, name=name).first()
        if not user:
            user = User(name=name, server=server)
            db.session.add(user)

        user.score = int(data.get('score', 0))
        user.color = color_to_hex(data.get('color'))

    db.session.commit()
    print(f'Imported {len(old_users)} users into server "{server_code}".')


if __name__ == '__main__':
    from app import app

    with app.app_context():
        import_users()
