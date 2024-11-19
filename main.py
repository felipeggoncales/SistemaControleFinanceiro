from flask import Flask, render_template, request, flash, url_for, redirect, get_flashed_messages, session
from datetime import datetime
import fdb
import re
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

app = Flask(__name__)
app.secret_key = 'logisticBanco'

host = 'localhost'
database = r'C:\Users\felip\OneDrive\Documentos\GitHub\SistemaControleFinanceiro\BANCO.FDB'
user = 'SYSDBA'
password = 'sysdba'
con = fdb.connect(host=host, database=database, user=user, password=password)

contagem = 0;

def limpar_flash():
    get_flashed_messages()

class Usuario:
    def __init__(self, id_usuario, nome, sobrenome, email, senha):
        self.id_usuario = id_usuario
        self.nome = nome
        self.sobrenome = sobrenome
        self.email = email
        self.senha = senha


class Receitas:
    def __init__(self, id_receita, id_usuario, valor, data, fonte):
        self.id_receita = id_receita
        self.id_usuario = id_usuario
        self.valor = valor
        self.data = data
        self.fonte = fonte


class Despesas:
    def __init__(self, id_despesa, id_usuario, valor, data, fonte):
        self.id_despesa = id_despesa
        self.id_usuario = id_usuario
        self.valor = valor
        self.data = data
        self.fonte = fonte


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/abrirUsuario')
def abrirUsuario():
    return render_template('cadastro.html', titulo='Novo usuario')

@app.route('/abrirDespesa')
def abrirDespesa():
    return render_template('adicionarDespesa.html', titulo='Nova despesa')

@app.route('/abrirReceita')
def abrirReceita():
    return render_template('adicionarReceita.html', titulo='Nova receita')

@app.route('/historico')
def historico():
    mes = request.args.get('mes', None)
    ano = request.args.get('ano', None)

    if mes == None:
        mes = session.get('mes')

    if ano == None:
        ano = session.get('ano')

    session['mes'] = mes
    session['ano'] = ano

    mensagem = None
    if mes and ano:
        mes_convertido = datetime.strptime(mes, "%m").strftime("%b")
        mensagem = 'em '+datetime.strptime(mes, "%m").strftime("%B")
    else:
        mes_convertido = None
        mensagem = 'nos últimos 30 dias'

    despesas = 0
    receitas = 0

    cursor = con.cursor()
    if mes and ano:
        cursor.execute('''
            SELECT VALOR FROM DESPESAS 
            WHERE (ID_USUARIO = ?) AND (EXTRACT(MONTH FROM DATA) = ?) AND (EXTRACT(YEAR FROM DATA) = ?)
        ''', (session.get('id_usuario'), mes, ano))
    else:
        cursor.execute('''
            SELECT VALOR FROM DESPESAS 
            WHERE (ID_USUARIO = ?) AND (DATA BETWEEN (CURRENT_DATE - 30) AND CURRENT_DATE)
        ''', (session.get('id_usuario'),))
        
    for valor in cursor.fetchall():
        despesas += valor[0]
    cursor.close()

    cursor = con.cursor()
    if mes and ano:
        cursor.execute('''
            SELECT VALOR FROM RECEITAS 
            WHERE ID_USUARIO = ? AND EXTRACT(MONTH FROM DATA) = ? AND EXTRACT(YEAR FROM DATA) = ?
        ''', (session.get('id_usuario'), mes, ano))
    else:
        cursor.execute('''
            SELECT VALOR FROM RECEITAS 
            WHERE ID_USUARIO = ? AND (DATA BETWEEN CURRENT_DATE - 30 AND CURRENT_DATE)
        ''', (session.get('id_usuario'),))
    for valor in cursor.fetchall():
        receitas += valor[0]
    cursor.close()

    return render_template('historico.html', despesas=despesas, receitas=receitas, mes=mes_convertido, ano=ano, mensagem=mensagem)

