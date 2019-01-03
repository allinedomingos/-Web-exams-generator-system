from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField , TextAreaField, IntegerField, DateField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    nomeU = StringField('Nome do usuário', validators=[DataRequired("Este campo deve ser preenchido")])
    senha = PasswordField('Senha', validators=[DataRequired("Este campo deve ser preenchido")])
    submit = SubmitField('Entrar')


class CadastraUForm(FlaskForm):
    nomeU = StringField('Nome do usuário', validators=[DataRequired("")])
    email = StringField('E-mail', validators=[DataRequired("")])
    senha = PasswordField('Senha', validators=[DataRequired("")])
    submit = SubmitField('Cadastrar')

class CadastraDisciplina(FlaskForm):
    nome = StringField('Nome Disciplina', validators=[DataRequired("")])
    submit = SubmitField('Cadastrar')

class CadastraTema(FlaskForm):
    nomeT = StringField('Nome Tema', validators=[DataRequired("")])
    submit = SubmitField('Cadastrar')


class CadastraQuestao(FlaskForm):
    questao = TextAreaField('Questão', validators=[DataRequired("")])
    resposta = TextAreaField('Resposta', validators=[DataRequired("")])
    submit = SubmitField('Cadastrar')

