import os

if os.path.exists("env.py"):
    import env  # noqa

from project import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host=os.environ.get("IP"), port=int(os.environ.get("PORT")), debug=os.environ.get("DEBUG"))
