from time import strftime

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Link
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from Formulario import LoginForm, CadastraUForm, CadastraDisciplina, CadastraTema, CadastraQuestao
from datetime import date
import sqlite3

app = Flask(__name__)

SECRET_KEY = "stringAleatoria"  #proteção contra ataques
app.secret_key = SECRET_KEY

bootstrap = Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meubanco.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

nav = Nav()

nav.init_app(app)

@nav.navigation()
def menunav():
    menu = Navbar('BankQA System')
    if session.get('logged_in'):
        menu.items=[View('Home','home'),View('Minhas Disciplinas', 'disciplinas'), View('Minhas Provas', 'home'), View('Gera Provas', 'selecionadisciplina'), View('Sair','sair')]
        menu.items.append(Link('Ajuda','https://www.google.com'))
    else:
        menu.items = [View('Login','autenticar'), View('Cadastrar','cadastra')]
    return menu


class Usuarios(db.Model):
    __tablename__ = "Usuarios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nomeU = db.Column(db.String(40), index=True, unique=True)
    email = db.Column(db.String(130), index=True, unique=True)
    senha = db.Column(db.String(130))


    def __init__(self, **kwargs):
          super().__init__(**kwargs)
          self.nomeU = kwargs.pop('nomeU')
          self.email = kwargs.pop('email')
          self.senha = generate_password_hash(kwargs.pop('senha'))


    def set_password(self,senha):
        self.senha= generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha, senha)



