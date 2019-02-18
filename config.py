import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".flaskenv"))


class Config(object):
    SECRET_KEY = "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ["MAIL_SERVER"]
    MAIL_PORT = int(os.environ["MAIL_PORT"])
    MAIL_USE_TLS = os.environ["MAIL_USE_TLS"]
    MAIL_USERNAME = os.environ["MAIL_USERNAME"]
    MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
    ADMINS = ["noreply@spikeballgent.be"]

    POSTS_PER_PAGE = 25
