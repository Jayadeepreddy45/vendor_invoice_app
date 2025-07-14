from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

# ✅ Required to expose CLI commands like `flask db`
from flask.cli import FlaskGroup
cli = FlaskGroup(app)

if __name__ == '__main__':
    cli()
