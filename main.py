"""Sistema de Gestão da Estação Ferroviária "Mira Monte" """
import os
import csv
from entidades import *
from operacoes import executar_operacoes, gerir_passageiros

# FUNÇÕES DE CARREGAMENTO DE DADOS

def ler_parametros(diretorio):
    """Importa os parâmetros de configuração da estação."""
    parametros = {}
    with open(f"{diretorio}/parametros.csv", newline='', encoding="utf-8") as ficheiro:
        for linha in csv.reader(ficheiro):
            chave, valor = linha[0].strip(), linha[1].strip()
            parametros[chave] = int(valor) if valor.isdigit() else valor
    return parametros

def ler_parque(diretorio):
    """Carrega o estado inicial do parque de comboios."""
    parque_inicial = Parque()
    with open(f"{diretorio}/parque.csv", newline='', encoding="utf-8") as ficheiro:
        for linha in csv.reader(ficheiro):
            parque_inicial.estacionar(linha)
    return parque_inicial

def ler_passageiros(diretorio):
    """Carrega a fila de passageiros VIP."""
    fila_bilheteira = Bilheteira()
    with open(f"{diretorio}/passageiros.csv", newline='', encoding="utf-8") as ficheiro:
        for linha in csv.reader(ficheiro):
            fila_bilheteira.juntar_fila(linha)
    return fila_bilheteira

def ler_perguntas(diretorio):
    """Carrega as perguntas sobre relações entre passageiros."""
    perguntas = []
    with open(f"{diretorio}/questoes_seguidores.csv", newline='', encoding="utf-8") as ficheiro:
        for linha in csv.reader(ficheiro):
            perguntas.append(Pergunta(linha[0].strip(), linha[1].strip()))
    return perguntas

def ler_calendario(diretorio):
    """Carrega o calendário de operações ferroviárias."""
    operacoes = []
    with open(f"{diretorio}/viagens.csv", "r", encoding="utf-8") as ficheiro:
        for linha in csv.reader(ficheiro):
            horario, tipo, nif = linha[0].strip(), linha[1].strip(), linha[2].strip()
            comboio = linha[3].strip() if len(linha) == 4 else None
            operacoes.append(Operacao(horario, tipo, nif, comboio))
    return operacoes

# FUNÇÕES DE GRAVAÇÃO DE RESULTADOS

def gravar_parque(diretorio, parque_final):
    """Grava o estado final do parque."""
    with open(f"{diretorio}/parque.csv", "w", newline="", encoding="utf-8") as ficheiro:
        escritor = csv.writer(ficheiro)
        for comboio in parque_final.pilha:
            escritor.writerow(comboio)

def gravar_passageiros(diretorio, lista):
    """Grava os dados dos passageiros processados."""
    with open(f"{diretorio}/passageiros.csv", "w", newline="", encoding="utf-8") as ficheiro:
        escritor = csv.writer(ficheiro)
        for p in lista:
            escritor.writerow([p.hora_entrada, p.identidade, p.hora_saida])

def gravar_placar(diretorio, cronologia):
    """Grava a cronologia do placar da estação."""
    with open(f"{diretorio}/placar.csv", "w", newline="", encoding="utf-8") as ficheiro:
        escritor = csv.writer(ficheiro)
        for horario, nomes in cronologia:
            escritor.writerow([horario] + nomes)

def gravar_respostas(diretorio, lista_respostas):
    """Grava as respostas às perguntas sobre seguidores."""
    with open(f"{diretorio}/questoes_seguidores.csv", "w", newline="", encoding="utf-8") as ficheiro:
        escritor = csv.writer(ficheiro)
        for seguidor, seguido, resultado in lista_respostas:
            escritor.writerow([seguidor, seguido, str(resultado)])

def gravar_viagens(diretorio, lista_viagens):
    """Grava o registo de todas as viagens efectuadas."""
    with open(f"{diretorio}/viagens.csv", "w", newline="", encoding="utf-8") as ficheiro:
        escritor = csv.writer(ficheiro)
        for v in lista_viagens:
            escritor.writerow([v.momento, v.categoria, v.nif_condutor, v.id_comboio])

# FUNÇÃO PRINCIPAL

def main():
    """Função principal que executa todo o processamento da estação."""
    
    # Configuração inicial
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Lê identificador do problema
    try:
        with open("nome_do_problema.txt", "r", encoding="utf-8") as ficheiro:
            identificador_problema = ficheiro.read().strip()
    except FileNotFoundError:
        print("Erro: ficheiro nome_do_problema.txt não existe.")
        return
    except IOError:
        print("Erro ao abrir o ficheiro.")
        return
    
    # Prepara diretórios
    dir_entrada = f"Input/{identificador_problema}"
    dir_saida = f"Output/{identificador_problema}"
    os.makedirs(dir_entrada, exist_ok=True)
    os.makedirs(dir_saida, exist_ok=True)
    
    # Inicializa ficheiro de erros
    caminho_erros = os.path.join(dir_saida, "erro.txt")
    with open(caminho_erros, "w", encoding="utf-8"):
        pass
    
    # Carrega dados
    config = ler_parametros(dir_entrada)
    parque = ler_parque(dir_entrada)
    bilheteira = ler_passageiros(dir_entrada)
    perguntas_seguidores = ler_perguntas(dir_entrada)
    calendario = ler_calendario(dir_entrada)
    
    # Processa operações
    viagens_efectuadas = executar_operacoes(calendario, config, caminho_erros, parque)
    passageiros_atendidos, historico_placar, grafo_social = gerir_passageiros(bilheteira, calendario, config)
    
    # Responde perguntas sobre seguidores
    respostas = []
    for pergunta in perguntas_seguidores:
        seguidos = grafo_social.get(pergunta.viajante, [])
        respostas.append((pergunta.viajante, pergunta.pessoa_seguida, pergunta.pessoa_seguida in seguidos))
    
    # Grava resultados
    gravar_parque(dir_saida, parque)
    gravar_passageiros(dir_saida, passageiros_atendidos)
    gravar_placar(dir_saida, historico_placar)
    gravar_respostas(dir_saida, respostas)
    gravar_viagens(dir_saida, viagens_efectuadas)
    
    # Apresenta resultados no terminal
    print(f"\n{'='*60}")
    print(f"ESTACAO 'MIRA MONTE' - {identificador_problema.upper()}")
    print(f"{'='*60}")
    
    print(f"\nRESUMO:")
    print(f"  Viagens: {len(viagens_efectuadas)} | Passageiros: {len(passageiros_atendidos)} | Parque: {parque.contar_comboios()}")
    
    print(f"\nVIAGENS:")
    for v in viagens_efectuadas:
        print(f"  {v.momento} | {v.categoria:8} | {v.id_comboio}")
    
    print(f"\nPASSAGEIROS:")
    for p in passageiros_atendidos:
        status = f"-> {p.hora_saida}" if p.hora_saida else "X Sem lugar"
        print(f"  {p.hora_entrada} {p.identidade:12} {status}")
    
    print(f"\nPARQUE FINAL: {[c[0] for c in parque.pilha]}")
    
    print(f"\nSEGUIDORES:")
    for seguidor, seguido, resultado in respostas:
        simbolo = "SIM" if resultado else "NAO"
        print(f"  [{simbolo}] {seguidor} -> {seguido}")
    
    print(f"\n{'='*60}")
    print(f"Processamento concluido | Outputs: {dir_saida}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
