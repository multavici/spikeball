from app import create_app, db
from app.models import User, Post, Event, Location

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Event': Event, 'Location': Location}


if __name__ == "__main__":
    app.run(host='0.0.0.0')
