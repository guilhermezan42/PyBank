import os, subprocess, tkinter as tk
from tkinter import *
from package.classes import Transacoes, SolicitaCredito, VerificarBanco
from PIL import ImageTk, Image
from tinydb import TinyDB, Query
import tkinter.messagebox as messagebox
from datetime import datetime, timedelta

azul = '#044cac'
azul_escuro = '#043c84'
class PYBANKApp:
    def __init__(self):
        self.diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        self.db = TinyDB(self.diretorio_atual + '/banco_de_dados.json')

        self.janela = tk.Tk()
        self.janela.geometry("700x900")
        self.janela.title("Pybank")
        self.janela.resizable(False, False)

        imagem = Image.open(self.diretorio_atual + "/images/pybank.png")
        imagem_tk = ImageTk.PhotoImage(imagem)
        label = tk.Label(self.janela, image=imagem_tk).place(x=0, y=0, relwidth=1, relheight=1)

        ######################################
        #         INÍCIO DAS FUNÇÕES         #
        ######################################

        def botoes():
            button_1 = tk.Button(self.janela, text= '1', width=2).place(x=113, y=404)
            button_2 = tk.Button(self.janela, text= '2', width=2).place(x=166, y=404)
            button_3 = tk.Button(self.janela, text= '3', width=2).place(x=219, y=404)
            button_4 = tk.Button(self.janela, text= '4', width=2).place(x=113, y=440)
            button_5 = tk.Button(self.janela, text= '5', width=2).place(x=166, y=440)
            button_6 = tk.Button(self.janela, text= '6', width=2).place(x=219, y=440)
            button_7 = tk.Button(self.janela, text= '7', width=2).place(x=113, y=476)
            button_8 = tk.Button(self.janela, text= '8', width=2).place(x=166, y=476)
            button_9 = tk.Button(self.janela, text= '9', width=2).place(x=219, y=476)
            button_0 = tk.Button(self.janela, text= '0', width=2).place(x=166, y=512)            

       ################################################################################################# INÍCIO DA FUNÇÃO REALIZAR CADASTRO: OK ##########################################
        def realizar_cadastro():
            subprocess.run(['python', self.diretorio_atual +'/cadastro.py'])

        ################################################################################################ INÍCIO DA FUNÇÃO LOGIN: OK #####################################################
        def fazer_login():
            imagem_tk = ImageTk.PhotoImage(imagem)
            label = tk.Label(self.janela, image=imagem_tk)
            label.place(x=0, y=0, relwidth=1, relheight=1)

            def mudar_imagem():
                imagem_original = Image.open(self.diretorio_atual + "/images/PYBANK.png")
                nova_imagem = imagem_original.resize((700, 900))
                nova_imagem = ImageTk.PhotoImage(nova_imagem)
                label.config(image=nova_imagem)
                label.image = nova_imagem    
            mudar_imagem()

            def logar():
                cpf = entry_cpf_login.get()
                senha = entry_senha.get()
                
                for indice, cliente in enumerate(self.db.all()):
                    if cliente['cpf_ou_cnpj'] == cpf and cliente['senha'] == senha and cliente['solicita_exclusao'] == 0:
                        label_cliente['text'] = 'Login realizado com sucesso!'
                        label_cliente['bg'] = '#5FC0E6'
                        cliente_id = indice+1
                        usuario = self.db.get(doc_id=cliente_id)
                        abrir_menu(cliente_id)                   
                    else:
                        label_cliente['text'] = 'CPF ou senha inválidos!'
                        label_cliente['bg'] = '#2475e0'
            
             
            label_cpf_login= tk.Label(self.janela, text= 'CPF:', height=1, width= 4, background="#044cac", fg="#FFFFFF",font= 'Arial 10 bold')
            label_cpf_login.pack()
            label_cpf_login.place(x=275, y=400)
            entry_cpf_login = tk.Entry(self.janela)
            entry_cpf_login.pack()
            entry_cpf_login.place(x=275, y=420)

            label_senha = tk.Label(self.janela, text='Senha:', background="#044cac",fg="#FFFFFF",font= 'Arial 10 bold')
            label_senha.pack()
            label_senha.place(x=275, y=450)
            entry_senha = tk.Entry(self.janela, show='*')
            entry_senha.pack()
            entry_senha.place(x=275, y=470)

            
            button_enter = tk.Button(self.janela, text= 'Enter', command=logar,fg="#FFFFFF" ,bg="#043c84",font= 'Arial 10 bold', activebackground="#0c4895",
                                      activeforeground= "#f1f0f0",cursor='hand2',relief= FLAT, padx=10, pady=5).place(x=310, y=500)
       
            label_cliente = tk.Label(self.janela, background="#044cac",font='Arial 10 bold',padx= 5, pady=5,border=1,relief="flat")
            label_cliente.place(x=100, y=350)

       ######################################################################################################## # FUNÇÃO EXTRATO ####################################################
        def abrir_extrato(cliente_id):
            imagem_tk = ImageTk.PhotoImage(imagem)
            label = tk.Label(self.janela, image=imagem_tk)
            label.place(x=0, y=0, relwidth=1, relheight=1)
            nova_imagem = Image.open(self.diretorio_atual + "/images/PYBANK_interface.png")
            nova_imagem = ImageTk.PhotoImage(nova_imagem)
            label.config(image=nova_imagem)
            label.image = nova_imagem
            cliente = self.db.get(doc_id=cliente_id)

            def atualiza_tela():
                imagem = Image.open(self.diretorio_atual + "/images/PYBANK_interface.png")
                nova_imagem = ImageTk.PhotoImage(imagem)
                label.configure(image=nova_imagem)
                label.image = nova_imagem
                mensagem_label.config(text="Comprovante impresso!", font=('normal', 14))
                
            transacoes_extrato = Transacoes()

            mensagem_label = tk.Label(self.janela, text="", background="white", font=('normal', 10), justify="left")
            mensagem_label.pack()
            mensagem_label.place(x=120, y=170)

            def extrato(cliente_id):
                nonlocal cliente
                cliente = self.db.get(doc_id=cliente_id)
                transacoes_cliente = transacoes_extrato.extrato(cliente_id)
                if transacoes_cliente:
                    atualiza_tela()
                    janela_extrato = tk.Toplevel(self.janela)
                    janela_extrato.title("Extrato impresso")
                    janela_extrato.geometry("300x400")
                    
                    frame_extrato = tk.Frame(janela_extrato)
                    frame_extrato.pack(fill=tk.BOTH, expand=True)
                    
                    scrollbar = tk.Scrollbar(frame_extrato)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    
                    # Cria um widget Canvas para o frame do extrato
                    canvas = tk.Canvas(frame_extrato, yscrollcommand=scrollbar.set)
                    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                    
                    # Associa a barra de rolagem ao canvas
                    scrollbar.config(command=canvas.yview)
                    
                    # Cria um frame interno para as transações
                    inner_frame = tk.Frame(canvas)
                    canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)
                    
                    for i, transacao in enumerate(transacoes_cliente):
                        label_transacao = tk.Label(inner_frame, text=transacao, font=('normal', 10), justify="left")
                        label_transacao.pack(anchor=tk.W)
                    
                    # Atualiza o tamanho do canvas
                    canvas.update_idletasks()
                    canvas.config(scrollregion=canvas.bbox(tk.ALL))
                    
                else:
                    mensagem_label.config(text="Não há transações para exibir.")
                    mensagem_label.place(x=50, y=345)

            label_cabecalho = tk.Label(self.janela, text=cliente["nome"].split()[0] + ", aqui você pode olhar seu extrato.\nSeu saldo atual é: R$ " + str(cliente['saldo']),
                                        font=('Arial', 18),fg=azul, bg="white",justify="left").place(x=50, y=210)  
            

            
            button_enter = tk.Button(self.janela, text='Abrir Extrato',  width=13, height=4,fg="white", bg="#004aad",font= "Arial 12 bold",relief=RIDGE , command=lambda: extrato(cliente_id)).place(x=350, y=400)
            button_asterisco = tk.Button(self.janela, text= 'Voltar',  width=13, height=4,fg="white", bg="#004aad",font= "Arial 12 bold" ,relief=RIDGE , command=lambda: abrir_menu(cliente_id)).place(x=200, y=400)
           

        ############################################################################################################## FUNÇÃO DEPÓSITO> OK ##########################################################
        def abrir_deposito(cliente_id):
            imagem_tk = ImageTk.PhotoImage(imagem)
            label = tk.Label(self.janela, image=imagem_tk)
            label.place(x=0, y=0, relwidth=1, relheight=1)
            nova_imagem = Image.open(self.diretorio_atual + "/images/PYBANK_interface.png")
            nova_imagem = ImageTk.PhotoImage(nova_imagem)
            label.config(image=nova_imagem)
            label.image = nova_imagem
            cliente = self.db.get(doc_id=cliente_id)

            def atualiza_tela(valor):
                nonlocal cliente                                                                                                                    
                cliente = self.db.get(doc_id=cliente_id)
                label_cabecalho = tk.Label(self.janela, text=cliente["nome"] + ",\nSeu saldo é:R$ " + str(cliente['saldo']) + '\n\nREALIZAR DEPÓSITO:', font=('normal', 16), fg=azul, bg="white", justify="left").place(x=50, y=170)
                imagem = Image.open(self.diretorio_atual + "/images/PYBANK_interface.png")
                nova_imagem = ImageTk.PhotoImage(imagem)
                label.configure(image=nova_imagem)
                label.image = nova_imagem
                
            transacao = Transacoes()

            mensagem_label = tk.Label(self.janela, text="",fg="white", bg="white", font=('normal', 11), justify="left")
            mensagem_label.pack()
            mensagem_label.place(x=50, y=330)

            def depositar(cliente_id):
                nonlocal cliente
                cliente = self.db.get(doc_id=cliente_id)
                valor = entry_valor.get()
                if valor:
                    valor = float(valor)
                    print(valor)
                    if transacao.deposito(cliente_id, valor):
                        atualiza_tela(valor)
                        mensagem_label.config(text="Seu depósito de R$" + str(valor) + " foi realizado com sucesso.\nSeu saldo atual é: R$ " + str(cliente['saldo']),bg=azul)
                    else:
                        mensagem_label.config(text="Erro. Este valor é inválido para depósitos.\nSeu saldo atual é: R$ " + str(cliente['saldo']) , bg=azul)
                      

            label_cabecalho = tk.Label(self.janela, text=cliente["nome"] + ",\nSeu saldo é:R$ " + str(cliente['saldo']) + '\n\nREALIZAR DEPÓSITO:', font=('normal', 16), justify="left",fg=azul, bg="white",).place(x=50, y=170)
            
                                                                
            label_valor= tk.Label(self.janela, text= 'Valor:',fg='black', bg="white",font=('Arial', 10,'bold')).place(x=50, y=280)
            entry_valor = tk.Entry(self.janela, bg='#f2f3f4')
            entry_valor.pack()
            entry_valor.place(x=50, y=300)

          
            button_enter = tk.Button(self.janela, text='Confirmar\nDepósito', width=13, height=4,fg="white", bg="#004aad",font= "Arial 12 bold",relief=RIDGE, command=lambda: depositar(cliente_id)).place(x=350, y=500)
            button_asterisco = tk.Button(self.janela, text= 'Voltar',  width=13, height=4,fg="white", bg="#004aad",font= "Arial 12 bold",relief=RIDGE, command=lambda: abrir_menu(cliente_id)).place(x=200, y=500)
            

        ############################################################################################################# INÍCIO DA FUNÇÃO SOLICITAR CRÉDITO#
        def solicita_credito(cliente_id):
            imagem_tk = ImageTk.PhotoImage(imagem)
            label = tk.Label(self.janela, image=imagem_tk)
            label.place(x=0, y=0, relwidth=1, relheight=1)
            nova_imagem = Image.open(self.diretorio_atual + "/images/PYBANK_interface.png")
            nova_imagem = ImageTk.PhotoImage(nova_imagem)
            label.config(image=nova_imagem)
            label.image = nova_imagem
            cliente = self.db.get(doc_id=cliente_id)
            
          

            solicitar = SolicitaCredito()

            label_valor = tk.Label(self.janela, text='Valor:', fg='black', bg="white",font=('Arial', 10,'bold'))
            label_valor.pack()
            label_valor.place(x=50, y=300)
            entry_valor = tk.Entry(self.janela, background="#f2f3f4")
            entry_valor.pack()
            entry_valor.place(x=50, y=320)

            label_credito_situacao = tk.Label(self.janela, text="", font=("Arial", 10), justify="left", fg="white", bg="white")
            label_credito_situacao.pack()
            label_credito_situacao.place(x=50, y=345)

        

            label_cabecalho = tk.Label(self.janela, text="Olá, " + cliente["nome"] + "\nfaça o seu pedido." + '\n\nPEDIDO DE CRÉDITO:',  font=('normal', 16), fg=azul, bg="white", justify="left").place(x=50, y=170)
            button_asterisco = tk.Button(self.janela, text= 'Voltar', width=13, height=4,fg="white", bg="#004aad",font= "Arial 12 bold",relief=RIDGE, command=lambda: abrir_menu(cliente_id)).place(x=200, y=500)

            def enviar_solicitacao(cliente_id):
                print(cliente_id)
                valor = float(entry_valor.get())
                data_atual = datetime.now().date()
                data_prox_fatura = data_atual + timedelta(days=30)
                data_formatada = data_prox_fatura.strftime("%d/%m/%Y")
                if valor <= 0:
                    label_credito_situacao.configure(text="O valor da solicitação não pode ser menor ou igual a 0.",bg=azul)
                else:
                    if solicitar.solicitacao(cliente_id, valor, data_formatada):
                        label_credito_situacao.configure(text="Parabéns, seu crédito foi aprovado!\nSua próxima fatura será debitada em 30 dias.",bg=azul)
                    else: label_credito_situacao.configure(text="Que pena! Não foi dessa vez.\nSe você já fez um pedido de crédito, outra liberação\nsó ocorrerá quando não houver mais débitos a serem feitos.",bg=azul)

            button_enter = tk.Button(self.janela, text='Confirmar\nSolicitaçao',width=13, height=4,fg="white", bg="#004aad",font= "Arial 12 bold",relief=RIDGE, command=lambda: enviar_solicitacao(cliente_id)).place(x=350, y=500)
            

        ########################################################################################################### INÍCIO DA FUNÇÃO PAGAMENTO
        def realizar_pagamento(cliente_id):
            imagem_tk = ImageTk.PhotoImage(imagem)
            label = tk.Label(self.janela, image=imagem_tk)
            label.place(x=0, y=0, relwidth=1, relheight=1)
            nova_imagem = Image.open(self.diretorio_atual + "/images/PYBANK_interface.png")
            nova_imagem = ImageTk.PhotoImage(nova_imagem)
            label.config(image=nova_imagem)
            label.image = nova_imagem
            cliente = self.db.get(doc_id=cliente_id)
            
            label_cabecalho = tk.Label(self.janela, text=cliente["nome"] + ", seu saldo é:\nR$ " + str(cliente['saldo']) + '\n\nREALIZAR TRANSFERÊNCIA:', justify=LEFT, font=('normal', 16), fg=azul, bg="white",).place(x=50, y=170)

            def pagamento(cliente_id):
                cpf = conta_destino_entry.get()
                valor = float(valor_entry.get())
                valor_str = valor_entry.get()
                valor_str = valor_str.replace(',','.')
                valor = float(valor_str)
                
                if valor <= 0:
                    mensagem_label = tk.Label(self.janela, text='Valor inválido', background="#004aad")
                    mensagem_label.place(x=50, y=365)
                    return False
                
                for indice, destinatario in enumerate(self.db.all()):
                    if destinatario['cpf_ou_cnpj'] == cpf:
                        destinatario_id = indice+1
                        destinatario = self.db.get(doc_id=destinatario_id)
                        transacao = Transacoes()
                        
                        if transacao.realizar_pagamento(cliente_id, destinatario_id, valor):
                            cliente = self.db.get(doc_id=cliente_id)
                            label_cabecalho = tk.Label(self.janela, text=cliente["nome"] + ", seu saldo é:\nR$ " + str(cliente['saldo']) + '\n\nREALIZAR TRANSFERÊNCIA:', justify=LEFT, font=('normal', 16), fg=azul, bg="white",).place(x=50, y=170)
                            mensagem_label = tk.Label(self.janela, text='Pagamento realizado com sucesso', background="#004aad")
                            mensagem_label.place(x=50, y=365)
                            cliente = self.db.get(doc_id=cliente_id)
                            return True
                        else:
                            mensagem_label = tk.Label(self.janela, text='ERRO! Transação não realizada',background="#004aad")
                            mensagem_label.place(x=50, y=365)
                            return False
            
            conta_destino_label = tk.Label(self.janela, text="CPF/CNPJ da conta de destino:", background="#FFF",font=('Arial', 10,'bold'))
            conta_destino_label.place(x=50, y=280)
            conta_destino_entry = tk.Entry(self.janela, background="#f2f3f4")
            conta_destino_entry.place(x=50, y=300)

            valor_label = tk.Label(self.janela, text="Valor do pagamento:", fg='black', bg="white",font=('Arial', 10,'bold'))
            valor_label.place(x=50, y=320)
            valor_entry = tk.Entry(self.janela, background="#f2f3f4")
            valor_entry.place(x=50, y=340)            
            
        
            button_enter = tk.Button(self.janela, text='Confirmar\nTransferência',  width=13, height=4,fg="white", bg="#004aad",font= "Arial 12 bold",relief=RIDGE, command= lambda: pagamento(cliente_id))
            button_enter.place(x=350, y=500)
            button_asterisco = tk.Button(self.janela, text= 'Voltar',width=13, height=4,fg="white", bg="#004aad",font= "Arial 12 bold",relief=RIDGE, command=lambda: abrir_menu(cliente_id)).place(x=200, y=500)
            
        # INÍCIO DA FUNÇÃO MENU #
        def abrir_menu(cliente_id):
            imagem = Image.open(self.diretorio_atual + "/images/pybank_interface.png")
            imagem_tk = ImageTk.PhotoImage(imagem)
            label = tk.Label(self.janela, image=imagem_tk)
            label.place(x=0, y=0, relwidth=1, relheight=1)
            cliente = self.db.get(doc_id=cliente_id)

            label_cabecalho = tk.Label(self.janela, text='Olá, ' + cliente["nome"] + ".", font=('Arial', 18), fg= azul, bg="white" , justify="center", pady=10).place(x=50, y=170)
            label_saldo = tk.Label(self.janela, text="SALDO:\nR$ " + str(cliente['saldo']), font=('Arial', 30), fg=azul, bg="white" , justify="left").place(x=50, y= 220)

           

            def sair():
                self.janela.destroy()

            

            button_1 = tk.Button(self.janela, text= 'Extrato',font= "Arial 12 bold" ,width=13, height=4, fg="white", bg="#004aad",relief=RIDGE, command=lambda: abrir_extrato(cliente_id)).place(x=50, y=400)
            button_3 = tk.Button(self.janela, text= 'Deposito',font= "Arial 12 bold" , width=13, height=4, fg="white",bg="#004aad", justify="left",relief=RIDGE, command=lambda: abrir_deposito(cliente_id)).place(x=200, y=400)
            button_4 = tk.Button(self.janela, text= 'Transferência \n Bancária',font= "Arial 12 bold" , width=13, height=4,fg="white", bg="#004aad",relief=RIDGE, command=lambda: realizar_pagamento(cliente_id)).place(x=350, y=400)
            button_5 = tk.Button(self.janela, text= 'Solicitar Crédito',font= "Arial 12 bold" , width=13, height=4,fg="white", bg="#004aad",relief=RIDGE, command=lambda: solicita_credito(cliente_id)).place(x=500, y=400)
            button_6 = tk.Button(self.janela, text= 'Sair',font= "Arial" , width=6, height=2,fg="white", bg="#004aad",relief=RIDGE, command=sair).place(x=625, y=840)

            self.janela.mainloop()
            
                
        def realizar_cadastro():
            mensagem = "Vá até o banco para que o gerente faça seu cadastro."
            # Exibe a mensagem em uma caixa de diálogo
            tk.messagebox.showinfo("PYBANK", mensagem)
    
            
        while True:
            opcoes_texto = 'Bem-vindo ao PYBANK.\n\nEscolha uma das opções abaixo:'
            verificar_debitos = Transacoes()
            verificar_debitos.verificar_debitos()
            verificar_banco = VerificarBanco()
            verificar_banco.verificar_banco()
            label_opcoes = tk.Label(self.janela, text=opcoes_texto, font=("Arial", 16 ), justify="left", bg= azul, wraplength=300, foreground= '#FFF').place(x=215, y=325)


            button_1 = tk.Button(self.janela, text= 'Login',width= 10,bg=azul_escuro,relief=RIDGE,command=fazer_login,font=("Arial", 10, 'bold' ),
                                 foreground= '#FFF',height=2,activebackground="#0c4895",activeforeground= "#f1f0f0",cursor='hand2').place(x=250, y=460)
            button_2 = tk.Button(self.janela, text= 'Cadastre-se',width= 10,bg=azul_escuro,font=("Arial", 10,'bold' ),foreground= '#FFF',
                                  command= realizar_cadastro, height=2,activebackground="#0c4895",activeforeground= "#f1f0f0",cursor='hand2',relief=RIDGE).place(x=350, y=460)

            self.janela.mainloop()

            

if __name__ == "__main__":
    app = PYBANKApp()
    app.iniciar()