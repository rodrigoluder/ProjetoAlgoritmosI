#!/usr/bin/env python
import sys
from typing import List
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import pandas as pd

TODO_FILE = 'todo.txt'
ARCHIVE_FILE = 'done.txt'

RED = "\033[1;31m"
BLUE = "\033[0;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"
YELLOW = "\033[0;33m"

ADICIONAR = 'a'
REMOVER = 'r'
FAZER = 'f'
PRIORIZAR = 'p'
LISTAR = 'l'
DESENHAR = 'g'


class Compromisso:
    def __init__(self, data, hora, pri, desc, contexto, projeto):
        self.data = data
        self.hora = hora
        self.contexto = contexto
        self.projeto = projeto
        self.descricao = desc
        self.prioridade = pri

    def __str__(self):
        attributes = [self.data, self.hora, self.prioridade, self.descricao, self.contexto, self.projeto]
        while '' in attributes:
            attributes.remove('')
        qnt = len(attributes)
        if qnt == 1:
            string = attributes[0]
        else:
            string = attributes[0]
            for n in range(1, (qnt)):
                string += ' {}'.format(attributes[n])

        return string

# Imprime texto com cores. Por exemplo, para imprimir "Oi mundo!" em vermelho, basta usar
#
# printCores('Oi mundo!', RED)
# printCores('Texto amarelo e negrito', YELLOW + BOLD)

def printCores(texto, cor):
    print(cor + texto + RESET)


# Adiciona um compromisso aa agenda. Um compromisso tem no minimo
# uma descrição. Adicionalmente, pode ter, em caráter opcional, uma
# data (formato DDMMAAAA), um horário (formato HHMM), uma prioridade de A a Z,
# um contexto onde a atividade será realizada (precedido pelo caractere
# '@') e um projeto do qual faz parte (precedido pelo caractere '+'). Esses
# itens opcionais podem ser implementados como uma tupla, dicionário  ou objeto. A função
# recebe esse item através do parâmetro extras.
#
# extras tem como elementos data, hora, prioridade, contexto, projeto
#
def adicionar(descricao:Compromisso): # assinatura da função modificada do original, como sugerido pelo professor
    # não é possível adicionar uma atividade que não possui descrição.
    if descricao.descricao == '':
        return False

    else:
        #transformar objeto compromisso em string pra facilitar sua manipulação
        novaAtividade = str(descricao)

    # Escreve no TODO_FILE.
    try:
        fp = open(TODO_FILE, 'a')
        fp.write(novaAtividade + "\n")
    except IOError as err:
        print("Não foi possível escrever para o arquivo " + TODO_FILE)
        print(err)
        return False
    finally:
        fp.close()

    return True


# Valida a prioridade.
def prioridadeValida(pri:str):
    if type(pri) != str or len(pri) != 3 or pri[0] != '(' or pri[2] != ')' or not(65 <= ord(pri[1].upper()) <= 90):
        return False
    else:
        return True


# Valida a hora. Consideramos que o dia tem 24 horas, como no Brasil, ao invés
# de dois blocos de 12 (AM e PM), como nos EUA.
def horaValida(horaMin:str):
    if len(horaMin) != 4 or not soDigitos(horaMin):
        return False
    else:
        horaMin = [int(i) for i in horaMin]
        if horaMin[0] < 2 and horaMin[2] < 7:
            return True
        elif horaMin[0] == 2 and horaMin[1] <= 3 and horaMin[2] < 6:
            return True
        else:
            return False


# Valida datas. Verificar inclusive se não estamos tentando
# colocar 31 dias em fevereiro. Não precisamos nos certificar, porém,
# de que um ano é bissexto.
def dataValida(data:str):
    if len(data) != 8 or not soDigitos(data):
        return False
    else:
        dia = int(data[:2])
        mes = int(data[2:4])
        ano = int(data[4:])
        if mes in [1, 3, 5, 7, 8, 10, 12] and 0 < dia <= 31 and ano <= 2020:
            return True
        elif mes in [4, 6, 9, 11] and 0 < dia < 31 and ano <= 2020:
            return True
        elif mes == 2 and 0 < dia < 30 and ano <= 2020:
            return True
        else:
            return False


