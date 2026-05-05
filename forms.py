from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, ValidationError


class LoginForm(FlaskForm):
    email    = StringField('Email or Username', validators=[DataRequired()])
    password = PasswordField('Password',        validators=[DataRequired()])


class RegisterForm(FlaskForm):
    email    = StringField('Email',    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])

    def validate_password(self, field):
        p = field.data
        if not any(c.isupper() for c in p):
            raise ValidationError('Must contain an uppercase letter.')
        if not any(c.islower() for c in p):
            raise ValidationError('Must contain a lowercase letter.')
        if not any(c.isdigit() for c in p):
            raise ValidationError('Must contain a number.')

    def validate_email(self, field):
        # Imported here to avoid circular import at module load time
        from models import User
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')
