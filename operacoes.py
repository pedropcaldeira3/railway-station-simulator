"""
Módulo de Operações da Estação Ferroviária "Mira Monte"

Contém toda a lógica de negócio para:
- Conversão e cálculo de horários em diferentes formatos
- Processamento de chegadas e partidas de comboios
- Gestão da bilheteira VIP e alocação de lugares
- Detecção de colisões temporais entre movimentos
- Registo de anomalias e situações de erro
"""
import os
from entidades import Viagem, Passageiro


def horario_em_minutos(texto_hora):
    """
    Converte uma hora em formato textual para minutos desde a meia-noite.
    
    Argumentos:
        texto_hora: String no formato "HH:MM"
    
    Retorna:
        Inteiro representando minutos totais desde as 00:00
    """
    partes = texto_hora.split(":")
    horas_int = int(partes[0])
    minutos_int = int(partes[1])
    return horas_int * 60 + minutos_int


def minutos_em_horario(minutos_totais):
    """
    Converte minutos desde a meia-noite para formato de hora textual.
    
    Argumentos:
        minutos_totais: Número de minutos desde as 00:00
    
    Retorna:
        String formatada como "HH:MM"
    """
    horas = minutos_totais // 60
    minutos = minutos_totais % 60
    return f"{horas:02d}:{minutos:02d}"


def existe_colisao(viagem1, viagem2):
    """
    Verifica se duas viagens têm sobreposição temporal na plataforma.
    
    Duas viagens colidem se os seus intervalos de ocupação da plataforma
    se sobrepõem, mesmo que parcialmente.
    
    Argumentos:
        viagem1: Primeira viagem a verificar
        viagem2: Segunda viagem a verificar
    
    Retorna:
        True se houver sobreposição, False caso contrário
    """
    inicio_1 = horario_em_minutos(viagem1.instante_inicial)
    fim_1 = horario_em_minutos(viagem1.instante_final)
    inicio_2 = horario_em_minutos(viagem2.instante_inicial)
    fim_2 = horario_em_minutos(viagem2.instante_final)
    
    # Há colisão se os intervalos se intersectam
    return inicio_1 < fim_2 and inicio_2 < fim_1


def escrever_erro(caminho_ficheiro, texto_erro):
    """
    Adiciona uma mensagem de erro ao ficheiro de log da estação.
    
    Garante que cada erro fica numa linha separada e que o ficheiro
    é criado se não existir.
    
    Argumentos:
        caminho_ficheiro: Localização do ficheiro erro.txt
        texto_erro: Mensagem descritiva do problema
    """
    if not caminho_ficheiro or not texto_erro.strip():
        return

    ficheiro_existe = os.path.exists(caminho_ficheiro)
    modo = "a" if ficheiro_existe else "w"
    
    with open(caminho_ficheiro, modo, encoding="utf-8") as ficheiro:
        if ficheiro_existe and os.path.getsize(caminho_ficheiro) > 0:
            ficheiro.write("\n")
        ficheiro.write(texto_erro.strip())


def processar_chegada(operacao, config):
    """
    Calcula os tempos de ocupação da plataforma para uma chegada.
    
    Uma chegada ocupa a plataforma desde que o comboio inicia a entrada
    até que termina de se deslocar para o parque após o desembarque.
    
    Argumentos:
        operacao: Dados da chegada programada
        config: Dicionário com parâmetros de duração
    
    Retorna:
        Objecto Viagem com todos os tempos calculados
    """
    momento_referencia = horario_em_minutos(operacao.horario)
    
    # Tempo que demora a entrar na plataforma (antes do horário oficial)
    duracao_entrada = int(config["duracao_entrada_plataforma"])
    
    # Tempo de desembarque + transferência para o parque (depois do horário)
    duracao_desembarque = int(config["duracao_desembarque"])
    duracao_transferencia = int(config["duracao_plataforma_parque"])
    
    inicio_ocupacao = momento_referencia - duracao_entrada
    fim_ocupacao = momento_referencia + duracao_desembarque + duracao_transferencia
    
    return Viagem(
        operacao.horario,
        "Chegada",
        operacao.nif_condutor,
        operacao.id_comboio,
        minutos_em_horario(inicio_ocupacao),
        minutos_em_horario(fim_ocupacao)
    )


