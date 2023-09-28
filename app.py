from flask import Flask, make_response, jsonify, request
from flask_pydantic_spec import FlaskPydanticSpec
from flask_pydantic_spec import Response, Request
import psycopg2
from src.models.Secao.Secao import Secao
from src.models.Secao.Secoes import Secoes
from src.models.Produto.Produto import Produto
from src.models.Produto.Produtos import Produtos
from src.models.Erro import Erro
from flask_cors import CORS

app = Flask(__name__)
spec = FlaskPydanticSpec()
spec.register(app)
CORS(app)

conn = psycopg2.connect(database="ecommerce",
                        user="postgres",
                        password="123456",
                        host="localhost", port="5432")

# conn = psycopg2.connect(database="ecommerce",
#                        user="postgres",
#                        password="123456",
#                        host="bd_postgres_produtos")


@app.get('/Secao')
# HTTP_200=Secoes
@spec.validate(resp=Response(HTTP_200=Secoes), tags=['Secoes'])
def Get():
    """
    Retorna todas as seções da base de dados

    """
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome FROM SECAO Where ativa = true')
    secoes = cursor.fetchall()
    cursor.close()

    secoesVO = list()
    for sc in secoes:
        secoesVO.append({
            'id': sc[0],
            'nome': sc[1]
        })

    return make_response(
        jsonify(Secoes(Secoes=secoesVO).dict()))


@app.post('/BuscarSecao')
# HTTP_200=Secoes
@spec.validate(body=Request(Secao), resp=Response(HTTP_200=Secoes), tags=['Secoes'])
def BuscarSecao():
    """
    Retorna uma secão de acordo com os parâmetros pesquisados

    """

    cursor = conn.cursor()
    cursor.execute('SELECT id, nome FROM SECAO Where ativa = true ' +
                   MontaPredicadoBuscaSecao(request))
    secoes = cursor.fetchall()
    cursor.close()

    secoesVO = list()
    for sc in secoes:
        secoesVO.append({
            'id': sc[0],
            'nome': sc[1]
        })

    return make_response(
        jsonify(Secoes(Secoes=secoesVO).dict()))


@app.post('/Secao')
# HTTP_200=jsonify,
@spec.validate(body=Request(Secao), resp=Response(HTTP_400=Erro,  HTTP_500=Erro), tags=['Secoes'])
def Post():
    """
    Insere uma seção da base de dados

    """
    try:
        body = request.context.body.dict()
        secao = request.json

        if secao['nome'] != "":
            cursor = conn.cursor()
            sql = f"INSERT INTO SECAO(NOME) VALUES('{secao['nome']}')"
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            return body

        return make_response(
            jsonify(Erro(status=400, msg="Não foi possível incluir a Seção. Verifique os parêmetros enviados").dict())), 400

    except Exception as e:
        return make_response(
            jsonify(Erro(status=500, msg="Houve um erro grave com a aplicação").dict())), 500


@app.put('/Secao')
@spec.validate(body=Request(Secao), resp=Response(HTTP_400=Erro,  HTTP_500=Erro), tags=['Secoes'])
def Put():
    """
    Atualiza a seção da base de dados

    """
    try:

        body = request.context.body.dict()
        secao = request.json

        if secao['nome'] == "":
            return make_response(
                jsonify(Erro(status=400, msg="Não é possível atualizar o nome da Seção. Verifique os parêmetros enviados").dict())), 400

        if len(secao['nome']) < 3:
            return make_response(
                jsonify(Erro(status=400, msg="Nome da Seção deve ter mais de 2 caracteres. Verifique os parêmetros enviados").dict())), 400

        if secao['id'] == "":
            return make_response(
                jsonify(Erro(status=400, msg="Id da Seção não especificado. Verifique os parêmetros enviados").dict())), 400

        if secao['id'] == 0:
            return make_response(
                jsonify(Erro(status=400, msg="Id da Seção não especificado. Verifique os parêmetros enviados").dict())), 400

        if type(int(secao['id'])) != int:
            return make_response(
                jsonify(Erro(status=400, msg="Id da Seção inválido. Verifique os parêmetros enviados").dict())), 400

        cursor = conn.cursor()
        sql = f"UPDATE SECAO SET NOME = '{secao['nome']}' WHERE ID = {secao['id']}"
        cursor.execute(sql)
        conn.commit()
        cursor.close()

        return make_response(
            jsonify(body))

    except Exception as e:
        return make_response(
            jsonify(Erro(status=500, msg="Houve um erro durante a atualização").dict())), 500


