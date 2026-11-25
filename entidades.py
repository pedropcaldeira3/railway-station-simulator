"""
Módulo de Entidades do Sistema Ferroviário "Mira Monte"

Este módulo contém as estruturas de dados fundamentais para a gestão da estação:
- Pilha LIFO para controlo do parque de estacionamento de comboios
- Fila FIFO para gestão da bilheteira VIP e atendimento de passageiros
- Classes que representam as entidades do domínio ferroviário
"""

class Viagem:
    """
    Representa uma operação ferroviária registada no sistema.
    
    Cada viagem corresponde a um movimento de comboio (chegada ou partida)
    e inclui toda a informação temporal necessária para detectar conflitos.
    """
    def __init__(self, momento, categoria, nif_condutor, id_comboio, instante_inicial, instante_final):
        self.momento = momento  # Horário oficial da operação
        self.categoria = categoria  # "Chegada" ou "Partida"
        self.nif_condutor = nif_condutor  # NIF do maquinista responsável
        self.id_comboio = id_comboio  # Identificador da composição
        self.instante_inicial = instante_inicial  # Início da ocupação da plataforma
        self.instante_final = instante_final  # Fim da ocupação da plataforma

    def __str__(self):
        return f"{self.momento},{self.categoria},{self.nif_condutor},{self.id_comboio}"


class Parque:
    """
    Estrutura LIFO (Last In, First Out) para gestão do parque de comboios.
    
    Simula um parque ferroviário com entrada e saída únicas, onde o último
    comboio a entrar é necessariamente o primeiro a sair.
    """
    def __init__(self):
        self.pilha = []  # Armazena os comboios estacionados

    def estacionar(self, comboio):
        """Coloca um comboio no topo do parque (entrada)."""
        self.pilha.append(comboio)

    def retirar(self):
        """Remove e retorna o comboio do topo (saída). Retorna None se vazio."""
        if self.esta_vazio():
            return None
        return self.pilha.pop()

    def consultar_proximo(self):
        """Consulta qual o próximo comboio a sair sem o remover."""
        if self.esta_vazio():
            return None
        return self.pilha[-1]

    def esta_vazio(self):
        """Verifica se o parque tem comboios estacionados."""
        return not self.pilha
    
    def contar_comboios(self):
        """Retorna o número de comboios atualmente no parque."""
        return len(self.pilha)


class Operacao:
    """
    Armazena os dados de uma operação ferroviária programada.
    
    Utilizada para representar viagens agendadas antes do seu processamento,
    contendo apenas a informação básica do horário e identificação.
    """
    def __init__(self, horario, tipo_operacao, nif_condutor, id_comboio=None):
        self.horario = horario  # Hora programada
        self.tipo_operacao = tipo_operacao  # Tipo de movimento
        self.nif_condutor = nif_condutor  # Identificação do maquinista
        self.id_comboio = id_comboio  # ID do comboio (obrigatório só para chegadas)

    def __str__(self):
        if self.id_comboio:
            return f"{self.horario},{self.tipo_operacao},{self.nif_condutor},{self.id_comboio}"
        return f"{self.horario},{self.tipo_operacao},{self.nif_condutor}"


class Pergunta:
    """
    Modela uma pergunta sobre relações sociais entre passageiros.
    
    Permite verificar se um passageiro segue outro nas redes sociais,
    conforme especificado no ficheiro de questões.
    """
    def __init__(self, viajante, pessoa_seguida):
        self.viajante = viajante  # Nome do passageiro que queremos verificar
        self.pessoa_seguida = pessoa_seguida  # Nome da pessoa que pode ser seguida

    def __str__(self):
        return f"{self.viajante},{self.pessoa_seguida}"


class Passageiro:
    """
    Registo completo do percurso de um passageiro VIP pela estação.
    
    Documenta todos os momentos relevantes desde a chegada à bilheteira
    até ao embarque (ou não) num comboio.
    """
    def __init__(self, hora_entrada, identidade, conexoes, hora_saida="", 
                 momento_fim_bilheteira="", momento_plataforma="", momento_embarque=""):
        self.hora_entrada = hora_entrada  # Chegada à bilheteira
        self.identidade = identidade  # Nome do passageiro
        self.conexoes = conexoes  # Lista de pessoas que segue
        self.hora_saida = hora_saida  # Horário do comboio (se conseguiu lugar)
        self.momento_fim_bilheteira = momento_fim_bilheteira  # Fim do atendimento
        self.momento_plataforma = momento_plataforma  # Chegada à plataforma
        self.momento_embarque = momento_embarque  # Entrada no comboio


class Bilheteira:
    """
    Estrutura FIFO (First In, First Out) para atendimento na bilheteira VIP.
    
    Os passageiros são atendidos por ordem de chegada, respeitando
    rigorosamente a sequência de entrada na fila.
    """
    def __init__(self):
        self.fila_espera = []  # Armazena os passageiros em espera

    def juntar_fila(self, cliente):
        """Adiciona um passageiro ao final da fila de espera."""
        self.fila_espera.append(cliente)

    def atender_proximo(self):
        """Remove e retorna o próximo passageiro a ser atendido. Retorna None se vazio."""
        if self.esta_vazia():
            return None
        return self.fila_espera.pop(0)
    
    def ver_proximo(self):
        """Consulta quem é o próximo a ser atendido sem o remover."""
        if self.esta_vazia():
            return None
        return self.fila_espera[0]
    
    def ver_ultimo(self):
        """Consulta quem é o último da fila."""
        if self.esta_vazia():
            return None
        return self.fila_espera[-1]

    def esta_vazia(self):
        """Verifica se há passageiros na fila de espera."""
        return not self.fila_espera

    def contar_pessoas(self):
        """Retorna o número de passageiros aguardando atendimento."""
        return len(self.fila_espera)