def processar_partida(operacao, config, ficheiro_erros, parque):
    """
    Calcula os tempos de ocupação da plataforma para uma partida.
    
    Uma partida requer retirar um comboio do parque. Ocupa a plataforma
    desde que o comboio sai do parque até que termina de sair da estação.
    
    Argumentos:
        operacao: Dados da partida programada
        config: Dicionário com parâmetros de duração
        ficheiro_erros: Caminho para registo de erros
        parque: Estrutura com comboios disponíveis
    
    Retorna:
        Tupla (Viagem, comboio_retirado) ou (None, None) se não houver comboios
    """
    comboio = parque.retirar()

    if not comboio:
        escrever_erro(ficheiro_erros, 
            f"Não existem comboios disponíveis para efectuar a partida das {operacao.horario}")
        return None, None

    momento_referencia = horario_em_minutos(operacao.horario)
    
    # Tempo de embarque + transferência do parque (antes do horário oficial)
    duracao_embarque = int(config["duracao_embarque"])
    duracao_transferencia = int(config["duracao_plataforma_parque"])
    
    # Tempo de saída da plataforma (depois do horário oficial)
    duracao_saida = int(config["duracao_entrada_plataforma"])
    
    inicio_ocupacao = momento_referencia - duracao_embarque - duracao_transferencia
    fim_ocupacao = momento_referencia + duracao_saida
    
    return (
        Viagem(
            operacao.horario,
            "Partida",
            operacao.nif_condutor,
            comboio[0],
            minutos_em_horario(inicio_ocupacao),
            minutos_em_horario(fim_ocupacao)
        ),
        comboio
    )


def gerir_passageiros(bilheteira, calendario, config):
    """
    Processa todos os passageiros VIP que chegam à bilheteira.
    
    Simula o atendimento sequencial, respeitando:
    - Horário de abertura da bilheteira
    - Tempo de atendimento de cada passageiro
    - Tempo de deslocação até à plataforma
    - Capacidade limitada de lugares VIP por comboio
    - Tempo necessário para embarque
    
    Argumentos:
        bilheteira: Fila com os passageiros a atender
        calendario: Lista de operações (para saber as partidas)
        config: Parâmetros do sistema
    
    Retorna:
        Tupla (lista_passageiros, cronologia_placar, mapa_seguidores)
    """
    # Extrai parâmetros de configuração
    tempo_atendimento = int(config["duracao_atendimento"])
    tempo_deslocacao = int(config["duracao_bilheteira_plataforma"])
    tempo_embarque = int(config["duracao_embarque"])
    lugares_vip = int(config["numero_de_lugares_vip"])

    # Identifica todas as partidas e inicializa lugares disponíveis
    partidas = sorted(
        [op.horario for op in calendario if op.tipo_operacao == "Partida"],
        key=horario_em_minutos
    )
    lugares_livres = {hora: lugares_vip for hora in partidas}
    
    # Horário em que a bilheteira abre
    momento_disponivel = horario_em_minutos(config.get("horario_abertura", "00:00"))

    passageiros_tratados = []
    relacoes_sociais = {}
    
    # Processa cada passageiro pela ordem de chegada
    for dados in bilheteira.fila_espera:
        hora_chegada = dados[0].strip()
        nome = dados[1].strip() if len(dados) > 1 else ""
        seguidos = [item.strip() for item in dados[2:] if item.strip()]
        relacoes_sociais[nome] = seguidos

        # Calcula quando é atendido (pode ter de esperar pela abertura)
        momento_chegada = horario_em_minutos(hora_chegada)
        inicio_atendimento = max(momento_chegada, momento_disponivel)
        fim_atendimento = inicio_atendimento + tempo_atendimento
        momento_disponivel = fim_atendimento  # Próximo só pode ser atendido depois
        
        # Calcula quando chega à plataforma
        chegada_plataforma = fim_atendimento + tempo_deslocacao

        # Tenta alocar a uma partida
        partida_alocada = ""
        momento_entra_comboio = None

        for hora_partida in partidas:
            if lugares_livres[hora_partida] <= 0:
                continue  # Esta partida já está cheia
            
            momento_partida = horario_em_minutos(hora_partida)
            
            # Quando pode começar a embarcar (o mais tarde entre chegar e início do embarque)
            pode_embarcar_em = max(chegada_plataforma, momento_partida - tempo_embarque)
            
            # Só embarca se chegar a tempo
            if pode_embarcar_em <= momento_partida:
                partida_alocada = hora_partida
                momento_entra_comboio = pode_embarcar_em
                lugares_livres[hora_partida] -= 1
                break

        # Cria registo do passageiro
        passageiro = Passageiro(
            hora_chegada,
            nome,
            seguidos,
            partida_alocada,
            minutos_em_horario(fim_atendimento),
            minutos_em_horario(chegada_plataforma),
            minutos_em_horario(momento_entra_comboio) if momento_entra_comboio is not None else ""
        )
        passageiros_tratados.append(passageiro)

    def construir_placar():
        """
        Gera a cronologia de passageiros presentes na estação.
        
        O placar mostra quem está na estação em cada momento relevante:
        - Aumenta quando alguém termina de comprar bilhete
        - Diminui quando alguém embarca num comboio
        
        Retorna:
            Lista de tuplas (horário, lista_nomes_presentes)
        """
        eventos = []
        presentes = set()
        
        # Adiciona eventos de chegada (fim de compra = chegada à estação)
        for p in passageiros_tratados:
            presentes.add(p.identidade)
            eventos.append((p.momento_fim_bilheteira, sorted(presentes)))

        # Prepara eventos de saída (embarque)
        presentes = set(p.identidade for p in passageiros_tratados)
        embarques_por_hora = {}
        
        for p in passageiros_tratados:
            if not p.hora_saida:
                continue  # Não embarcou
            momento = p.momento_embarque
            if momento:
                embarques_por_hora.setdefault(momento, []).append(p.identidade)

        # Adiciona eventos de saída
        for momento in sorted(embarques_por_hora.keys(), key=horario_em_minutos):
            for nome in embarques_por_hora[momento]:
                presentes.discard(nome)
            eventos.append((momento, sorted(presentes)))

        return eventos
    
    placar = construir_placar()

    return passageiros_tratados, placar, relacoes_sociais