@app.delete('/Secao')
@spec.validate(body=Request(Secao), resp=Response(HTTP_400=Erro,  HTTP_500=Erro), tags=['Secoes'])
def Delete():
    """
    Deleta a seção da base de dados

    """
    try:
        body = request.context.body.dict()
        secao = request.json
        secoes = retorna_produtos(secao['id'])

        if secao['id'] == "":
            return make_response(
                jsonify(Erro(status=400, msg="Id da Seção não especificado. Verifique os parêmetros enviados").dict())), 400

        if secao['id'] == "0":
            return make_response(
                jsonify(Erro(status=400, msg="Id da Seção não especificado. Verifique os parêmetros enviados").dict())), 400

        if type(int(secao['id'])) != int:
            return make_response(
                jsonify(Erro(status=400, msg="Id da Seção inválido. Verifique os parêmetros enviados").dict())), 400

        if secoes > 0:
            return make_response(
                jsonify(Erro(status=400, msg="Não é possível excluir pois existem produtos vinculados").dict())), 400

        cursor = conn.cursor()
        sql = f"DELETE FROM SECAO WHERE ID = {secao['id']}"
        cursor.execute(sql)
        conn.commit()

        cursor.close()
        return make_response(
            jsonify(body))

    except Exception as e:
        return make_response(
            jsonify(Erro(status=500, msg="Existem produtos vinculados a essa seção. Não é possível excluir.").dict())), 500


@app.get('/Produtos')
@spec.validate(resp=Response(HTTP_200=Produtos), tags=['Produtos'])
def getProdutos():
    """
    Retorna todos os produtos da base de dados

    """
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, nome, preco, idSecao FROM PRODUTOS Where ativa = true')
    produtos = cursor.fetchall()

    cursor.close()

    produtosVO = list()
    for pd in produtos:
        produtosVO.append({
            'id': pd[0],
            'nome': pd[1],
            'preco': pd[2],
            'idSecao': pd[3]
        })

    return make_response(
        jsonify(Produtos(Produtos=produtosVO).dict()))


@app.post('/BuscaProdutos')
@spec.validate(body=Request(Produto), resp=Response(HTTP_200=Produtos), tags=['Produtos'])
def getBuscaProdutos():
    """
    Retorna todos os produtos que estejam ativos de acordo com a solicitação

    """
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, preco, idSecao FROM PRODUTOS Where ativa = true ' +
                   MontaPredicadoBuscaProduto(request))
    produtos = cursor.fetchall()

    cursor.close()

    produtosVO = list()
    for pd in produtos:
        produtosVO.append({
            'id': pd[0],
            'nome': pd[1],
            'preco': pd[2],
            'idSecao': pd[3]
        })

    return make_response(
        jsonify(Produtos(Produtos=produtosVO).dict()))


@app.post('/Produtos')
@spec.validate(body=Request(Produto), resp=Response(HTTP_200=Produto, HTTP_400=Erro,  HTTP_500=Erro), tags=['Produtos'])
def postProduto():
    """
    Insere um produto da base de dados

    """
    try:

        body = request.context.body.dict()
        produto = request.json

        if produto['nome'] == "":
            return make_response(
                jsonify(Erro(status=400, msg="O nome do pruduto não pode ser vazio").dict())), 400

        if len(produto['nome']) < 3:
            return make_response(
                jsonify(Erro(status=400, msg="Nome do produto deve ter mais de 2 caracteres. Verifique os parêmetros enviados").dict())), 400

        if produto['idSecao'] == "":
            return make_response(
                jsonify(Erro(status=400, msg="Seção não especificada. Verifique os parêmetros enviados").dict())), 400

        if produto['idSecao'] == "0":
            return make_response(
                jsonify(Erro(status=400, msg="Seção não especificada. Verifique os parêmetros enviados").dict())), 400

        if type(int(produto['idSecao'])) != int:
            return make_response(
                jsonify(Erro(status=400, msg="Seção não especificada. Verifique os parêmetros enviados").dict())), 400

        if produto['preco'] == "":
            return make_response(
                jsonify(Erro(status=400, msg="Preço do produto não especificado. Verifique os parêmetros enviados").dict())), 400

        cursor = conn.cursor()
        sql = f"INSERT INTO PRODUTOS(NOME,PRECO, IDSECAO) VALUES('{produto['nome']}', {produto['preco']}, {produto['idSecao']})"
        cursor.execute(sql)
        conn.commit()

        cursor.close()
        return body

    except Exception as e:
        return make_response(
            jsonify(Erro(status=500, msg="Houve um erro ao cadastrar o produto").dict())), 500