# Valida que o string do projeto está no formato correto.
def projetoValido(proj:str):
    if type(proj) != str or len(proj) < 2 or proj[0] != '+':
        return False
    else:
        return True


# Valida que o string do contexto está no formato correto.
def contextoValido(cont:str):
    if type(cont) != str or len(cont) < 2 or cont[0] != '@':
        return False
    else:
        return True


# Valida que a data ou a hora contém apenas dígitos, desprezando espaços
# extras no início e no fim.
def soDigitos(numero):
    if type(numero) != str:
        return False
    for x in numero:
        if x < '0' or x > '9':
            return False
    return True


# Dadas as linhas de texto obtidas a partir do arquivo texto todo.txt, devolve
# uma lista de tuplas contendo os pedaços de cada linha, conforme o seguinte
# formato:
#
# (descrição, prioridade, (data, hora, contexto, projeto))
#
# É importante lembrar que linhas do arquivo todo.txt devem estar organizadas de acordo com o
# seguinte formato:
#
# DDMMAAAA HHMM (P) DESC @CONTEXT +PROJ
#
# Todos os itens menos DESC são opcionais. Se qualquer um deles estiver fora do formato, por exemplo,
# data que não tem todos os componentes ou prioridade com mais de um caractere (além dos parênteses),
# tudo que vier depois será considerado parte da descrição.
def organizar(linhas:List[str]) -> List[Compromisso]:
    itens = []

    for l in linhas:
        data = ''
        hora = ''
        pri = ''
        desc = ''
        contexto = ''
        projeto = ''

        l = l.strip()  # remove espaços em branco e quebras de linha do começo e do fim
        tokens = l.split()  # quebra o string em palavras


        # Processa os tokens um a um, verificando se são as partes da atividade.
        # Por exemplo, se o primeiro token é uma data válida, deve ser guardado
        # na variável data e posteriormente removido a lista de tokens. Feito isso,
        # é só repetir o processo verificando se o primeiro token é uma hora. Depois,
        # faz-se o mesmo para prioridade. Neste ponto, verifica-se os últimos tokens
        # para saber se são contexto e/ou projeto. Quando isso terminar, o que sobrar
        # corresponde à descrição. É só transformar a lista de tokens em um string e
        # construir a tupla com as informações disponíveis.

        if dataValida(tokens[0]):
            data += tokens.pop(0)
        #else:
            #raise RuntimeError('Há alguma data fora da formatação DDMMAAAA: 2 numeros para descrever dia, 2 para mês e 4 para ano.')
        if horaValida(tokens[0]):
            hora += tokens.pop(0)
        #else:
            #raise RuntimeError('Há alguma hora fora da formatação HHMM: 2 numeros para descrever horas e 2 para minutos.')
        if prioridadeValida(tokens[0]):
            pri += tokens.pop(0)
        #else:
            #raise RuntimeError('Há alguma prioridade fora da formatação (P): uma letra de A a Z entre parênteses.')
        if projetoValido(tokens[-1]):
            projeto += tokens.pop(-1)
        #else:
            #raise RuntimeError('Há algum projeto fora da formatação +P: palavra ou letra seguida do +')
        if contextoValido(tokens[-1]):
            contexto += tokens.pop(-1)
        #else:
            #raise RuntimeError('Há algum contexto fora da formatação @C: palavra ou letra seguida do @')

        i = 0
        for t in tokens:
            #checar se tem erro e se nao tiver, construir descricao
            # se o primeiro token for so numeros de tamanho 5 ou 7, provavel que seja erro
            #if soDigitos(t) and (i == 0)  and len(t) in [ 5, 7]:
            desc += (' ' + t)
            i += 1
        desc = desc.strip()


        compromisso = Compromisso(data, hora, pri, desc, contexto, projeto)
        itens.append(compromisso)
    # A linha abaixo inclui em itens um objeto contendo as informações relativas aos compromissos
    # nas várias linhas do arquivo.
    # itens.append(...)

    return itens


