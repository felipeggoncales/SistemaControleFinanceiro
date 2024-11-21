from flask import Flask, render_template, request, flash, url_for, redirect, get_flashed_messages, session
from datetime import datetime
import fdb
import re
import locale
import base64

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

app = Flask(__name__)
app.secret_key = 'logisticBanco'

host = 'localhost'
database = r'C:\Users\Aluno\Documents\GitHub\SistemaControleFinanceiro\BANCO.FDB'
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


@app.route('/upload-profile-image', methods=['POST'])
def upload_profile_image_handler():
    if 'image' not in request.files:
        return {'success': False, 'error': 'Nenhuma imagem enviada.'}, 400

    image = request.files['image']
    user_id = session.get('id_usuario')

    if image and user_id:
        image_blob = image.read()

        cursor = con.cursor()
        cursor.execute("""
            UPDATE usuario
            SET foto_perfil = ?
            WHERE id_usuario = ?
        """, (image_blob, user_id))
        con.commit()

        # Converter a imagem para base64 para exibição no front-end
        import base64
        image_base64 = f"data:image/jpeg;base64,{base64.b64encode(image_blob).decode('utf-8')}"

        return {'success': True, 'image_url': image_base64}

    return {'success': False, 'error': 'Erro ao salvar a imagem.'}, 500

@app.route('/remove-profile-image', methods=['POST'])
def remove_profile_image_handler():
    user_id = session.get('id_usuario')

    if user_id:
        cursor = con.cursor()
        cursor.execute("""
            UPDATE usuario
            SET foto_perfil = NULL
            WHERE id_usuario = ?
        """, (user_id,))
        con.commit()

        return {'success': True}

    return {'success': False, 'error': 'Erro ao remover a imagem.'}, 500

@app.route('/profile')
def profile():
    user_id = session.get('id_usuario')
    cursor = con.cursor()
    cursor.execute("SELECT foto_perfil FROM usuario WHERE id_usuario = ?", (user_id,))
    foto_perfil = cursor.fetchone()[0]

    user_image_url = None
    if foto_perfil:
        import base64
        user_image_url = f"data:image/jpeg;base64,{base64.b64encode(foto_perfil).decode('utf-8')}"

    return render_template('home.html', user_image_url=user_image_url)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/abrirUsuario')
def abrirUsuario():
    return render_template('cadastro.html', titulo='Novo usuario')


@app.route('/abrirDespesa')
def abrirDespesa():
    id_usuario = session.get('id_usuario')

    if id_usuario:
        return render_template('adicionarDespesa.html', titulo='Nova despesa')
    else:
        flash('Sessão não iniciada', 'error')
        return render_template('index.html')

@app.route('/abrirReceita')
def abrirReceita():
    id_usuario = session.get('id_usuario')

    if id_usuario:
        return render_template('adicionarReceita.html', titulo='Nova receita')
    else:
            flash('Sessão não iniciada', 'error')
            return render_template('index.html')

