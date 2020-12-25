import requests, bs4, json, os
import matplotlib.pyplot as plt
from datetime import date
from functools import total_ordering

os.chdir(r'put here the directory where you want the images to be saved')

def pra_numeric(valor):
    valor = valor.replace(',', '.')
    valor = float(valor)
    return valor

def new_graphic_30days(produto, valor):
    try:
        fig = plt.figure(figsize=(20, 9))
        plt.plot(datas_preços.datas[-30:], valor[-30:], linewidth=3)
    except ValueError as e:
        print(e)
    else:
        plt.title(f'Preço do {produto}', fontsize=24)
        plt.ylabel('Valor', fontsize=14)
        fig.autofmt_xdate()
        plt.grid(True)
        plt.savefig(f'{produto}table_30days.png')

def new_graphic_all_days(produto, valor):
    try:
        fig = plt.figure(figsize=(20, 9))
        plt.plot(datas_preços.datas, valor, linewidth=3)
    except ValueError as e:
        print(e)
    else:
        plt.title(f'Preço do {produto}', fontsize=24)
        plt.ylabel('Valor', fontsize=14)
        fig.autofmt_xdate()
        plt.grid(True)
        plt.savefig(f'{produto}table_all_days.png')

def all_graphic(dict_valores, cores):
    fig = plt.figure(figsize=(20, 9))
    milho = dict_valores['milho']
    trigo = dict_valores['trigo']
    soja = dict_valores['soja']
    plt.plot(datas_preços.datas, milho, color=f'{cores[0]}', linewidth=3, label=f'milho - ${milho[-1]}')
    plt.plot(datas_preços.datas, trigo, color=f'{cores[1]}', linewidth=3, label=f'trigo - ${trigo[-1]}')
    plt.plot(datas_preços.datas, soja, color=f'{cores[2]}', linewidth=3, label=f'soja - ${soja[-1]}')
    plt.title(f'Cotações', fontsize=24)
    plt.ylabel('Valor', fontsize=14)
    fig.autofmt_xdate()
    plt.grid(True)
    plt.legend()
    plt.savefig('cotacoestable.png')
    
@total_ordering
class Data:
    def __init__ (self, data):
        self.data = self.faz_data(data)
        self.data_ord = f'{data}'
    def __eq__ (self, other):
        return self.data == other.data
    def __lt__(self, other):
        return self.data < other.data
    def faz_data(self, data):
        dia, mes, ano = self.separa_datas(data)
        return date(ano, mes, dia)
    
    @staticmethod
    def separa_datas (str_data):
        data_list = []
        datavalue = str_data.split('-')
        for data in datavalue:
            data_list.append(int(data))
        return(data_list)


class Datas_Preços:
    def __init__(self, dados):
        self.datas = dados[0]
        self.preços = dados[1]
    
    def ordena(self):
        datas_desordenadas = self.datas
        self.datas = Dados.ordena_data(self.datas)
        self.preços = Dados.ordena_preços(self.datas, datas_desordenadas, self.preços)

    def add_valor(self, dados):
        try:
            data, *preços = dados
        except ValueError:
            return
        data = data.replace('/', '-')
        for data_passada in self.datas:
            if data == data_passada:
                break
        else:
            self.datas.append(data)
            self.preços.append(preços)
    
    def add_valores(self, lista_dados):
        for valores in lista_dados:
            self.add_valor(valores)
    
    def get_preço_produto(self):
        list_soja, list_milho, list_trigo = [], [], []
        for soja, milho, trigo in self.preços:
            list_soja.append(pra_numeric(soja))
            list_milho.append(pra_numeric(milho))
            list_trigo.append(pra_numeric(trigo))
        return (list_soja, list_milho, list_trigo)


class Dados:
    @staticmethod
    def baixa_dados(local='dados.json'):
        try:
            arq = open(local)
            dados = json.load(arq)
            return dados
        except Exception:
            return [[], []]

                
    @staticmethod
    def salva_dados(class_d_p, local='dados.json'):
        arq = open(local, 'w')
        json.dump([class_d_p.datas, class_d_p.preços], arq)
    
    @staticmethod
    def ordena_data(lista_datas):
        lista_ordenada = []
        lista_classes = []
        for data in lista_datas:
            data = Data(data)
            lista_classes.append(data)
        lista_classes = sorted(lista_classes)
        for data in lista_classes:
            lista_ordenada.append(data.data_ord)
        return lista_ordenada

    @staticmethod
    def ordena_preços(datas_ord, datas_desordenadas, preços):
        preços_ordenados = []
        for data_ord in datas_ord:
            local = datas_desordenadas.index(data_ord)
            preços_ordenados.append(preços[local])
        return preços_ordenados
    
    @staticmethod
    def chamada():
        request = requests.get('https://www.cotrirosa.com/servicos/cotacoes/')
        try:
            request.raise_for_status()
        except Exception:
            print('---ERROR---')
        soup = bs4.BeautifulSoup(request.text)
        valores = []
        for valor in range(2, 30):
            grupo_valores = []
            lista = soup.select(f'#tablepress-1 .row-hover .row-{valor} td')
            print(lista)
            for valor in lista:
                valor = valor.getText()
                grupo_valores.append(valor)
            valores.append(grupo_valores)
        return valores

valores = Dados.chamada()
datas_preços = Datas_Preços(Dados.baixa_dados())
datas_preços.add_valores(valores)
datas_preços.ordena()
soja, milho, trigo = datas_preços.get_preço_produto()
Dados.salva_dados(datas_preços)
dict_valores = {'soja': soja, 'milho': milho, 'trigo': trigo}

for produto, valor in dict_valores.items():
    new_graphic_30days(produto, valor)
    new_graphic_all_days(produto, valor)
all_graphic(dict_valores, ('#008000', '#000080', 'red'))
