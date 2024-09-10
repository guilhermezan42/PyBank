from datetime import datetime
import os
import json
from tinydb import TinyDB, Query
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Transacoes:
    def __init__(self):
        self.diretorio_pai = os.path.dirname(os.path.abspath(__file__))
        caminho_banco_dados = os.path.join(os.path.dirname(self.diretorio_pai), 'banco_de_dados.json')
        self.db = TinyDB(caminho_banco_dados)
        self.verificar_debitos()
        
    def obter_todos_clientes(self):
        clientes = self.db.table('_default').all()
        return [cliente.doc_id for cliente in clientes]

    def verificar_debitos(self):
        data_atual = datetime.now().strftime("%d/%m/%Y")

        clientes = self.obter_todos_clientes()
        
        for cliente_id in clientes:
            cliente = self.obter_cliente_por_id(str(cliente_id))
            # print(cliente)
            if cliente['solicita_credito'] == 1:
                if cliente['valor_total_em_debito'] == 0:
                    self.db.update({'solicita_credito': 0}, doc_ids=[cliente_id])
                    self.db.update({'valor_solicitado': 0}, doc_ids=[cliente_id])
                    self.db.update({'dia_para_cobranca': ""}, doc_ids=[cliente_id])
                    self.db.update({'valor_parcelas': 0}, doc_ids=[cliente_id])
                    self.db.update({'valor_total_em_debito': 0}, doc_ids=[cliente_id])
                else:
                    dia_cobranca = cliente['dia_para_cobranca']
                    data_prox_fatura = datetime.strptime(dia_cobranca, "%d/%m/%Y") + timedelta(days=30)
                    data_formatada = data_prox_fatura.strftime("%d/%m/%Y")
                    # print(data_atual, data_formatada, dia_cobranca)
                    if datetime.strptime(dia_cobranca, "%d/%m/%Y").date() <= datetime.strptime(data_atual, "%d/%m/%Y").date():
                        valor_parcela = cliente['valor_parcelas']
                        if self.debitar_conta(cliente_id, valor_parcela):
                            self.registrar_transacao('Débito automático', valor_parcela, conta_origem=cliente_id)
                            self.atualizar_dados(cliente_id, valor_parcela, dia_cobranca=data_formatada)

    def atualizar_dados(self, cliente_id, valor_parcela, dia_cobranca):
        cliente = self.db.get(doc_id=cliente_id)
        debito = cliente['valor_total_em_debito']
        valor_atualizado = debito - valor_parcela
        self.db.update({'valor_total_em_debito': valor_atualizado}, doc_ids=[cliente_id])
        self.db.update({'dia_para_cobranca': dia_cobranca}, doc_ids=[cliente_id])

    def obter_cliente_por_id(self, cliente_id):
        cliente = self.db.table('_default').get(doc_id=cliente_id)
        return cliente

    def debitar_conta(self, conta, valor):
        cliente = self.db.get(doc_id=conta)
        saldo = cliente['saldo']
        # if saldo >= valor and valor > 0: Cancelado, agora vai debitar e deixar valor negativo do saldo se tiver como 0
        novo_saldo = saldo - valor
        novo_saldo = round(novo_saldo, 2)
        self.registrar_transacao('Débito em conta', valor, conta_origem=conta)
        self.db.update({'saldo': novo_saldo}, doc_ids=[conta])
        return True

    # RESGISTRAR TRANSAÇÕES: OK#
    def registrar_transacao(self, tipo, valor, conta_origem=None, conta_destino=None):
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Recupera as transações existentes do banco de dados e cria uma nova transação
        transacoes = self.db.get(doc_id=conta_origem)['transacoes']
        nova_transacao = {
            'data': data_atual,
            'tipo': tipo,
            'valor': valor,
            'conta_origem': conta_origem,
            'conta_destino': conta_destino
        }
        
        # Verifica se transacoes é uma lista e adiciona a nova transação à lista
        if isinstance(transacoes, list):
            transacoes.append(nova_transacao)
        else:
            transacoes = json.loads(transacoes) if transacoes else []
            transacoes.append(nova_transacao)
        transacoes_str = json.dumps(transacoes)
        self.db.update({'transacoes': transacoes_str}, doc_ids=[conta_origem])


    # EXTRATO: OK #
    def extrato(self, cliente_id):
        cliente = self.db.get(doc_id=cliente_id)
        transacoes_extrato = []
        
        if cliente and 'transacoes' in cliente:
            transacoes_json = cliente['transacoes']
            
            if transacoes_json:
                transacoes = json.loads(transacoes_json)
                
                for transacao in transacoes:
                    data = transacao['data']
                    tipo = transacao['tipo']
                    valor = transacao['valor']
                    conta_origem = transacao['conta_origem']
                    conta_destino = transacao['conta_destino']

                    if conta_destino is None:
                        extrato_str = "Data: " + data + "\n" + "Tipo: " + tipo + "\n" + "Valor: R$ " + str(valor) + "\n---------------------"
                        transacoes_extrato.append(extrato_str)
                    else:
                        cliente_destino = self.db.get(doc_id=conta_destino)
                        if tipo == 'Pagamento recebido':
                            extrato_str = "Data: " + data + "\n" + "Tipo: " + tipo + "\n" + "Valor: R$ " + str(valor) + "\n" + "Transferido por: " + cliente_destino['nome'] + "\n---------------------"
                        else:
                            extrato_str = "Data: " + data + "\n" + "Tipo: " + tipo + "\n" + "Valor: R$ " + str(valor) + "\n" + "Transferido para: " + cliente_destino['nome'] + "\n---------------------"
                        transacoes_extrato.append(extrato_str)

        return transacoes_extrato

    
    # SAQUE: OK #
    def saque(self, conta, valor):
        cliente = self.db.get(doc_id=conta)
        saldo = cliente['saldo']

        if saldo >= valor and valor > 0:
            novo_saldo = saldo - valor
            novo_saldo = round(novo_saldo, 2)
            # print(novo_saldo, saldo, valor)
            self.registrar_transacao('Saque', valor, conta_origem=conta)
            self.db.update({'saldo': novo_saldo}, doc_ids=[conta])
            return True
        else:
            return False

    # DEPOSITO: OK #
    def deposito(self, conta, valor):
        cliente = self.db.get(doc_id=conta)
        saldo = cliente['saldo']

        if valor > 0:
            novo_saldo = saldo + valor
            novo_saldo = round(novo_saldo, 2)
            # print(novo_saldo, saldo, valor)
            self.registrar_transacao('Depósito', valor, conta_origem=conta)
            self.db.update({'saldo': novo_saldo}, doc_ids=[conta])
            return True
        else:
            return False


    def realizar_pagamento(self, conta_origem, conta_destino, valor):
        if valor >= 0 and conta_origem != conta_destino: 
            cliente_origem = self.db.get(doc_id=conta_origem)
            cliente_destino = self.db.get(doc_id=conta_destino)
            
            saldo_origem = cliente_origem['saldo']
            saldo_destino = cliente_destino['saldo']
        
            if saldo_origem >= valor:
                novo_saldo_origem = saldo_origem - valor
                novo_saldo_destino = saldo_destino + valor
                
                self.registrar_transacao('Pagamento', valor, conta_origem, conta_destino)
                self.db.update({'saldo': novo_saldo_origem}, doc_ids=[conta_origem])
                self.db.update({'saldo': novo_saldo_destino}, doc_ids=[conta_destino])
                
                self.registrar_transacao('Pagamento recebido', valor, conta_destino, conta_origem)

                return True
            else:
                return False
        else:
            return False
    
