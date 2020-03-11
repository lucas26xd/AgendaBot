from Storage import *
from Utils import *
from Config import API_KEY_TelegramBot
from time import sleep
from telepot import Bot, glance
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from emoji import emojize
# from pprint import pprint

# LINKS
# https://telepot.readthedocs.io/en/latest/
# https://core.telegram.org/bots/api
# https://www.webfx.com/tools/emoji-cheat-sheet/

# SUGESTÕES DE MELHORIA
# - Ordenamento na lista de lembretes por data em que irá acontecer
# - Não permitir datas/horas passadas
# - Habilitar/Desabilitar lembretes
# - Função de periodicidade nos lembretes (ex: Seg a Sab)
# - Menu de configs (ex: Tempo de Soneca = 15 min)


def onChatMessage(msg):  # Função para tratamento do recebimento de mensagens
    # pprint(msg)
    contentType, chatType, chatid = glance(msg)  # Pega informações da mensagem
    try:
        chatid = str(chatid)
        if contentType == 'text':  # Mensagens de texto
            command = msg['text']
            if '/start' in command or '/help' in command:  # Resposta de ajuda
                sendMessage(chatid, ':information_source: *Informações:* :information_source:\n'
                                    ':white_check_mark: ChatBot criado com o intuito de introduzir os estudantes do ETEC na API do Telegram utilizando Python.\n\n'
                                    ':arrow_down: Abaixo segue a lista de ações que o bot pode realizar: :arrow_down:\n'
                                    ':small_blue_diamond: /start ou /help - Para listar  os comandos aceitos.\n'
                                    ':small_blue_diamond: /list - Para listar  os seus lembretes ativos.\n'
                                    ':small_blue_diamond: /alert - Para criar um novo lembrete.\n'
                                    ':small_blue_diamond: /timer - Seguido de (23m, 2h, 1d) para criar um temporizador.\n')
            elif '/list' in command:  # Listagem dos alertas habilitados
                sendMessage(chatid, getAlertList(chatid, users))
            elif '/alert' in command:  # Inicia bloco para recebimento das informações do alerta
                sendMessage(chatid, 'Você pode enviar-me (/cancel) para cancelar sua requisição.')
                sendMessage(chatid, ':memo: Digite a *mensagem* do lembrete:', action=False)
                requests[chatid] = list()
            elif chatid in requests:  # Significa que o usuário está dentro de uma requisição de criação de um alerta
                if '/cancel' in command:  # Cancelamento de requisição
                    sendMessage(chatid, f'Tudo bem {msg["from"]["first_name"]}, requisição cancelada! :thumbsup:')
                    del requests[chatid]  # Exclui a requisição do usuário
                else:
                    requests[chatid].append(command)
                    if len(requests[chatid]) == 1:
                        sendMessage(chatid, ':date: Digite a *data* do lembrete:')
                    elif len(requests[chatid]) == 2:
                        sendMessage(chatid, ':watch: Digite a *hora* do lembrete:')
                    elif len(requests[chatid]) == 3:  # Salva o alerta depois de requisitar todas as 3 informações
                        alert = createAlert(requests[chatid][0], requests[chatid][1], requests[chatid][2])
                        updateAlert(chatid, users, alert)
                        sendMessage(chatid, f'Ok {msg["from"]["first_name"]}, compromisso agendado com sucesso! :thumbsup:')
                        sendMessage(chatid, getAlertList(chatid, users), action=False)
                        del requests[chatid]
            elif '/timer' in command:  # Marca temporizador de acordo com o parâmetro passado
                command = text = command[6:]
                if len(text) > 1:
                    mn = hr = dt = 0
                    if 'm' in command:
                        command, mn = getParamsTimer(command, 'm')
                    if 'h' in command:
                        command, hr = getParamsTimer(command, 'h')
                    if 'd' in command:
                        command, dt = getParamsTimer(command, 'd')
                    day, hour = snooze(mn, hr, dt)  # Acrescenta os parâmetros passados na data e hora atual
                    alert = createAlert(f'Temporizador de {text}', day, hour)  # Cria o alerta
                    updateAlert(chatid, users, alert)
                    sendMessage(chatid, f':thumbsup: Temporizador ativado para :date:{day} às :watch:{hour}!')
                else:  # Caso seja envia apenas o comando /timer sem nenhum parâmetro
                    sendMessage(chatid, ':x: Erro, por favor envie-me o comando /timer seguido do tempo até o alarme'
                                        ' a partir de agora, por exemplo /timer 1h 2m para criar um alerta para'
                                        ' daqui a 1 hora de 2 minutos.')
            else:  # Caso o enviado não esteja na lista de comandos realizados
                sendMessage(chatid, ':disappointed_relieved: Desculpe, não entendi o que você me falou.')
        else:  # Caso seja enviado mensagens de tipos diferentes de 'text'
            sendMessage(chatid, ':pensive: Desculpe, ainda não fui preparado para receber este tipo de mensagem.')
    except Exception as error:
        sendMessage(chatid, ':disappointed_relieved: Desculpe, ocorreu um erro ainda não tratado.')
        print(f'Ocorreu um erro ainda não tratado: {error}')


def onCallbackQuery(msg):  # Função de ação do botão de soneca
    queryID, fromID, queryData = glance(msg, flavor='callback_query')
    user = users[str(fromID)]
    user[int(queryData)]['enabled'] = True  # Reativa o lembrete
    user[int(queryData)]['day'], user[int(queryData)]['hour'] = snooze(mn=10)  # Acrescenta 10 minutos a hora atual
    bot.answerCallbackQuery(queryID, text='Lembrete reativado para daqui a 10 minutos')
    updateFile(users)


def sendMessage(chatid, text, markup=None, action=True):  # Função de envio de mensagem para o chat específico
    if action:
        bot.sendChatAction(chatid, 'typing')
        sleep(1)
    bot.sendMessage(chatid, emojize(text, use_aliases=True), parse_mode='Markdown', reply_markup=markup)


def watchAlert():  # Função de monitoramento de todos os alertas cadastrados
    day, hour = getDayHour()
    for user in users.items():
        for i, alert in enumerate(user[1]):
            if alert['enabled'] and alert['day'] == day and alert['hour'] == hour:  # Aciona alarme
                markup = InlineKeyboardMarkup(inline_keyboard=[  # Cria botão passando como dado o índice do alerta
                    [InlineKeyboardButton(text='Soneca 😴', callback_data=i)]])
                sendMessage(user[0], f':bangbang::bell::alarm_clock: *{alert["message"].upper()}* '
                                     ':alarm_clock::bell::bangbang:', markup)
                alert['enabled'] = False  # Depois de enviar o alerta, desabilita o lembrete
                updateFile(users)


requests = dict()  # Dicionário das requisições momentâneas de cada usuário
users = loadFile()  # Carrega arquivo
bot = Bot(API_KEY_TelegramBot)  # Seleciona API KEY do  Bot escolhido

MessageLoop(bot, {'chat': onChatMessage, 'callback_query': onCallbackQuery}).run_as_thread()  # Liga Thread de escuta
print(bot.getMe())
print('Escutando ...')

while True:
    try:
        watchAlert()  # Chama função de monitoramento a cada 1 segundo
        sleep(1)
    except KeyboardInterrupt:
        print('Desligando...')
        break
