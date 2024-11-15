from flask import Flask, render_template, request, flash, url_for, redirect, get_flashed_messages, session
import fdb
import re

app = Flask(__name__)
app.secret_key = 'logisticBanco'

host = 'localhost'
database = r'C:\Users\felip\OneDrive\Documentos\GitHub\SistemaControleFinanceiro\BANCO.FDB'
user = 'SYSDBA'
password = 'sysdba'
con = fdb.connect(host=host, database=database, user=user, password=password)

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
    mensagens = get_flashed_messages()
    
    # Verificar se existe alguma mensagem e se é diferente de "Sua conta foi cadastrada com sucesso"
    if mensagens:
        if mensagens[0] != "Sua conta foi cadastrada com sucesso":
            # Se for diferente, limpa as mensagens (elas já são apagadas automaticamente)
            pass  # Aqui você pode adicionar alguma lógica extra se quiser limpar manualmente
    
    # Renderiza o template
    return render_template('index.html')


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

@app.route('/historico')
def historico():
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

    return render_template('historico.html', despesas=despesas, receitas=receitas)

# Historico Receitas
@app.route('/historicoReceita')
def historicoReceita():
    cursor = con.cursor()
    cursor.execute('SELECT valor, data, fonte FROM RECEITAS')
    receitas = cursor.fetchall()
    cursor.close()
    return render_template('historicoReceita.html', receitas=receitas)

# Historico Despesas
@app.route('/historicoDespesas')
def historicoDespesas():
    cursor = con.cursor()
    cursor.execute('SELECT valor, data, fonte FROM DESPESAS')
    despesas = cursor.fetchall()
    cursor.close()
    return render_template('historicoDespesas.html', despesas=despesas)

# Abrir pagina 'adicionarReceita'
@app.route('/abrirReceita')
def abrirReceita():
    return render_template('adicionarReceita.html', titulo='Nova receita')

@app.route('/addReceita', methods=['POST'])
def addReceita():
     if request.method == 'POST':
        try:
            valor = float(request.form['valor'])
            data = request.form['data']
            fonte = request.form['fonte']

            if valor <= 0:
                flash('Coloque um valor maior que 0', 'error')
            else:
                cursor = con.cursor()
                cursor.execute("INSERT INTO RECEITAS (id_usuario, valor, data, fonte) VALUES (?, ?, ?, ?)", (session.get('id_usuario'), valor, data, fonte))
                con.commit()
                cursor.close()
                flash('Sua receita foi adicionada com sucesso')
        except ValueError:
            flash('O valor informado não é válido. Por favor, insira um número válido.', 'error')

        return redirect(url_for('home'))

# Editar receita
@app.route('/atualizarReceita')
def atualizarReceita():
    return render_template('atualizarReceita.html', Receita='Editar receita')

@app.route('/editarReceita/<int:id>', methods=['GET', 'POST'])
def editarReceita(id):
    cursor = con.cursor()
    cursor.execute("SELECT id_receita, valor, fonte, data FROM RECEITAS WHERE id_receita = ?", (id,))
    receita = cursor.fetchone()

    if not receita:
        flash("Receita não encontrada.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        valor = float(request.form['valor'])
        fonte = request.form['fonte']
        data = request.form['data']

        cursor.execute("UPDATE RECEITAS SET valor = ?, fonte = ?, data = ? WHERE id_receita = ?",
                       (valor, fonte, data, id))
        con.commit()
        flash("Receita atualizada com sucesso")
        return redirect(url_for('index'))
    cursor.close()
    return render_template('atualizarReceita.html', receita=receita, titulo='Editar receita')

# Abrir pagina 'adicionarDespesa'
@app.route('/abrirDespesa')
def abrirDespesa():
    return render_template('adicionarDespesa.html', titulo='Nova despesa')

@app.route('/addDespesa', methods=['POST'])
def addDespesa():
    if request.method == 'POST':
        try:
            valor = float(request.form['valor'])
            data = request.form['data']
            fonte = request.form['fonte']

            if valor <= 0:
                flash('Coloque um valor maior que 0', 'error')
            else:
                cursor = con.cursor()
                cursor.execute("INSERT INTO DESPESAS (id_usuario, valor, data, fonte) VALUES (?, ?, ?, ?)", (session.get('id_usuario'),valor, data, fonte))
                con.commit()
                cursor.close()
                flash('Sua despesa foi adicionada com sucesso!')
        except ValueError:
            flash('O valor informado não é válido. Por favor, insira um número válido.', 'error')

        return redirect(url_for('home'))


# Editar despesa
@app.route('/atualizarDespesa')
def atualizarDespesa():
    return render_template('atualizarDespesa.html', titulo='Editar despesa')

@app.route('/editarDespesa/<int:id>', methods=['GET', 'POST'])
def editarDespesa(id):
    cursor = con.cursor()
    cursor.execute("SELECT id_despesa, valor, fonte, data FROM DESPESAS WHERE id_despesa = ?", (id,))
    despesas = cursor.fetchone()

    if not despesas:
        flash("Despesa não encontrada.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        valor = float(request.form['valor'])
        fonte = request.form['fonte']
        data = request.form['data']

        cursor.execute("UPDATE DESPESAS SET valor = ?, fonte = ?, data = ? WHERE id_despesa = ?",
                       (valor, fonte, data, id))
        con.commit()
        flash("Despesa atualizada com sucesso")
        return redirect(url_for('index'))
    cursor.close()
    return render_template('atualizarDespesa.html', despesas=despesas, titulo='Editar despesa')

# Abrir pagina 'cadastro'
@app.route('/abrirUsuario')
def abrirUsuario():
    get_flashed_messages()
    return render_template('cadastro.html', titulo='Novo usuario')

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
            flash('Email já cadastrado', 'error')
            return redirect(url_for('abrirUsuario'))
        # Validação de senha (8 caracteres, 1 letra maiúscula, 1 número, 1 caractere especial)
        if not re.fullmatch(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$', senha):
            flash('A senha deve ter ao menos 8 caracteres, uma letra maiúscula, um número e um caractere especial.', 'error')
            return redirect(url_for('abrirUsuario'))  # Certifique-se de retornar após flash
        # Inserção de novo usuário
        cursor.execute("INSERT INTO USUARIO (nome, sobrenome, email, senha) VALUES (?, ?, ?, ?)",
                       (nome, sobrenome, email, senha))
        con.commit()
        flash('Sua conta foi cadastrada com sucesso', 'success')
        return redirect(url_for('index'))  # Redireciona após o sucesso
    except Exception as e:
        flash(f'Erro ao cadastrar a conta: {e}', 'error')
        return redirect(url_for('abrirUsuario'))  # Redireciona após erro
    finally:
        cursor.close()  # Fecha o cursor mesmo em caso de exceção

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()
    cursor.execute("SELECT id_usuario, email, senha FROM USUARIO WHERE email = ?", (email,))
    usuario = cursor.fetchone()

    if usuario and usuario[2] == senha:
        flash('Login realizado com sucesso', 'success')
        session['id_usuario'] = usuario[0]
        # Obter nome e sobrenome do usuário
        cursor.execute("SELECT nome, sobrenome FROM USUARIO WHERE email = ?", (email,))
        resultado = cursor.fetchone()  # fetchone() retorna uma única linha como uma tupla
        cursor.close()
        if resultado:
            nome, sobrenome = resultado  # Desempacotando a tupla
            session['nome'] = nome
            session['sobrenome'] = sobrenome
            # Passar nome e sobrenome como parâmetros para a rota 'home'
            return redirect(url_for('home'))
    else:
        cursor.close()
        flash('E-mail ou senha incorretos', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