def executar_operacoes(calendario, config, ficheiro_erros, parque):
    """
    Executa todas as operações ferroviárias programadas.
    
    Processa sequencialmente cada chegada e partida, verificando:
    - Disponibilidade de espaço no parque para chegadas
    - Disponibilidade de comboios no parque para partidas
    - Colisões temporais entre operações consecutivas
    
    Argumentos:
        calendario: Lista de operações a executar
        config: Parâmetros do sistema
        ficheiro_erros: Caminho para registo de erros
        parque: Estrutura de estacionamento
    
    Retorna:
        Lista de viagens efectivamente realizadas
    """
    viagens_realizadas = []
    capacidade_parque = int(config.get("capacidade_do_parque", 999999))

    for operacao in calendario:
        viagem_actual = None

        if operacao.tipo_operacao == "Chegada":
            viagem_actual = processar_chegada(operacao, config)

            # Verifica se há espaço no parque
            if parque.contar_comboios() >= capacidade_parque:
                escrever_erro(ficheiro_erros,
                    f"Parque cheio: não é possível estacionar o comboio {operacao.id_comboio} na chegada das {operacao.horario}")
                continue

        elif operacao.tipo_operacao == "Partida":
            viagem_actual, _ = processar_partida(operacao, config, ficheiro_erros, parque)
            if viagem_actual is None:
                continue  # Erro já foi registado

        else:
            escrever_erro(ficheiro_erros,
                f"Tipo de viagem desconhecido '{operacao.tipo_operacao}'")
            continue

        # Verifica colisão com a viagem anterior
        if viagens_realizadas and viagem_actual and existe_colisao(viagens_realizadas[-1], viagem_actual):
            anterior = viagens_realizadas[-1]
            escrever_erro(ficheiro_erros,
                f"Colisão entre o comboio {anterior.id_comboio} da {anterior.categoria} e o comboio {viagem_actual.id_comboio} da {viagem_actual.categoria}")

        # Estaciona o comboio se for chegada
        if operacao.tipo_operacao == "Chegada":
            parque.estacionar([operacao.id_comboio])

        viagens_realizadas.append(viagem_actual)

    return viagens_realizadas
