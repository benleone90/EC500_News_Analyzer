# Source: https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
# application.py

from flask import Flask
# from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# # init SQLAlchemy so we can use it later in our models
# db = SQLAlchemy()
application = Flask(__name__)
application.secret_key = 'random_key'
db = SQLAlchemy()


def create_app():
    # init SQLAlchemy so we can use it later in our models

    # DEV = True
    # if DEV == True:
    #     application.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
    #     application.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
    #     application.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
    #     application.config['MYSQL_DB'] = 'newsanalyzer'
    # elif DEV == False:
    #     application.config['MYSQL_HOST'] = os.environ['RDS_HOSTNAME']
    #     application.config['MYSQL_USER'] = os.environ['RDS_USERNAME']
    #     application.config['MYSQL_PASSWORD'] = os.environ['RDS_PASSWORD']
    #     application.config['MYSQL_DB'] = os.environ['RDS_DB_NAME']

    application.config['SECRET_KEY'] = 'secret-key-goes-here'
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    application.config['UPLOAD_FOLDER'] = './files'

    db.init_app(application)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(application)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    application.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    application.register_blueprint(main_blueprint)
    return application



if __name__ == '__main__':
    create_app()
    application.run(debug=True)