class Disciplinas(db.Model):

    __tablename__ = "Disciplinas"
    idDisciplina = db.Column(db.Integer, primary_key=True)
    nomeD = db.Column(db.String(100))
    idUsuario = db.Column(db.Integer, db.ForeignKey("Usuarios.id"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nomeD = kwargs.pop('nomeD')
        self.idUsuario = kwargs.pop('idUsuario')


class Tema(db.Model):
        __tablename__ = "Tema"
        idTema = db.Column(db.Integer, primary_key=True)
        nomeT = db.Column(db.String(100))
        idUsuario = db.Column(db.Integer, db.ForeignKey("Usuarios.id"))
        idDisciplina = db.Column(db.Integer, db.ForeignKey("Disciplinas.idDisciplina"))


        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.nomeT = kwargs.pop('nomeT')
            self.idUsuario = kwargs.pop('idUsuario')
            self.idDisciplina = kwargs.pop('idDisciplina')


class Questao(db.Model):
        __tablename__ = "Questao"
        idQuestao = db.Column(db.Integer, primary_key=True)
        questao = db.Column(db.String(8000))
        resposta = db.Column(db.String(8000))
        idTema = db.Column(db.Integer, db.ForeignKey("Tema.idTema"))
        idUsuario = db.Column(db.Integer, db.ForeignKey("Usuarios.id"))

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.questao = kwargs.pop('questao')
            self.resposta = kwargs.pop('resposta')
            self.idTema = kwargs.pop('idTema')
            self.idUsuario = kwargs.pop('idUsuario')

class Prova(db.Model):

        __tablename__ = "Prova"
        idProva = db.Column(db.Integer, primary_key=True)
        dataprova = db.Column(db.Date)
        idDisciplina = db.Column(db.Integer,db.ForeignKey("Disciplinas.idDisciplina"))


        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.dataprova = kwargs.pop('dataprova')


class ProvaGeradas(db.Model):
    __tablename__ = "ProvaGeradas"
    idQuestao = db.Column(db.Integer, db.ForeignKey("Questao.idQuestao"), primary_key=True)
    idProva = db.Column(db.Integer, db.ForeignKey("Prova.idProva"), primary_key=True)




@app.route('/')
def home():
        return render_template('index.html',user=session.get('usuario'))


@app.route('/login', methods=['GET','POST'])
def autenticar():

    formulario = LoginForm()

    if formulario.validate_on_submit():
        #fazer autenticacao do usuario
        usuario = Usuarios.query.filter_by(nomeU=formulario.nomeU.data).first_or_404()
        if(usuario.check_password(formulario.senha.data)):
            session['logged_in'] = True
            session['usuario'] = usuario.nomeU
            session['id'] = usuario.id
            flash('Bem-vindo! {}'.format(usuario.nomeU), 'info')
            return render_template('index.html',user=session.get('usuario'))
        else:
            flash('Usuário ou senha inválidos', 'info')
    return render_template('login.html',form=formulario)



@app.route('/cadastrauser', methods=['GET','POST'])
def cadastra():

    form = CadastraUForm()
    if form.validate_on_submit():

        if Usuarios.query.filter_by(nomeU=form.nomeU.data).first() != None:
            flash('Atenção: Usuário {} já cadastrado!'.format(form.nomeU.data))
        elif Usuarios.query.filter_by(email=form.email.data).first() != None:
            flash('Atenção: Email {} já cadastrado!'.format(form.email.data))
        else:
            adiciona = Usuarios(nomeU=form.nomeU.data, email=form.email.data, senha=form.senha.data)
            db.session.add(adiciona)
            db.session.commit()
            flash('Sucesso: Usuário {} cadastrado!'.format(form.nomeU.data))
    return render_template('cadastrauser.html', form=form)


@app.route('/disciplinas', methods=['GET', 'POST'])
def disciplinas():

        usuario = Usuarios.query.filter_by(nomeU=session.get('usuario')).first_or_404()
        idUsuario = usuario.id
        lista_disciplinas = Disciplinas.query.filter_by(idUsuario=idUsuario).all()
        return render_template('disciplinas.html', disciplinas=lista_disciplinas)



@app.route('/cadastraDisciplina', methods=['GET', 'POST'])
def cadastraDisciplina():

    form = CadastraDisciplina()
    if form.validate_on_submit():
        if Disciplinas.query.filter_by(nomeD=form.nome.data,idUsuario=session['id']).first() != None:
            flash('Atenção: Disciplina {} já cadastrada!'.format(form.nome.data))
        else:
            adiciona = Disciplinas(nomeD=form.nome.data, idUsuario=session['id'])
            db.session.add(adiciona)
            db.session.commit()
            flash('Sucesso: Disciplina {} cadastrada!'.format(form.nome.data))
    return render_template('cadastraDisciplina.html', form=form)




@app.route('/tema', methods=['GET', 'POST'])
def tema():
        usuario = Usuarios.query.filter_by(nomeU=session.get('usuario')).first_or_404()
        idUsuario = usuario.id
        idDisciplina = request.args['idDisciplina']
        lista_tema = Tema.query.filter_by(idDisciplina=idDisciplina, idUsuario=idUsuario).all()
        return render_template('tema.html', title='Temas', idDisciplina=idDisciplina, tema=lista_tema)



@app.route('/cadastraTema', methods=['GET', 'POST'])
def cadastraTema():

    form = CadastraTema()

    if form.validate_on_submit():
        idDisciplina = request.args['idDisciplina']
        if Tema.query.filter_by(nomeT=form.nomeT.data, idDisciplina=idDisciplina).first() != None:
            flash('Atenção: Tema {} já cadastrada!'.format(form.nomeT.data))
        else:
            adiciona = Tema(nomeT=form.nomeT.data,idDisciplina=idDisciplina ,idUsuario=session['id'])
            db.session.add(adiciona)
            db.session.commit()
            flash('Sucesso: Tema {} cadastrada!'.format(form.nomeT.data))
    return render_template('cadastraTema.html', form=form)


@app.route('/questao', methods=['GET', 'POST'])
def questao():

    usuario = Usuarios.query.filter_by(nomeU=session.get('usuario')).first_or_404()
    idUsuario = usuario.id
    idTema = request.args['idTema']
    lista_questao = Questao.query.filter_by(idTema=idTema, idUsuario=idUsuario).all()
    return render_template('questao.html', idTema=idTema, questao=lista_questao)



@app.route('/cadastraQuestao', methods=['GET', 'POST'])
def cadastraQuestao():

    form = CadastraQuestao()

    if form.validate_on_submit():
        idTema = request.args['idTema']
        adiciona = Questao(questao=form.questao.data,resposta=form.resposta.data, idTema=idTema,idUsuario=session['id'])
        db.session.add(adiciona)
        db.session.commit()
        flash('Sucesso: Questão cadastrada!')
    return render_template('cadastraQuestao.html', form=form)

@app.route('/index')
def provas():

    usuario = Usuarios.query.filter_by(nomeU=session.get('usuario')).first_or_404()
    idUsuario = usuario.id
    lista_prova = ProvaGeradas.query.filter_by(idUsuario=idUsuario)
    return render_template('provageradas.html', idUsuario=idUsuario, provageradas=lista_prova)


@app.route('/selecionadisp', methods=['GET', 'POST'])
def selecionadisciplina():

    usuario = Usuarios.query.filter_by(nomeU=session.get('usuario')).first_or_404()
    idUsuario = usuario.id
    lista_disciplinas = Disciplinas.query.filter_by(idUsuario=idUsuario).all()
    return render_template('selecionadisp.html', disciplinas=lista_disciplinas)


@app.route('/selecionatema', methods=['GET', 'POST'])
def selecionatema():

    usuario = Usuarios.query.filter_by(nomeU=session.get('usuario')).first_or_404()
    idUsuario = usuario.id
    idDisciplina = request.args['idDisciplina']
    lista_tema = Tema.query.filter_by(idDisciplina=idDisciplina, idUsuario=idUsuario).all()
    return render_template('selecionatema.html', idDisciplina=idDisciplina, tema=lista_tema)


@app.route('/prova', methods=['GET', 'POST'])
def geraprova():

    # Get
    #idDisciplina = request.args['idDisciplina']
    #print(idDisciplina)

    # Post
    numQ = request.form['quantidade']
    datap = request.form['datamax']

    TemaIds = []

    for campo in request.form.items():
        if 'tema-' in campo[0]:
            # pegando somente o id e descartando o tema-
            idT = campo[0].split('-')[1]
            print(idT)
            TemaIds.append(idT)
            i = 0
            while i < len(TemaIds):
                id = TemaIds[i]
                print(id)
                lista_q = Questao.query.filter_by(idTema=id)
                i+=1
                return render_template('prova.html', prova=lista_q)

    data_atual = date.today()

@app.route('/minhasprovas', methods=['GET', 'POST'])
def verprovas():
    usuario = Usuarios.query.filter_by(nomeU=session.get('usuario')).first_or_404()
    idUsuario = usuario.id
    lista_p = Questao.query.join(ProvaGeradas).filter(idUsuario=idUsuario)
    for lista in lista_p:
        enunciado = Questao.query.filter_by(idQuestao=lista.idQuestao)
        return render_template('minhasprovas.html', minhasprovas=enunciado)


def adicionaProva(idDisciplina, data_atual):
    adiciona = Prova(dataprova=data_atual,idDisciplina=idDisciplina)
    db.session.add(adiciona)
    db.session.commit()

def adicionaProvaGerada(idProva,idQuestao):
    provagerada = ProvaGeradas(idQuestao=idQuestao,idProva=idProva)
    db.session.add(provagerada)
    db.session.commit()


@app.route('/logout')
def sair():

        session['logged_in'] = False
        return render_template('logout.html')


@app.errorhandler(404)
def page_not_found(e):
    '''
    Para tratar erros de páginas não encontradas - HTTP 404
    :param e:
    :return:
    '''
    return render_template('404.html'), 404


