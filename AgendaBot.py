from Storage import *
from Utils import *
from Config import API_KEY_TelegramBot
from time import sleep
from telepot import Bot, glance
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from emoji import emojize
# from pprint import pprint

requests = dict()


def onChatMessage(msg):
    # pprint(msg)
    contentType, chatType, chatid = glance(msg)
    try:
        chatid = str(chatid)
        if contentType == 'text':
            command = msg['text']
            if '/start' in command or '/help' in command:
                sendMessage(chatid, ':information_source: *Informações:* :information_source:\n\n'
                                    ':small_blue_diamond: /start ou /help - Para listar  os comandos aceitos.\n'
                                    ':small_blue_diamond: /list - Para listar  os seus lembretes ativos.\n'
                                    ':small_blue_diamond: /alert - Para criar um novo lembrete.\n'
                                    ':small_blue_diamond: /timer - Seguido de (23m, 2h, 1d) para criar um temporizador.\n')
            elif '/list' in command:
                sendMessage(chatid, getAlertList(chatid, users))
            elif '/alert' in command:
                sendMessage(chatid, 'Você pode enviar-me (/cancel) para cancelar sua requisição.')
                sendMessage(chatid, ':memo: Digite a *mensagem* do lembrete:', action=False)
                requests[chatid] = list()
            elif chatid in requests:
                if '/cancel' in command:
                    sendMessage(chatid, f'Tudo bem {msg["from"]["first_name"]}, requisição cancelada! :thumbsup:')
                    del requests[chatid]
                else:
                    requests[chatid].append(command)
                    if len(requests[chatid]) == 1:
                        sendMessage(chatid, ':date: Digite a *data* do lembrete:')
                    elif len(requests[chatid]) == 2:
                        sendMessage(chatid, ':watch: Digite a *hora* do lembrete:')
                    elif len(requests[chatid]) == 3:
                        alert = createAlert(requests[chatid][0], requests[chatid][1], requests[chatid][2])
                        updateAlert(chatid, users, alert)
                        sendMessage(chatid, f'Ok {msg["from"]["first_name"]}, compromisso agendado com sucesso! :thumbsup:')
                        sendMessage(chatid, getAlertList(chatid, users), action=False)
                        del requests[chatid]
            elif '/timer' in command:
                command = text = command[6:]
                if len(text) > 1:
                    mn = hr = dt = 0
                    if 'm' in command:
                        command, mn = getParamsTimer(command, 'm')
                    if 'h' in command:
                        command, hr = getParamsTimer(command, 'h')
                    if 'd' in command:
                        command, dt = getParamsTimer(command, 'd')
                    day, hour = snooze(mn, hr, dt)
                    alert = createAlert(f'Temporizador de {text}', day, hour)
                    updateAlert(chatid, users, alert)
                    sendMessage(chatid, f':thumbsup: Temporizador ativado para :date:{day} às :watch:{hour}!')
                else:
                    sendMessage(chatid, ':x: Erro, por favor envie-me o comando /timer seguido do tempo até o alarme'
                                        ' a partir de agora, por exemplo /timer 1h 2m para criar um alerta para'
                                        ' daqui a 1 hora de 2 minutos.')
            else:
                sendMessage(chatid, ':disappointed_relieved: Desculpe, não entendi o que você me falou.')
        else:
            sendMessage(chatid, ':pensive: Desculpe, ainda não fui preparado para receber este tipo de mensagem.')
    except Exception as error:
        sendMessage(chatid, ':disappointed_relieved: Desculpe, ocorreu um erro ainda não tratado.')
        print(f'Ocorreu um erro ainda não tratado: {error}')


def onCallbackQuery(msg):
    queryID, fromID, queryData = glance(msg, flavor='callback_query')
    user = users[str(fromID)]
    user[int(queryData)]['enabled'] = True
    user[int(queryData)]['day'], user[int(queryData)]['hour'] = snooze(mn=10)
    bot.answerCallbackQuery(queryID, text='Lembrete reativado para daqui a 10 minutos')
    updateFile(users)


def sendMessage(chatid, text, markup=None, action=True):
    if action:
        bot.sendChatAction(chatid, 'typing')
        sleep(1)
    bot.sendMessage(chatid, emojize(text, use_aliases=True), parse_mode='Markdown', reply_markup=markup)


def watchAlert():
    day, hour = getDayHour()
    for user in users.items():
        for i, alert in enumerate(user[1]):
            if alert['enabled'] and alert['day'] == day and alert['hour'] == hour:
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Soneca 😴', callback_data=i)]])
                sendMessage(user[0], f':bangbang::bell::alarm_clock: *{alert["message"].upper()}* :alarm_clock::bell::bangbang:', markup)
                alert['enabled'] = False
                updateFile(users)


users = loadFile()
bot = Bot(API_KEY_TelegramBot)

MessageLoop(bot, {'chat': onChatMessage, 'callback_query': onCallbackQuery}).run_as_thread()
print('Escutando ...')

while True:
    try:
        watchAlert()
        # sleep(10)
    except KeyboardInterrupt:
        print('Desligando...')
        break