@app.route('/historicoReceita')
def historicoReceita():
    mes = request.args.get('mes', None)
    ano = request.args.get('ano', None)

    if mes == None:
        mes = session.get('mes')

    if ano == None:
        ano = session.get('ano')

    session['mes'] = mes
    session['ano'] = ano

    if mes and ano:
        mes_convertido = datetime.strptime(mes, "%m").strftime("%b")
    else:
        mes_convertido = None

    cursor = con.cursor()
    if mes and ano:
        cursor.execute('''
            SELECT id_receita, valor, data, fonte FROM RECEITAS WHERE ID_USUARIO = ? 
            AND EXTRACT(MONTH FROM DATA) = ? AND EXTRACT(YEAR FROM DATA) = ? ORDER BY data DESC
        ''', (session.get('id_usuario'), mes, ano))
    else:
        cursor.execute('''
            SELECT id_receita, valor, data, fonte FROM RECEITAS 
            WHERE (ID_USUARIO = ?) AND (DATA BETWEEN (CURRENT_DATE - 30) AND CURRENT_DATE)
        ''', (session.get('id_usuario'),))

    receitas = cursor.fetchall()
    cursor.close()

    return render_template('historicoReceita.html', receitas=receitas, mes=mes_convertido, ano=ano)


@app.route('/historicoDespesas')
def historicoDespesas():
    mes = request.args.get('mes', None)
    ano = request.args.get('ano', None)

    if mes == None:
        mes = session.get('mes')

    if ano == None:
        ano = session.get('ano')

    session['mes'] = mes
    session['ano'] = ano

    if mes and ano:
        mes_convertido = datetime.strptime(mes, "%m").strftime("%b")
    else:
        mes_convertido = None

    cursor = con.cursor()
    if mes and ano:
        cursor.execute('''
            SELECT id_despesa, valor, data, fonte FROM DESPESAS WHERE ID_USUARIO = ? 
            AND EXTRACT(MONTH FROM DATA) = ? AND EXTRACT(YEAR FROM DATA) = ? ORDER BY data DESC
        ''', (session.get('id_usuario'), mes, ano))
    else:
        cursor.execute('''
            SELECT id_despesa, valor, data, fonte FROM DESPESAS 
            WHERE (ID_USUARIO = ?) AND (DATA BETWEEN (CURRENT_DATE - 30) AND CURRENT_DATE)
        ''', (session.get('id_usuario'),))

    despesas = cursor.fetchall()
    cursor.close()

    return render_template('historicoDespesas.html', despesas=despesas, mes=mes_convertido, ano=ano)

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()
    cursor.execute("SELECT id_usuario, email, senha FROM USUARIO WHERE email = ?", (email,))
    usuario = cursor.fetchone()

    if usuario and usuario[2] == senha:
        limpar_flash()
        flash('Login realizado com sucesso', 'success')
        session['id_usuario'] = usuario[0]
        cursor.execute("SELECT nome, sobrenome FROM USUARIO WHERE email = ?", (email,))
        resultado = cursor.fetchone()
        cursor.close()
        if resultado:
            nome, sobrenome = resultado
            session['nome'] = nome
            session['sobrenome'] = sobrenome
            return redirect(url_for('home'))
    else:
        limpar_flash()
        flash('E-mail ou senha incorretos', 'error')
        cursor.close()
        return redirect(url_for('index'))
    
@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')
    
