from datetime import datetime
daysOfMouth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def snooze(mn=0, hr=0, dt=0):  # Função de incremento de tempo a partir da hora e data atuais
    day, hour = getDayHour()
    h, m = [int(s) for s in hour.split(':')]
    d, month, y = [int(s) for s in day.split('/')]
    # Incrementa tempos
    m += mn
    h += hr
    d += dt
    # Realiza ajustes no formato de data e hora caso seja necessário
    if m >= 60:
        m %= 60
        h += 1
    if h > 23:
        h %= 24
        d += 1
    if d > daysOfMouth[month]:
        d %= daysOfMouth[month]
        month += 1
        if month > 12:
            month %= 12
            y += 1

    day = f'{d:0>2}/{month:0>2}/{y}'
    hour = f'{h:0>2}:{m:0>2}'

    return day, hour


def getDayHour():  # Pega data e hora atuais
    today = datetime.today()
    return today.strftime('%d/%m/%Y'), today.strftime('%H:%M')


def getParamsTimer(command, param):  # Separa parâmetros do comando /timer
    t = command[:command.find(param) + 1]
    t = t[t.rfind(' '):]
    command.replace(t, '')
    return command, abs(int(t[1:-1]))