@app.put('/Produtos')
@spec.validate(body=Request(Produto), resp=Response(HTTP_200=Produto, HTTP_400=Erro,  HTTP_500=Erro), tags=['Produtos'])
def putProduto():
    """
    Atualiza um produto da base de dados

    """
    try:
        body = request.context.body.dict()
        produto = request.json

        if produto['id'] == "":
            return make_response(
                jsonify(Erro(status=400, msg="Id do produto não especificado. Verifique os parêmetros enviados").dict())), 400

        if produto['id'] == 0:
            return make_response(
                jsonify(Erro(status=400, msg="Id do produto não especificado. Verifique os parêmetros enviados").dict())), 400

        if type(int(produto['id'])) != int:
            return make_response(
                jsonify(Erro(status=400, msg="Id do produto inválido. Verifique os parêmetros enviados").dict())), 400

        if produto['nome'] == "":
            return make_response(
                jsonify(Erro(status=400, msg="O nome do pruduto não pode ser vazio").dict())), 400

        if len(produto['nome']) < 3:
            return make_response(
                jsonify(Erro(status=400, msg="Nome do produto deve ter mais de 2 caracteres. Verifique os parêmetros enviados").dict())), 400

        if produto['idSecao'] == "":
            return make_response(
                jsonify(Erro(status=400, msg="Seção não especificada. Verifique os parêmetros enviados").dict())), 400

        if produto['idSecao'] == "0":
            return make_response(
                jsonify(Erro(status=400, msg="Seção não especificada. Verifique os parêmetros enviados").dict())), 400

        if type(int(produto['idSecao'])) != int:
            return make_response(
                jsonify(Erro(status=400, msg="Seção não especificada. Verifique os parêmetros enviados").dict())), 400

        if produto['preco'] == "":
            return make_response(
                jsonify(Erro(status=400, msg="Preço do produto não especificado. Verifique os parêmetros enviados").dict())), 400

        cursor = conn.cursor()
        sql = f"UPDATE PRODUTOS SET NOME = '{produto['nome']}', PRECO = {produto['preco']} , IDSECAO = {produto['idSecao']} WHERE ID = {produto['id']}"
        cursor.execute(sql)
        conn.commit()

        cursor.close()
        return make_response(
            jsonify(body))

    except Exception as e:
        return make_response(
            jsonify(Erro(status=500, msg="Houve um erro ao atualizar o produto").dict())), 500


@app.delete('/Produtos')
@spec.validate(body=Request(Produto), resp=Response(HTTP_200=Produto, HTTP_400=Erro,  HTTP_500=Erro), tags=['Produtos'])
def deleteProduto():
    """
    Deleta um produto da base de dados

    """
    try:
        body = request.context.body.dict()
        produto = request.json

        if produto['id'] == "":
            return make_response(
                jsonify(Erro(status=400, msg="Id do produto não especificado. Verifique os parêmetros enviados").dict())), 400

        if produto['id'] == 0:
            return make_response(
                jsonify(Erro(status=400, msg="Id do produto não especificado. Verifique os parêmetros enviados").dict())), 400

        if type(int(produto['id'])) != int:
            return make_response(
                jsonify(Erro(status=400, msg="Id do produto inválido. Verifique os parêmetros enviados").dict())), 400

        cursor = conn.cursor()
        sql = f"DELETE FROM PRODUTOS WHERE ID = {produto['id']}"
        cursor.execute(sql)
        conn.commit()

        cursor.close()
        return make_response(
            jsonify(body))

    except Exception as e:
        return make_response(
            jsonify(Erro(status=500, msg="Houve um erro ao excluir o produto").dict())), 500


def retorna_produtos(id):
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome FROM PRODUTOS WHERE idSecao = ' + str(id))
    produtos = cursor.fetchall()
    cursor.close()

    return len(produtos)


def MontaPredicadoBuscaSecao(Secao):
    secao = Secao.json
    predicado = ""

    if (secao.get("nome", False)):
        if (secao['nome'] != "") and (len(secao['nome']) > 3):
            predicado += " and LOWER(nome) like '%" + \
                str(secao['nome']).lower() + "%'"

        if (secao.get("id", False)):
            if (type(int(secao['id']) != int)) and (secao['id'] != 0) and (secao['id'] != ""):
                predicado += " and id = " + str(secao['id']) + ""

        if (predicado == ""):
            predicado = " and id = 0"

        return predicado


def MontaPredicadoBuscaProduto(Produto):
    produto = Produto.json
    predicado = ""

    if (produto.get("id", False)):
        if (type(int(produto['id']) != int)) and (produto['id'] != 0) and (produto['id'] != ""):
            predicado += " and id = " + str(produto['id']) + ""

    if (produto.get("idSecao", False)):
        if (type(int(produto['idSecao']) != int)) and (produto['idSecao'] != 0) and (produto['idSecao'] != ""):
            predicado += " and idSecao = " + str(produto['idSecao']) + ""

    if (produto.get("nome", False)):
        if (produto['nome'] != "") and (len(produto['nome']) > 3):
            predicado += " and LOWER(nome) like '%" + \
                str(produto['nome']).lower() + "%'"

    if (predicado == ""):
        predicado = " and id = 0"

    return predicado


app.run()
