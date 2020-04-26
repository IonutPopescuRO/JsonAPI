from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, SubmitField, validators
from wtforms.validators import Email, InputRequired


class Config(object):
    DEBUG = True

    SECRET_KEY = 'jsonapi2020'

    # Configuratie SMTP pentru trimiterea unui mail (contul de email va fi accesibil pe parcursul proiectului)
    MAIL_SERVER = 'mail.ionut.work'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = MAIL_DEFAULT_SENDER = 'json_api@ionut.work'
    MAIL_PASSWORD = 'xiVkWNlWog'

    # Configuratie Google reCaptcha (pentru inregistrare key)
    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = '6LfRBngUAAAAAIRaSVLXc6LfAMaESzhc5fuEdHmJ'
    RECAPTCHA_PRIVATE_KEY = '6LfRBngUAAAAABbGfo_iWeD4LW0EgrLV3Csi3MtI'
    RECAPTCHA_OPTIONS = {'theme': 'light'}


class RegisterForm(FlaskForm):
    email = StringField(
        'Email Address', validators=[
            Email("Invalid E-mail Address"),
            InputRequired("This field is required.")
            ])

    recaptcha = RecaptchaField("Are you real?")
    submit = SubmitField('Generează-mi un key')