@app.route('/historico')
def historico():
    id_usuario = session.get('id_usuario')

    if id_usuario:
        mes = request.args.get('mes', None)
        ano = request.args.get('ano', None)

        if mes == None:
            if session.get('mes'):
                mes = session.get('mes')
            else:
                mes = str(datetime.now().month)
        if ano == None:
            if session.get('ano'):
                ano = session.get('ano')
            else:
                ano = str(datetime.now().year)

        session['mes'] = mes
        session['ano'] = ano    

        mensagem = None
        mes_convertido = None
        if mes and ano and mes != '13':
            mes_convertido = datetime.strptime(mes, "%m").strftime("%b")
            mensagem = 'em '+datetime.strptime(mes, "%m").strftime("%B")
        elif mes == '13' and ano == '13':
            mensagem = 'em todo o período'
        elif mes == '13':
            mensagem = f'em {ano}'
        elif ano == '13':
            mensagem = f'em {datetime.strptime(mes, "%m").strftime("%B")} de 2024-2026'
        else:
            mensagem = 'nos últimos 30 dias'

        textoPeriodo = 'Últimos 30 dias'
        if mes != '13' and ano != '13':
            textoPeriodo = f'{mes_convertido}/{ano}'
        elif mes == '13' and ano == '13':
            textoPeriodo = 'Em todo o período'
        elif mes == '13':
            textoPeriodo = f'Em {ano}'
        elif ano == '13':
            textoPeriodo = f'{mes_convertido}/2024-2026'

        despesas = 0
        receitas = 0

        cursor = con.cursor()
        if mes and ano and mes != '13' and ano != '13':
            cursor.execute('''
                SELECT VALOR FROM DESPESAS 
                WHERE (ID_USUARIO = ?) AND (EXTRACT(MONTH FROM DATA) = ?) AND (EXTRACT(YEAR FROM DATA) = ?)
            ''', (session.get('id_usuario'), mes, ano))
        elif mes == '13' and ano == '13':
            cursor.execute('''
                SELECT VALOR FROM DESPESAS 
                WHERE ID_USUARIO = ?
            ''', (session.get('id_usuario'),))
        elif mes == '13':
            cursor.execute('''
                SELECT VALOR FROM DESPESAS 
                WHERE (ID_USUARIO = ?) AND (EXTRACT(YEAR FROM DATA) = ?)
            ''', (session.get('id_usuario'), ano))
        elif ano == '13':
            cursor.execute('''
                SELECT VALOR FROM DESPESAS 
                WHERE (ID_USUARIO = ?) AND (EXTRACT(MONTH FROM DATA) = ?)
            ''', (session.get('id_usuario'), mes))
        else:
            cursor.execute('''
                SELECT VALOR FROM DESPESAS 
                WHERE (ID_USUARIO = ?) AND (DATA BETWEEN (CURRENT_DATE - 30) AND CURRENT_DATE)
            ''', (session.get('id_usuario'),))
            
        for valor in cursor.fetchall():
            despesas += valor[0]

        if mes and ano and mes != '13' and ano != '13':
            cursor.execute('''
                SELECT VALOR FROM RECEITAS 
                WHERE ID_USUARIO = ? AND EXTRACT(MONTH FROM DATA) = ? AND EXTRACT(YEAR FROM DATA) = ?
            ''', (session.get('id_usuario'), mes, ano))
        elif mes == '13' and ano == '13':
            cursor.execute('''
                SELECT VALOR FROM RECEITAS 
                WHERE ID_USUARIO = ?
            ''', (session.get('id_usuario'),))
        elif mes == '13':
            cursor.execute('''
                SELECT VALOR FROM RECEITAS 
                WHERE (ID_USUARIO = ?) AND (EXTRACT(YEAR FROM DATA) = ?)
            ''', (session.get('id_usuario'), ano))
        elif ano == '13':
            cursor.execute('''
                SELECT VALOR FROM RECEITAS 
                WHERE (ID_USUARIO = ?) AND (EXTRACT(MONTH FROM DATA) = ?)
            ''', (session.get('id_usuario'), mes))
        else:
            cursor.execute('''
                SELECT VALOR FROM RECEITAS 
                WHERE ID_USUARIO = ? AND (DATA BETWEEN CURRENT_DATE - 30 AND CURRENT_DATE)
            ''', (session.get('id_usuario'),))
        for valor in cursor.fetchall():
            receitas += valor[0]
        cursor.close()

        return render_template('historico.html', despesas=despesas, receitas=receitas, mes=mes_convertido, ano=ano, mensagem=mensagem, textoPeriodo=textoPeriodo)
    else:
        flash('Sessão não iniciada', 'error')
        return render_template('index.html')

@app.route('/historicoReceita')
def historicoReceita():
    id_usuario = session.get('id_usuario')

    if id_usuario:
        mes = request.args.get('mes', None)
        ano = request.args.get('ano', None)

        if mes == None:
            if session.get('mes'):
                mes = session.get('mes')
            else:
                mes = str(datetime.now().month)
        if ano == None:
            if session.get('ano'):
                ano = session.get('ano')
            else:
                ano = str(datetime.now().year)

        session['mes'] = mes
        session['ano'] = ano

        mes_convertido = None
        if mes and ano and mes != '13':
            mes_convertido = datetime.strptime(mes, "%m").strftime("%b")

        textoPeriodo = 'Últimos 30 dias'
        if mes != '13' and ano != '13':
            textoPeriodo = f'{mes_convertido}/{ano}'
        elif mes == '13' and ano == '13':
            textoPeriodo = 'Em todo o período'
        elif mes == '13':
            textoPeriodo = f'Em {ano}'
        elif ano == '13':
            textoPeriodo = f'{mes_convertido}/2024-2026'

        cursor = con.cursor()
        if mes and ano and mes != '13' and ano != '13':
            cursor.execute('''
                SELECT id_receita, valor, data, fonte FROM RECEITAS WHERE ID_USUARIO = ? 
                AND EXTRACT(MONTH FROM DATA) = ? AND EXTRACT(YEAR FROM DATA) = ? ORDER BY data DESC
            ''', (session.get('id_usuario'), mes, ano))
        elif mes == '13' and ano == '13':
            cursor.execute('''
                SELECT id_receita, valor, data, fonte FROM RECEITAS 
                WHERE ID_USUARIO = ?
            ''', (session.get('id_usuario'),))
        elif mes == '13':
            cursor.execute('''
                SELECT id_receita, valor, data, fonte FROM RECEITAS 
                WHERE (ID_USUARIO = ?) AND (EXTRACT(YEAR FROM DATA) = ?)
            ''', (session.get('id_usuario'), ano))
        elif ano == '13':
            cursor.execute('''
                SELECT id_receita, valor, data, fonte FROM RECEITAS 
                WHERE (ID_USUARIO = ?) AND (EXTRACT(MONTH FROM DATA) = ?)
            ''', (session.get('id_usuario'), mes))
        else:
            cursor.execute('''
                SELECT id_receita, valor, data, fonte FROM RECEITAS 
                WHERE (ID_USUARIO = ?) AND (DATA BETWEEN (CURRENT_DATE - 30) AND CURRENT_DATE)
            ''', (session.get('id_usuario'),))

        receitas = cursor.fetchall()
        cursor.close()

        return render_template('historicoReceita.html', receitas=receitas, mes=mes_convertido, ano=ano, textoPeriodo=textoPeriodo)
    else:
        flash('Sessão não iniciada', 'error')
        return render_template('index.html')


