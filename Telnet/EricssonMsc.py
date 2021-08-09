from Telnet.EricssonTelnet import EricssonTelnet as Telnet
from Telnet.EricssonBsc import EricssonObject
from Telnet.Alex import EricssonMscCommands as Alex
from Telnet.EricssonParser import EricssonParser
import time


class EricssonMsc(EricssonObject):
    def __init__(self, host, login, password, name='MSC'):
        self.name = name
        self.password = password
        self.host = host
        self.login = login
        self.__parser = EricssonParser()
        self.connect()

    def connect(self):
        self.__connection = Telnet(self.host, self.login, self.password)

    def __waitFor(self, answer, objectName, timeout=10):
        stopWord = 'FAULT CODE'
        busyWord = 'FUNCTION BUSY'
        preAnswer = ';\r\n'
        for timepoint in range(timeout * 2):
            log = self.__connection.getAlarms()
            for __print in log:
                if objectName in __print or __print.startswith(preAnswer):
                    if busyWord in __print:
                        return "Функция занята, попробуйте позже"
                    elif stopWord in __print:
                        return "Ошибка при выполнении"
                    elif answer in __print:
                        return __print
            time.sleep(0.5)
        return "Привышен интервал ожидания ответа"

    def getRegistration(self, msisdn):
        self.__connection.send(Alex.mgtrp(msisdn), accepting=False)
        mgtrp = self.__waitFor(answer='TO IMSI', objectName=msisdn, timeout=40) #'MT MSISDN TO IMSI'
        parsedMgtrp = self.__parser.parse(mgtrp)
        if len(parsedMgtrp):
            for part in parsedMgtrp:
                imsi = part['IMSI']
                if imsi:
                    break
            if imsi:
                mgssp = self.__connection.get(Alex.mgssp(imsi)).replace('IMSI', '\nIMSI')
                parsedMgssp = self.__parser.parse(mgssp)[0]
                print(parsedMgssp)
                state = 'Неизвестно'
                cid = 'Неизвестно'
                sai = 'Неизвестно'
                datetime = 'Неизвестно'
                keys = parsedMgssp.keys()
                if 'STATE' in keys:
                    state = parsedMgssp['STATE']
                if 'LAST RADIO ACCESS' in keys:
                    dt = parsedMgssp['LAST RADIO ACCESS']
                    __date = '000000'
                    __time = '0000'
                    for dtPart in dt.split(',')[1].split(' '):
                        if len(dtPart) == 6:
                            __date = dtPart
                        if len(dtPart) == 4:
                            __time = dtPart
                    datetime = f'{__date[-2:]}.{__date[-4:-2]}.20{__date[:-4]} {__time[:2]}:{__time[2:]}'
                if 'SAI' in keys:
                    cid = parsedMgssp['SAI']
                if 'CELL ID' in keys:
                    cid = parsedMgssp['CELL ID']
                if 'LAI' in keys:
                    sai = parsedMgssp['LAI']
                result = f'MSS: {self.name}\nMSISDN: {msisdn}\nIMSI: {imsi}\nSTATE: {state}\n' \
                         f'CELL ID: {cid}\nSAI: {sai}\nLAST RADIO ACCESS:\n{datetime}'
                return result
        return 'Не найдено'

    def putRegistration(self, msisdn, container):
        registration = self.getRegistration(msisdn)
        if registration:
            container.append(registration)
