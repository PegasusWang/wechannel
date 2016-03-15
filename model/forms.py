#!/usr/bin/env python
# -*- coding:utf-8 -*-


"""forms of user"""


from wtforms.fields import StringField, PasswordField, BooleanField
from wtforms.validators import Required, Email, Length, DataRequired, EqualTo
from wtforms_tornado import Form


class LoginForm(Form):
    email = StringField('email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('password', validators=[Required()])
    remeber_me = BooleanField('remeber_me')


class RegisterForm(Form):
    email = StringField('email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('password', validators=[
        DataRequired(), EqualTo('password2', message='密码不匹配')])
    password2 = PasswordField('confirm password', validators=[DataRequired()])


if __name__ == '__main__':
    f = RegisterForm(dict(email="t@qq.com",
                     password="1234",
                     password2="123"))
    print(f.errors)
    print(f.validate())
    print(f.errors)
