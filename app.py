from flask import Flask, request, render_template, send_from_directory, redirect, url_for, session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os
from num2words import num2words
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave_secreta"


@app.route('/gerar')  # Página para gerar o link com o valor
def gerar():
    return render_template('gerar.html')

@app.route('/gerar_link', methods=['POST'])
def gerar_link():
    valor = request.form.get('valor')
    if not valor:
        return "Erro: Valor inválido!", 400

    session['valor'] = valor  # Armazena o valor na sessão
    return redirect(url_for('recibo'))  # Redireciona para uma rota fixa


@app.route('/recibo')
def recibo():
    valor = session.get('valor', 'Valor Padrão')  # Obtém o valor da sessão
    return render_template('index.html', valor=valor)




@app.route('/')
def index():
    valor = session.get('valor', 'Valor Padrão')  # Obtém o valor da sessão
    return render_template('index.html', valor=valor)

@app.route('/definir_valor', methods=['POST'])
def definir_valor():
    valor = request.form.get('valor')
    session['valor'] = valor  # Armazena o valor na sessão
    return redirect(url_for('index'))



# Criação da pasta de uploads se não existir
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para quebrar o texto automaticamente e evitar corte
def quebra_texto(c, texto, x, y, max_width=500):
    """
    Função para adicionar texto ao canvas com quebras automáticas.
    """
    text_object = c.beginText(x, y)
    text_object.setFont("Helvetica", 10)
    text_object.setTextOrigin(x, y)

    # Divida o texto por espaços e adicione uma nova linha quando necessário
    words = texto.split(' ')
    linha = ''
    
    for word in words:
        # Tenta adicionar uma palavra à linha
        test_line = linha + ' ' + word if linha else word
        # Verifica se a linha ultrapassa o limite de largura
        if c.stringWidth(test_line, "Helvetica", 10) < max_width:
            linha = test_line
        else:
            # Se ultrapassar, escreve a linha e começa uma nova
            text_object.textLine(linha)
            linha = word
    
    # Adiciona a última linha restante
    if linha:
        text_object.textLine(linha)
    
    # Adiciona o texto ao canvas
    c.drawText(text_object)
    
    # Retorna a nova posição Y após a escrita
    return text_object.getY()  # Retorna a posição Y final depois de imprimir o texto

# Função para converter o valor numérico em por extenso
def valor_por_extenso(valor):
    return f"({num2words(valor, to='currency', lang='pt_BR')})"

# Função para formatar data no formato "Cidade, DD/MM/AAAA"
def formatar_local_data(local, data):
    # Ajustando para aceitar a data no formato YYYY-MM-DD
    data_obj = datetime.strptime(data, "%Y-%m-%d")
    return f"{local}, {data_obj.strftime('%d/%m/%Y')}"

def formatar_data(data):
    # Ajustando para aceitar a data no formato YYYY-MM-DD
    data_obj = datetime.strptime(data, "%Y-%m-%d")
    return f"{data_obj.strftime('%d/%m/%Y')}"

# Função para gerar o número único do recibo
def gerar_numero_recibo():
    # Obtém a data atual no formato DDMMYYYY
    data_atual = datetime.now().strftime("%d%m%Y")
    
    # Arquivo para controlar a numeração sequencial
    numero_arquivo = "contador_recibo.txt"
    
    # Lê o número atual do arquivo ou cria um novo
    if os.path.exists(numero_arquivo):
        with open(numero_arquivo, 'r') as f:
            numero_atual = int(f.read().strip())
    else:
        numero_atual = 0
    
    # Incrementa o número sequencial
    numero_atual += 1
    
    # Salva o novo número sequencial no arquivo
    with open(numero_arquivo, 'w') as f:
        f.write(str(numero_atual))
    
    # Retorna o número do recibo (data + numeração)
    return f"{data_atual}-{numero_atual:04d}"

# Rota para renderizar o formulário

@app.route('/contato')
def contato():
    return render_template('contato.html')

