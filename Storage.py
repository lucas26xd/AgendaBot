import json
FILE_NAME = 'users.json'


def loadFile():
    from os.path import isfile
    if isfile(FILE_NAME):
        arq = open(FILE_NAME, 'r')
        file = json.load(arq)
        arq.close()
    else:
        return dict()
    return file


def updateFile(users):
    arq = open(FILE_NAME, 'w')  # Re-cria o arquivo
    json.dump(users, arq, indent=4)
    arq.close()


def updateAlert(chatid, users, alert):
    if chatid not in users:
        users[chatid] = list()
    users[chatid].append(alert)
    updateFile(users)


def createAlert(message, day, hour):
    from datetime import datetime
    today = datetime.today()

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
    dt = datetime(y, m, d, h, mn)
    return {
        'message': message,
        'day': dt.strftime('%d/%m/%Y'),
        'hour': dt.strftime('%H:%M'),
        # 'createdAt': {'day': today.strftime('%d/%m/%Y'), 'hour': today.strftime('%H:%M:%S')},
        'enabled': True
    }


def getNumEnabledAlerts(user):
    n = 0
    for alert in user:
        if alert['enabled']:
            n += 1
    return n
    # return sum([1 for alert in user if alert['enabled']])

def getAlertList(chatid, users):
    if chatid not in users:
        return '*Não há nenhum lembrete ativo em sua agenda.*'
    user = users[chatid]
    lst = f'*Existe(m) {getNumEnabledAlerts(user)} lembrete(s) ativo(s) em sua agenda.*\n\n'
    for alert in user:
        if alert['enabled']:
            lst += f':white_check_mark: :memo:*{alert["message"]:10}* {"-":^5} :date:{alert["day"]} _às_ :watch:{alert["hour"]}\n'
    return lst