#funcao p separar data
def separar_data(compromisso_data:str) -> (str,str,str):
    dia = compromisso_data[:2]
    mes = compromisso_data[2:4]
    ano = compromisso_data[4:]
    return dia, mes, ano

#funcao separar hora
def separar_hora(compromisso_hora:str) -> (str, str):
    hora = compromisso_hora[:2]
    mi = compromisso_hora[2:]

    return hora, mi

# funcao inverter data
def inverter_data(compromisso_data: str) -> str:
    dia, mes, ano = separar_data(compromisso_data)
    invertido = ano + mes + dia

    return invertido


# Datas e horas são armazenadas nos formatos DDMMAAAA e HHMM, mas são exibidas
# como se espera (com os separadores apropridados).
#
# Uma extensão possível é listar com base em diversos critérios: (i) atividades com certa prioridade;
# (ii) atividades a ser realizadas em certo contexto; (iii) atividades associadas com
# determinado projeto; (vi) atividades de determinado dia (data específica, hoje ou amanhã). Isso não
# é uma das tarefas básicas do projeto, porém.
def listar():
    try:
        fp = open(TODO_FILE, 'r', encoding='utf-8-sig') # encoding utilizado para retirar u'ffe no inicio do texto.txt
        tudo = fp.readlines()
    finally:
        fp.close()
    lista_compromissos = organizar(tudo)

    # Ordenar Por Prioridade
    todos_prioridade = ordenarPorPrioridade(lista_compromissos)

    # Ordenando por data e hora
    todos_prioridade = ordenarPorDataHora(todos_prioridade)

    # Imprimindo os compromissos
    i = 1
    for compp in todos_prioridade:
        # Deixando a impressao de data e hora mais bonita (com 30/09/2020 e '09h30m')
        data = compp.data
        hora = compp.hora
        nova_data = ''
        nova_hora = ''
        if data != '':
            dia, mes, ano = separar_data(data)
            nova_data = '{}/{}/{}'.format(dia, mes, ano)
        if hora != '':
            hora, mi = separar_hora(hora)
            nova_hora = '{}h{}m'.format(hora, mi)
        compp.data = nova_data
        compp.hora = nova_hora
        compp_str = str(i) + ' ' + str(compp)
        if compp.prioridade == '(A)':
            printCores(compp_str, RED)
        elif compp.prioridade == '(B)':
            printCores(compp_str, YELLOW)
        elif compp.prioridade == '(C)':
            printCores(compp_str, GREEN)
        elif compp.prioridade == '(D)':
            printCores(compp_str, BLUE)
        else:
            print(compp_str)
        i = int(i) + 1

        # retornando data depois de imprimir
        compp.data = data
        compp.hora = hora

    #return todos_prioridade


def ordenarPorDataHora(itens):
    i = 0
    while i < len(itens):
        j = 0
        while j < (len(itens)-1):
            # se tiverem prioridades iguais - aqui serve tanto para as que tem prioridade quanto para as que nao tem, ja
            # que no caso das que nao tem, as duas sao = ''
            # para comparar qual data eh mais cedo, inverte-se a data e ver qual eh menor
            if itens[j].prioridade == itens[j+1].prioridade:
                if itens[j].data == '':
                    data_i_inv = '1000000000'  # se nao tiver data, colocar numero alto para perder prioridade
                else:
                    data_i_inv = inverter_data(itens[j].data)
                if itens[j+1].data == '':
                    data_j_inv = '1000000000'  # o mesmo numero p y, casos nenhum dos dois tenha data
                else:
                    data_j_inv = inverter_data(itens[j+1].data)

                # compara as datas - se nas duas nao tiverem datas, elas serao iguais e passaremos para hora.
                if int(data_i_inv) > int(data_j_inv):
                    # se x for maior (mais tarde/depois que y), entao os dois trocam de lugar porque
                    # isso quer dizer y vem antes/mais cedo
                    temp = itens[j + 1]
                    itens[j + 1] = itens[j]
                    itens[j] = temp

                # se tiverem prioridades iguais (ou nao tiverem) e datas iguais (ou nao tiverem), comparamos as horas
                elif int(data_i_inv) == int(data_j_inv):
                    # comparacao pro hora se a data for a mesma, nao precisa inverter e mesma logica do de antes
                    # (numero menor, prioridade maior)

                    if itens[j].hora == '':
                        hora_i = '3000'
                    else:
                        hora_i = itens[j].hora
                    if itens[j+1].hora == '':
                        hora_j = '3000'
                    else:
                        hora_j = itens[j+1].hora

                    if int(hora_i) > int(hora_j):
                        temp = itens[j + 1]
                        itens[j + 1] = itens[j]
                        itens[j] = temp
            j += 1
        i += 1
    return itens