# Rota para gerar o recibo em PDF
@app.route('/gerar_recibo', methods=['POST'])
def gerar_recibo():
    print(request.form)
    # Coletando os dados do formulário
    nome = request.form['nome']
    valor = request.form['valor']
    data = request.form['data']
    telefone = request.form['telefone']
    cpf = request.form['cpf']
    banco = request.form['banco']
    evento = request.form['evento']
    cargo = request.form['role']
    data_pagamento = request.form['data_pagamento']
    observacoes = request.form['observacoes']
    
    # Verificando se a opção "Outro" foi escolhida e substituindo pelo valor do campo "outro_banco"
    if banco == 'Outro':
        banco = request.form['outro_banco']
    
    valor_extenso = valor_por_extenso(float(valor.replace('R$', '').replace(',', '.')))
    local_data_formatada = formatar_local_data("Rio de Janeiro", data_pagamento)
    data_1 = formatar_data(data) 

    # Gerar número único do recibo
    numero_recibo = gerar_numero_recibo()

    # Nome do arquivo PDF com base no número do recibo
    pdf_filename = f'recibo_{numero_recibo}.pdf'
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)

    # Criar o PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)

    # Definir a fonte
    c.setFont("Helvetica", 10)  # Reduzir o tamanho da fonte para caber mais texto

    # Posição inicial do texto
    y_position = 750  # Posição inicial do texto

    # Cabeçalho
    y_position = quebra_texto(c, "Recibo de Prestação de Serviços", 100, y_position)
    y_position -= 20

    # Informações do recibo
    y_position = quebra_texto(c, f"Recebemos,", 100, y_position)
    y_position -= 10
    y_position = quebra_texto(c, f"De PLURIELLECASTING BRASIL PRODUÇÕES LTDA, CNPJ: 18.005.911/0001-77", 100, y_position)
    y_position -= 10
    
    y_position = quebra_texto(c, f"A importância de R${valor} {valor_extenso} referentes a serviços de {cargo.lower()} em ações/eventos/marketing realizados no período: {data_1}.", 100, y_position)
    y_position = quebra_texto(c, "Dando plena, geral, integral, irrestrita e irrevogável quitação quanto a tudo o que diz respeito ao contrato 250201/2025.", 100, y_position)
    y_position -= 15
    # Evento e observações
    y_position = quebra_texto(c, f"Evento: {evento}", 100, y_position)
    y_position -= 10
    y_position = quebra_texto(c, f"[{observacoes}]", 100, y_position)
    y_position -= 10
    
    # Informações do usuário
    y_position = quebra_texto(c, f"Nome Completo: {nome}", 100, y_position)
    y_position -= 10
    y_position = quebra_texto(c, f"TEL: {telefone}", 100, y_position)
    y_position -= 10
    y_position = quebra_texto(c, f"CPF: {cpf}", 100, y_position)
    y_position -= 10
    y_position = quebra_texto(c, f"Banco: {banco}", 100, y_position)
    y_position -= 10
    
    # Agora a data do "Local do serviço" será a mesma de "Data de pagamento"
    y_position = quebra_texto(c, f" {local_data_formatada}", 200, y_position)

    # Adicionando mais espaço antes da linha de assinatura
    y_position -= 35

    # Linha de assinatura
    c.drawString(100, y_position, "ASS.:")
    c.line(160, y_position, 400, y_position)  # Linha de assinatura
    y_position -= 40  # Espaço para assinatura

    # Nome e CPF da pessoa que assinou
    y_position = quebra_texto(c, f"Nome Completo: {nome}", 160, y_position)
    y_position -= 10
    y_position = quebra_texto(c, f"CPF: {cpf}", 160, y_position)

    # Número do recibo no canto superior direito
    c.setFont("Helvetica", 8)
    c.drawString(450, 770, f"Nº Recibo: {numero_recibo}")

    # Finalizar o PDF
    c.save()

    # Passar o nome do arquivo gerado para ser mostrado na página de download
    return render_template('download.html', pdf_filename=pdf_filename)


@app.route('/avaliar', methods=['POST'])
def avaliar():
    nome = request.form['nome']
    avaliacao = request.form['avaliacao']
    estrelas = request.form['estrelas']
    data = request.form['data']
    
    # Definindo o diretório de avaliações
    diretorio_avaliacoes = 'avaliacoes'
    
    # Criar o diretório se não existir
    if not os.path.exists(diretorio_avaliacoes):
        os.makedirs(diretorio_avaliacoes)
    
    # Criação do nome do arquivo com base na data
    data_atual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    arquivo = os.path.join(diretorio_avaliacoes, f"avaliacao_{data_atual}.txt")
    
    # Salvando a avaliação no arquivo
    with open(arquivo, 'w') as file:
        file.write(f"Nome: {nome}\n")
        file.write(f"Avaliação: {avaliacao}\n")
        file.write(f"Estrelas: {estrelas}\n")
        file.write(f"Data: {data}\n")
    
    print(f"Avaliação salva no arquivo: {arquivo}")
    
    return {"status": "success"}, 200











# Rota para servir o PDF gerado para download
@app.route('/uploads/<filename>')
def upload_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)