class CadastroCliente:
    def __init__(self):
        self.diretorio_pai = os.path.dirname(os.path.abspath(__file__))
        caminho_banco_dados = os.path.join(os.path.dirname(self.diretorio_pai), 'banco_de_dados.json')
        self.db = TinyDB(caminho_banco_dados)


    def salvar_cadastro(self, nome, telefone, data_nascimento, cpf_ou_cnpj, endereco, renda, senha):
        data_atual = datetime.now().date()
        data_nascimento_check = datetime.strptime(data_nascimento, "%d/%m/%Y").date()
        idade = data_atual.year - data_nascimento_check.year

        if (data_atual.month, data_atual.day) < (data_nascimento_check.month, data_nascimento_check.day):
            idade -= 1
        if idade < 18:
            return False
        else:
            # Salvar os dados no banco de dados
            self.db.insert({
                'cadastro_nivel': 1,
                'nome': nome,
                'telefone': telefone,
                'data_nascimento': data_nascimento,
                'cpf_ou_cnpj': cpf_ou_cnpj,
                'endereco': endereco,
                'renda': renda,
                'senha': senha,
                'transacoes': '',
                'saldo': 0,
                'solicita_credito': 0,
                'valor_solicitado': 0,
                'dia_para_cobranca': '',
                'valor_parcelas': 0,
                'valor_total_em_debito': 0,
                'solicita_exclusao': 0
            })
            return True
    