@app.route('/addUsuario', methods=['POST'])
def addUsuario():
    nome = request.form['nome']
    sobrenome = request.form['sobrenome']
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT 1 FROM USUARIO WHERE email = ?', (email,))
        if cursor.fetchone():
            limpar_flash()
            flash('Email já cadastrado.', 'error')
            return redirect(url_for('abrirUsuario'))
        if not re.fullmatch(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$', senha):
            limpar_flash()
            flash('A senha deve ter ao menos 8 caracteres, uma letra maiúscula, um número e um caractere especial.',
                  'error')
            return redirect(url_for('abrirUsuario'))
        cursor.execute("INSERT INTO USUARIO (nome, sobrenome, email, senha) VALUES (?, ?, ?, ?)",
                       (nome, sobrenome, email, senha))
        con.commit()
        limpar_flash()
        flash('Sua conta foi cadastrada com sucesso.', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        limpar_flash()
        flash(f'Erro ao cadastrar a conta: {e}', 'error')
        return redirect(url_for('abrirUsuario'))
    finally:
        cursor.close()


@app.route('/home')
def home():
    despesas = 0
    receitas = 0

    cursor = con.cursor()
    cursor.execute('SELECT VALOR FROM DESPESAS WHERE ID_USUARIO = ?', (session.get('id_usuario'),))
    for valor in cursor.fetchall():
        despesas += valor[0]
    cursor.close()

    cursor = con.cursor()
    cursor.execute('SELECT VALOR FROM RECEITAS WHERE ID_USUARIO = ?', (session.get('id_usuario'),))
    for valor in cursor.fetchall():
        receitas += valor[0]
    cursor.close()

    return render_template('home.html', despesas=despesas, receitas=receitas)

@app.route('/addDespesa', methods=['POST'])
def addDespesa():
    if request.method == 'POST':
        try:
            valor = float(request.form['valor'])
            data = request.form['data']
            fonte = request.form['fonte']

            if valor <= 0:
                limpar_flash()
                flash('Coloque um valor maior que 0', 'error')
            else:
                cursor = con.cursor()
                cursor.execute("INSERT INTO DESPESAS (id_usuario, valor, data, fonte) VALUES (?, ?, ?, ?)",
                               (session.get('id_usuario'), valor, data, fonte))
                con.commit()
                cursor.close()
                limpar_flash()
                flash('Sua despesa foi adicionada com sucesso!', 'success')
        except ValueError:
            limpar_flash()
            flash('O valor informado não é válido. Por favor, insira um número válido.', 'error')

        return redirect(url_for('home'))
    
@app.route('/addReceita', methods=['POST'])
def addReceita():
    if request.method == 'POST':
        try:
            valor = float(request.form['valor'])
            data = request.form['data']
            fonte = request.form['fonte']

            if valor <= 0:
                limpar_flash()
                flash('Coloque um valor maior que 0', 'error')
            else:
                cursor = con.cursor()
                cursor.execute("INSERT INTO RECEITAS (id_usuario, valor, data, fonte) VALUES (?, ?, ?, ?)",
                               (session.get('id_usuario'), valor, data, fonte))
                con.commit()
                cursor.close()
                limpar_flash()
                flash('Sua receita foi adicionada com sucesso', 'success')
        except ValueError:
            limpar_flash()
            flash('O valor informado não é válido. Por favor, insira um número válido.', 'error')

        return redirect(url_for('home'))

@app.route('/editar/<int:id>/<tipo>')
def editar(id, tipo):
    cursor = con.cursor()
    if tipo == 'receita':
        cursor.execute('SELECT id_receita, valor, data, fonte FROM RECEITAS WHERE id_receita = ?', (id,))
    elif tipo == 'despesa':
        cursor.execute('SELECT id_despesa, valor, data, fonte FROM DESPESAS WHERE id_despesa = ?', (id,))

    mensagem = cursor.fetchone()
    cursor.close()
    return render_template('editar.html', mensagem=mensagem, receitaOuDespesa=tipo)

@app.route('/excluir/<int:id>/<tipo>')
def excluir(id,tipo):
    cursor = con.cursor()
    if tipo == 'receita':
        cursor.execute('DELETE FROM RECEITAS WHERE ID_RECEITA = ?', (id,))
        con.commit()
        cursor.close()
        return redirect(url_for('historicoReceita'))
    elif tipo == 'despesa':
        cursor.execute('DELETE FROM DESPESAS WHERE ID_DESPESA = ?', (id,))
        con.commit()
        cursor.close()
        return redirect(url_for('historicoDespesas'))
    
@app.route('/salvarAlteracoes/<int:id>/<tipo>', methods=['POST'])
def salvarAlteracoes(id,tipo):
    cursor = con.cursor()
    newFonte = request.form['fonte']
    newData = request.form['data']
    newValor = request.form['valor']

    if tipo == 'receita':
        cursor.execute('UPDATE RECEITAS SET FONTE = ?, VALOR = ?, DATA = ? WHERE ID_RECEITA = ?', (newFonte, newValor, newData, id))
        con.commit()
        cursor.close()
        return redirect(url_for('historicoReceita'))
    elif tipo == 'despesa':
        cursor.execute('UPDATE DESPESAS SET FONTE = ?, VALOR = ?, DATA = ? WHERE ID_DESPESA = ?', (newFonte, newValor, newData, id))
        con.commit()
        cursor.close()
        return redirect(url_for('historicoDespesas'))
    
@app.route('/filtroHistorico')
def filtroHistorico():
    mes = request.args.get('mes')
    ano = request.args.get('ano')
    print(f"Mes: {mes}, Ano: {ano}")  # Verifique se os parâmetros aparecem no log
    return redirect(url_for('historico', mes=mes, ano=ano))
    
if __name__ == '__main__':
    app.run(debug=True)