@app.route('/historicoDespesas')
def historicoDespesas():
    id_usuario = session.get('id_usuario')

    if id_usuario:
        mes = request.args.get('mes', None)
        ano = request.args.get('ano', None)

        if mes == None:
            if session.get('mes'):
                mes = session.get('mes')
            else:
                mes = str(datetime.now().month)
        if ano == None:
            if session.get('ano'):
                ano = session.get('ano')
            else:
                ano = str(datetime.now().year)

        session['mes'] = mes
        session['ano'] = ano

        mes_convertido = None
        if mes and ano and mes != '13':
            mes_convertido = datetime.strptime(mes, "%m").strftime("%b")

        textoPeriodo = 'Últimos 30 dias'
        if mes != '13' and ano != '13':
            textoPeriodo = f'{mes_convertido}/{ano}'
        elif mes == '13' and ano == '13':
            textoPeriodo = 'Em todo o período'
        elif mes == '13':
            textoPeriodo = f'Em {ano}'
        elif ano == '13':
            textoPeriodo = f'{mes_convertido}/2024-2026'

        cursor = con.cursor()
        if mes and ano and mes != '13' and ano != '13':
            cursor.execute('''
                SELECT id_despesa, valor, data, fonte FROM DESPESAS WHERE ID_USUARIO = ? 
                AND EXTRACT(MONTH FROM DATA) = ? AND EXTRACT(YEAR FROM DATA) = ? ORDER BY data DESC
            ''', (session.get('id_usuario'), mes, ano))
        elif mes == '13' and ano == '13':
            cursor.execute('''
                SELECT id_despesa, valor, data, fonte FROM DESPESAS 
                WHERE ID_USUARIO = ?
            ''', (session.get('id_usuario'),))
        elif mes == '13':
            cursor.execute('''
                SELECT id_despesa, valor, data, fonte FROM DESPESAS 
                WHERE (ID_USUARIO = ?) AND (EXTRACT(YEAR FROM DATA) = ?)
            ''', (session.get('id_usuario'), ano))
        elif ano == '13':
            cursor.execute('''
                SELECT id_despesa, valor, data, fonte FROM DESPESAS 
                WHERE (ID_USUARIO = ?) AND (EXTRACT(MONTH FROM DATA) = ?)
            ''', (session.get('id_usuario'), mes))
        else:
            cursor.execute('''
                SELECT id_despesa, valor, data, fonte FROM DESPESAS 
                WHERE (ID_USUARIO = ?) AND (DATA BETWEEN (CURRENT_DATE - 30) AND CURRENT_DATE)
            ''', (session.get('id_usuario'),))

        despesas = cursor.fetchall()
        cursor.close()

        return render_template('historicoDespesas.html', despesas=despesas, mes=mes_convertido, ano=ano, textoPeriodo=textoPeriodo)
    else:
        flash('Sessão não iniciada', 'error')
        return render_template('index.html')

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
            session['nome'] = resultado[0]
            session['sobrenome'] = resultado[1]
            return redirect(url_for('home'))
    else:
        limpar_flash()
        flash('E-mail ou senha incorretos', 'error')
        cursor.close()
        return redirect(url_for('index'))
    
