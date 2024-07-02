import os

if os.path.exists("env.py"):
    import env  # noqa

from project import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host=os.environ.get("IP"), port=int(os.environ.get("PORT")), debug=os.environ.get("DEBUG"))
