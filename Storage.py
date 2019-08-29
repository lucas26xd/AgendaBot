import json
FILE_NAME = 'users.json'


def loadFile():  # Carrega arquivo
    from os.path import isfile
    if isfile(FILE_NAME):
        arq = open(FILE_NAME, 'r')
        file = json.load(arq)
        arq.close()
        return file
    else:
        return dict()


def updateFile(users):  # Reescreve o arquivo
    arq = open(FILE_NAME, 'w')  # Re-cria o arquivo
    json.dump(users, arq, indent=4)
    arq.close()


def updateAlert(chatid, users, alert):
    if chatid not in users:
        users[chatid] = list()
    users[chatid].append(alert)
    updateFile(users)


def createAlert(message, day, hour):  # Cria objeto no padrão para armazenamento
    from datetime import datetime
    today = datetime.today()
    d, m, y, h, mn = formatDateHour(today, day, hour)
    dt = datetime(y, m, d, h, mn)
    return {
        'message': message,
        'day': dt.strftime('%d/%m/%Y'),
        'hour': dt.strftime('%H:%M'),
        # 'createdAt': {'day': today.strftime('%d/%m/%Y'), 'hour': today.strftime('%H:%M:%S')},
        'enabled': True
    }


def formatDateHour(today, day, hour):
    d = day.split('/')
    if len(d) == 1:
        d.append(today.month)
    if len(d) == 2:
        d.append(today.year)

    h = hour[:5].split(':')
    if len(h) == 1:
        h.append(0)

    d, m, y = [int(i) for i in d]
    h, mn = [int(i) for i in h]
    return d, m, y, h, mn


def getNumEnabledAlerts(user):  # Pega número de alerta ativados do usuário especificado
    n = 0
    for alert in user:
        if alert['enabled']:
            n += 1
    return n  # return sum([1 for alert in user if alert['enabled']])


def getAlertList(chatid, users):  # Retorna lista dos alertas ativados
    if chatid not in users:
        return '*Não há nenhum lembrete ativo em sua agenda.*'
    user = users[chatid]
    lst = f'*Existe(m) {getNumEnabledAlerts(user)} lembrete(s) ativo(s) em sua agenda.*\n\n'
    for alert in user:
        if alert['enabled']:
            lst += f':white_check_mark: :memo:*{alert["message"]:10}* {"-":^5} :date:{alert["day"]} _às_ :watch:{alert["hour"]}\n'
    return lst
