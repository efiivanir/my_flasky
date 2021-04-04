from datetime import datetime
import os

from flask import Flask, make_response, redirect, render_template
from flask import session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

basedir = os.path.abspath(os.path.dirname(__file__))
sql_db_path = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

app = Flask(__name__)
app.config["SECRET_KEY"] = "hard to guess string"
app.config['SQLALCHEMY_DATABASE_URI'] = sql_db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


# @app.route("/")
# def index():
#     user_agent = request.headers.get("User-Agent")
#     return "<h1>Hello World!</h1>"
#
#
# @app.route("/user/<name>")
# def user(name):
#     return "<h1>Hello, {}!</h1>".format(name)


@app.route("/aa")
def aa():
    response = make_response("<h1>This document carries a cookie!</h1>")
    response.set_cookie("answer", "42")
    return response


@app.route("/h")
def hh():
    return redirect("http://www.example.com")


def load_user(id):
    return id


# @app.route("/user/<id>")
# def get_user(id):
#     user = load_user(id)
#     if not user:
#         abort(404)
#     return "<h1>Hello, {}</h1>".format(user.name)


# @app.route("/", methods=["GET", "POST"])
# def index():
#     form = NameForm()
#     if form.validate_on_submit():
#         old_name = session.get("name")
#         if old_name is not None and old_name != form.name.data:
#             flash("Looks like you have changed your name!")
#         session["name"] = form.name.data
#         return redirect(url_for("index"))
#     return render_template(
#         "index.html",
#         form=form,
#         name=session.get("name"),
#         current_time=datetime.utcnow(),
#    )
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html',
        form=form, name=session.get('name'),
        known=session.get('known', False),
        current_time = datetime.utcnow(),
        )


@app.route("/user/<name>")
def user(name):
    return render_template("user.html", user=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("base.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