def ordenarPorPrioridade(itens:List[Compromisso]):
    # Ordenando por prioridade
    com_pri = dict()
    sem_pri = []
    for compromisso in itens:
        pri = compromisso.prioridade
        if pri != '':
            com_pri[compromisso] = ord(pri[1])
        else:
            sem_pri.append(compromisso)
    # o parametro key na funcao sorted aplica um funcao que eh utilizada para fazer a comparacao de ordem, no caso do dicionario
    # a funcao get pega os valores, entao a ordencao pode ser feita.
    com_pri_ordenados = []
    for comp in sorted(com_pri, key=com_pri.get):
        com_pri_ordenados.append(comp)
    # lista com todos, organizados por prioridade
    itens = com_pri_ordenados + sem_pri

    return itens


def fazer(num):
    try:
        fp = open(TODO_FILE, 'r', encoding='utf-8-sig')
        tudo = fp.readlines()
    finally:
        fp.close()
    lista_compromissos = organizar(tudo)

    # Ordenar Por Prioridade
    todos_prioridade = ordenarPorPrioridade(lista_compromissos)

    # Ordenando por data e hora
    lista_compromissos = ordenarPorDataHora(todos_prioridade)

    try:
        feito = lista_compromissos.pop(num-1)
    except IndexError as err:
        print('Erro de Index: Forneça um número referentes as atividades listadas')

    # escrevendo em outro artigo
    try:
        f = open(ARCHIVE_FILE, 'w+', encoding='utf-8-sig')
        f.write(str(feito) + '\n')
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, IsADirectoryError) as err:
        print('Erro na leitura do arquivo!')
    finally:
        f.close()

    remover(num)


def remover(numero:int):
    try:
        fp = open(TODO_FILE, 'r', encoding='utf-8-sig')
        tudo = fp.readlines()
    finally:
        fp.close()
    lista_compromissos = organizar(tudo)

    # Ordenar Por Prioridade
    todos_prioridade = ordenarPorPrioridade(lista_compromissos)

    # Ordenando por data e hora
    lista_compromissos = ordenarPorDataHora(todos_prioridade)


    # removendo compromisso
    del lista_compromissos[numero-1]

    # escrevendo por cima, mas agora sem a linha removida
    try:
        f = open(TODO_FILE, 'w+', encoding='utf-8-sig')
        for linha in lista_compromissos:
            f.write(str(linha) + '\n')
    finally:
        f.close()


# prioridade é uma letra entre A a Z, onde A é a mais alta e Z a mais baixa.
# num é o número da atividade cuja prioridade se planeja modificar, conforme
# exibido pelo comando 'l'.
def priorizar(num, prioridade):
    #checar prioridade
    prioridade = '(' + str(prioridade) + ')'
    if prioridadeValida(prioridade):
        nova_prioridade = prioridade
    else:
        raise RuntimeError('A prioridade inserida tem que ser uma letra entre A a Z')

    try:
        fp = open(TODO_FILE, 'r', encoding='utf-8-sig')
        tudo = fp.readlines()
    finally:
        fp.close()
    lista_compromissos = organizar(tudo)

    # Ordenar Por Prioridade
    todos_prioridade = ordenarPorPrioridade(lista_compromissos)

    # Ordenando por data e hora
    lista_compromissos = ordenarPorDataHora(todos_prioridade)

    try:
        compromisso = lista_compromissos[num-1]
        compromisso.prioridade = nova_prioridade
    except IndexError as err:
        print('Erro de Index: Forneça um número referentes as atividades listadas')

    #escrever por cima com prioridade troca
    try:
        f = open(TODO_FILE, 'w+', encoding='utf-8-sig')
        for linha in lista_compromissos:
            f.write(str(linha) + '\n')
    finally:
        f.close()