@app.route('/logout')
def logout():
    session['id_usuario'] = None
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
    id_usuario = session.get('id_usuario')

    if id_usuario:
        despesas = 0
        receitas = 0

        cursor = con.cursor()
        cursor.execute('SELECT VALOR FROM DESPESAS WHERE ID_USUARIO = ? AND EXTRACT(MONTH FROM DATA) = EXTRACT(MONTH FROM CURRENT_DATE)', (session.get('id_usuario'),))
        for valor in cursor.fetchall():
            despesas += valor[0]

        cursor.execute('SELECT VALOR FROM RECEITAS WHERE ID_USUARIO = ? AND EXTRACT(MONTH FROM DATA) = EXTRACT(MONTH FROM CURRENT_DATE)', (session.get('id_usuario'),))
        for valor in cursor.fetchall():
            receitas += valor[0]

        cursor.execute('SELECT LIMITE_GRAFICO FROM USUARIO WHERE ID_USUARIO = ?', (session.get('id_usuario'),))
        limite_teste = cursor.fetchone()
        if limite_teste:
            limite = limite_teste[0]
        else:
            limite = None

        cursor.execute('SELECT fonte, valor FROM DESPESAS WHERE ID_USUARIO = ? AND EXTRACT(MONTH FROM DATA) = EXTRACT(MONTH FROM CURRENT_DATE) ORDER BY valor DESC', (session.get('id_usuario'),))
        lista = cursor.fetchall()

        valores = []
        fontes = []

        if lista:
            top_4 = lista[:4]
            outros = lista[4:]

            for item in top_4:
                valores.append(item[1])
                fontes.append(item[0])

            if outros:
                valor_5 = 0;
                for item2 in outros:
                    valor_5 = valor_5 + int(item2[1])
                valores.append(valor_5)
                fontes.append("Outros")
        else:
            valores = [1]
            fontes = ['Nada']

        cursor.close()

        return render_template('home.html', despesas=despesas, receitas=receitas, limite=limite, fontes=fontes, valores=valores)
    else:
        flash('Sessão não iniciada', 'error')
        return render_template('index.html')


@app.route('/addDespesa', methods=['POST'])
def addDespesa():
    id_usuario = session.get('id_usuario')

    if id_usuario:
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
    else:
        flash('Sessão não iniciada', 'error')
        return render_template('index.html')
    
@app.route('/addReceita', methods=['POST'])
def addReceita():
    id_usuario = session.get('id_usuario')

    if id_usuario:
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
    else:
        flash('Sessão não iniciada', 'error')
        return render_template('index.html')

@app.route('/editar/<int:id>/<tipo>')
def editar(id, tipo):
    id_usuario = session.get('id_usuario')

    if id_usuario:
        cursor = con.cursor()
        if tipo == 'receita':
            cursor.execute('SELECT id_receita, valor, data, fonte FROM RECEITAS WHERE id_receita = ?', (id,))
        elif tipo == 'despesa':
            cursor.execute('SELECT id_despesa, valor, data, fonte FROM DESPESAS WHERE id_despesa = ?', (id,))

        mensagem = cursor.fetchone()
        cursor.close()
        return render_template('editar.html', mensagem=mensagem, receitaOuDespesa=tipo)
    else:
        flash('Sessão não iniciada', 'error')
        return render_template('index.html')

@app.route('/excluir/<int:id>/<tipo>')
def excluir(id,tipo):
    id_usuario = session.get('id_usuario')

    if id_usuario:
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
    else:
        flash('Sessão não iniciada', 'error')
        return render_template('index.html')
    
@app.route('/salvarAlteracoes/<int:id>/<tipo>', methods=['POST'])
def salvarAlteracoes(id,tipo):
    id_usuario = session.get('id_usuario')

    if id_usuario:
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
    else:
        flash('Sessão não iniciada', 'error')
        return render_template('index.html')
    
@app.route('/filtroHistorico')
def filtroHistorico():
    id_usuario = session.get('id_usuario')

    if id_usuario:
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        print(f"Mes: {mes}, Ano: {ano}")  # Verifique se os parâmetros aparecem no log
        return redirect(url_for('historico', mes=mes, ano=ano))
    else:
        flash('Sessão não iniciada', 'error')
        return render_template('index.html')

@app.route('/definirGrafico', methods=['GET'])
def definirGrafico():
    id_usuario = session.get('id_usuario')

    if id_usuario:
        limite = request.args.get('limiteInput')

        if limite:
            cursor = con.cursor()
            cursor.execute('UPDATE USUARIO SET LIMITE_GRAFICO = ? WHERE ID_USUARIO = ?', (limite, session.get('id_usuario')))
            con.commit()
            cursor.close()
            return jsonify({'status': 'success', 'message': 'Limite atualizado com sucesso!'})

        return jsonify({'status': 'error', 'message': 'Limite não informado!'})
    else:
        flash('Sessão não iniciada', 'error')
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
