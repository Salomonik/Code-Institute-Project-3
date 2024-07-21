import os
from flask import render_template

if os.path.exists("env.py"):
    import env  # noqa

from project import create_app, db

app = create_app()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host=os.environ.get("IP", "0.0.0.0"), port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("DEBUG", False))