class SolicitaCredito:
    def __init__(self):
        self.diretorio_pai = os.path.dirname(os.path.abspath(__file__))
        caminho_banco_dados = os.path.join(os.path.dirname(self.diretorio_pai), 'banco_de_dados.json')
        self.db = TinyDB(caminho_banco_dados)

    def solicitacao(self, conta, valor, data):
        cliente = self.db.get(doc_id=conta)
        if cliente['solicita_credito'] == 1: return False
        else:
            cpf_cnpj = cliente['cpf_ou_cnpj']
            if len(cpf_cnpj) == 11:
                max_parcela = cliente['renda']
            elif len(cpf_cnpj) == 14:
                max_parcela = cliente['renda']*10
            # print(max_parcela)
            montante = valor * 1.0149 ** 10
            valor_parcelas = montante / 10
            valor_parcelas = round(valor_parcelas,2)
            a_pagar = valor_parcelas*10

            if max_parcela < valor_parcelas:
                return False
            else:
                self.db.update({'solicita_credito': 1}, doc_ids=[conta])
                self.db.update({'valor_solicitado': valor}, doc_ids=[conta])
                self.db.update({'dia_para_cobranca': data}, doc_ids=[conta])
                self.db.update({'valor_parcelas': valor_parcelas}, doc_ids=[conta])
                self.db.update({'valor_total_em_debito': a_pagar}, doc_ids=[conta])

        return True

class VerificarBanco:
    def __init__(self):
        self.diretorio_pai = os.path.dirname(os.path.abspath(__file__))
        caminho_banco_dados = os.path.join(os.path.dirname(self.diretorio_pai), 'banco_de_dados.json')
        self.db = TinyDB(caminho_banco_dados)
        self.verificar_banco()
    # Se o banco de dados for apagado, insere dados padrão para o gerente
    def verificar_banco(self):
        if len(self.db) == 0:
            dados_padrao = {
                        "cadastro_nivel": 2,
                        "nome": "Clarice Bianca Bernardes",
                        "telefone": "(88) 99881-4748",
                        "data_nascimento": "26/02/1973",
                        "cpf_ou_cnpj": "11111111111",
                        "endereco": "Rua Clara Alves de Oliveira, Bastiana, Iguatu CE",
                        "renda": 1789.0,
                        "senha": "123456",
                        "transacoes": "",
                        "saldo": 106.5,
                        "solicita_credito": 1,
                        "valor_solicitado": 1500.0,
                        "dia_para_cobranca": "15/06/2023",
                        "valor_parcelas": 173.91,
                        "valor_total_em_debito": 1739.1,
                        "solicita_exclusao": 0,
            }
            self.db.insert(dados_padrao)
            return True