from collections import Counter
def desenhar(dias):
    #pegar compromissos de done.txt
    try:
        fp = open(ARCHIVE_FILE, 'r', encoding='utf-8-sig')
        tudo = fp.readlines()
    finally:
        fp.close()

    lista_compromissos = organizar(tudo)

    # Ordenar Por Prioridade
    todos_prioridade = ordenarPorPrioridade(lista_compromissos)

    # Ordenando por data e hora
    lista_compromissos = ordenarPorDataHora(todos_prioridade)

    if dias < 0:
        raise ValueError('Quantidade de dias nao pode ser negativo!')


    dt_lst = []
    for compromisso in lista_compromissos:
        dia, mes, ano = separar_data(compromisso.data)
        dt = dia + '-' + mes + '-' + ano
        dt = datetime.strptime(dt, '%d-%m-%Y')
        dt_lst.append(dt.date())


    y = Counter(dt_lst)
    datas_ordem = sorted(dt_lst) # ordernando

    datas_ordem = list(set(datas_ordem)) # tirando repeticoes, se houver
    if dias <= len(dt_lst):
        x = datas_ordem[len(datas_ordem)-dias:]
    else:
        x = datas_ordem[:]

    novo_y = dict()
    for key, value in y.items():
        if key in x:
            novo_y[key] = [value]

    x_y = pd.DataFrame.from_dict(novo_y) # Criar dataframe a partir de dicionario

    x_y = x_y.T
    x_y.rename(columns={0: "atividades"}, inplace=True)
    x_y.iloc[:].plot(y=0, color='red')
    plt.show()



# Esta função processa os comandos e informações passados através da linha de comando e identifica
# que função do programa deve ser invocada. Por exemplo, se o comando 'adicionar' foi usado,
# isso significa que a função adicionar() deve ser invocada para registrar a nova atividade.
# O bloco principal fica responsável também por tirar espaços em branco no início e fim dos strings
# usando o método strip(). Além disso, realiza a validação de horas, datas, prioridades, contextos e
# projetos.
def processarComandos(comandos):
    if comandos[1] == ADICIONAR:
        comandos.pop(0)  # remove 'agenda.py'
        comandos.pop(0)  # remove 'adicionar'
        itemParaAdicionar = organizar([' '.join(comandos)])[0]
        # itemParaAdicionar = Compromisso object
        adicionar(itemParaAdicionar)

    elif comandos[1] == LISTAR:
        listar()

    elif comandos[1] == REMOVER:
        remover(int(comandos[2]))

    elif comandos[1] == FAZER:
        fazer(int(comandos[2]))

    elif comandos[1] == PRIORIZAR:
        priorizar(int(comandos[2]), comandos[3])

    elif comandos[1] == DESENHAR:
        desenhar(int(comandos[2]))

    else:
        print("Comando inválido.")


# sys.argv é uma lista de strings onde o primeiro elemento é o nome do programa
# invocado a partir da linha de comando e os elementos restantes são tudo que
# foi fornecido em sequência. Por exemplo, se o programa foi invocado como
#
# python3 agenda.py a Mudar de nome.
#
# sys.argv terá como conteúdo
#
# ['agenda.py', 'a', 'Mudar', 'de', 'nome']
processarComandos(sys.argv)

#processarComandos(['agenda.py', 'a', 'Estudar'])
#processarComandos(['agenda.py', 'l'])
#processarComandos(['agenda.py', 'r', '21'])
#processarComandos(['agenda.py', 'l'])
#processarComandos(['agenda.py', 'p', '90', '(B)'])
#processarComandos(['agenda.py', 'l'])
#processarComandos(['agenda.py', 'f', '24'])
#processarComandos(['agenda.py', 'g', '8'])