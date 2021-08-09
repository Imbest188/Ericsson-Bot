from Telnet.EricssonTelnet import EricssonTelnet as Telnet
from Telnet.Alex import EricssonBscCommands as Alex
from Telnet.EricssonParser import EricssonParser
import time


class TranferingGroup:
    def __init__(self, tg, cells):
        self.tg = tg
        self.name = []
        for cell in cells:
            subname = cell[:-1]
            if subname not in self.name:
                self.name.append(subname)
        self.cells = cells

    def __eq__(self, other):
        if other == self.tg:
            return True
        for obj in self.cells + self.name:
            if obj == other:
                return True
        return False

    def __str__(self):
        return f'TG:{self.tg}, NAME:{",".join(self.name)}, CELLS:{",".join(self.cells)}'



class EricssonObject:
    __connection = None

    def __init__(self, host, login, password, name='OBJECT'):
        self.name = name
        self.__connection = Telnet(host, login, password)

    def getChannelOutput(self):
        return self.__connection.getAlarms()


class EricssonBsc(EricssonObject):
    def __init__(self, host, login, password, name='BSC'):
        self.name = name
        self.host = host
        self.login = login
        self.password = password
        self.__parser = EricssonParser()
        self.__objects = []
        self.connect()

    def connect(self):
        self.__connection = Telnet(self.host, self.login, self.password)
        self.updateObjectsList()

    def getCellState(self, cellName):
        answer = self.__connection.get(Alex.rlcrp(cellName))
        if 'CELL NOT DEFINED' in answer:
            return 'Такого сектора не существует'
        cell = ''
        sdcch = ''
        sdcchBusy = 0
        ts = ''
        tsBusy = 0
        speech = 0
        icm = 0
        icmCount = 0
        gprs = 0
        queved = ''
        for item in self.__parser.parse(answer):
            keys = item.keys()
            if 'CELL' in keys:
                cell = item['CELL']
            if 'SDCCH' in keys:
                sdcch = item['SDCCH']
            if 'NOOFTCH' in keys:
                __ts = item['NOOFTCH'].split(' ')
                ts = __ts[-1]
            if 'STATE' in keys:
                channelList = item['CHANNEL'].split(',')
                stateList = item['STATE'].split(',')
                chrateList = item['CHRATE'].split(',')
                for channel in range(len(channelList)):
                    if 'TCH' in channelList[channel]:
                        if 'HR' in chrateList[channel]:
                            if 'IDLE' not in stateList[channel]:
                                tsBusy += 1
                    elif 'SDCCH' in channelList[channel]:
                        if 'IDLE' not in stateList[channel]:
                            sdcchBusy += 1
            if 'USE' in keys:
                states = item['USE']
                for state in states.split(','):
                    if state == 'SPEECH':
                        speech += 1
                    if state == 'GPRS':
                        gprs += 1
            if 'ICMBAND' in keys:
                __icm = item['ICMBAND']
                for val in __icm.split(','):
                    try:
                        icm += int(val)
                        icmCount += 1
                    except:
                        pass
            if 'QUEUED' in keys:
                queved = item['QUEUED']
        if icmCount > 0:
            icm = icm / icmCount
        result = f'Сектор: {cell}\nТаймслоты: {tsBusy}' \
                 f' \\ {ts}\nSDCCH: {sdcchBusy} \\ {sdcch}\n' \
                 f'Интерференция: {round(icm, 2)}\nОчередь: {queved}\n' \
                 f'Разговоры: {speech}\nGPRS: {gprs}'
        return result

    def getCellCRO(self, cellName):
        answer = self.__connection.get(Alex.rlsbp(cellName))
        if 'CELL NOT DEFINED' in answer:
            return 'Такого сектора не существует'
        parsed = self.__parser.parse(answer)[0]
        cro = parsed['CRO']
        return f'Сектор: {cellName}\nCRO:{cro}'

    def setCellCRO(self, cellName, cro):
        self.__connection.send(Alex.rlsbc(cellName, cro=cro))
        answer = self.__waitFor('EXECUTED', cellName)
        if 'CELL NOT DEFINED' in answer:
            return 'Такого сектора не существует'
        return answer

    def getCellInfo(self, cellName):
        answer = self.__connection.get(Alex.rldep(cellName))
        if 'CELL NOT DEFINED' in answer:
            return 'Такого сектора не существует'
        parsed = self.__parser.parse(answer)[0]
        cell = parsed['CELL']
        bcch = parsed['BCCHNO']
        bsic = parsed['BSIC']
        cgi = parsed['CGI']
        answer2 = self.__connection.get(Alex.rlcfp(cellName))
        parsed2 = self.__parser.parse(answer2)[0]
        dchno = parsed2['DCHNO']

        return f'Сектор: {cell}\nCGI: {cgi}\nBCCH: {bcch}\nDCH: {dchno}\nBSIC: {bsic}'

    def getHardwareState(self, rbs):
        tg = self.getObject(rbs).tg
        answer = self.__connection.get(Alex.rxmsp(tg=tg))
        parsed = self.__parser.parse(answer)
        result = []
        for object in parsed:
            line = f'{object["MO"]} {object["STATE"]} {object["BLSTATE"]} {object["CONF"]}'
            result.append(line)
        return '\n'.join(result)

    def getThreadState(self, rbl):
        result = 'Ошибка при получении ответа от BSC'
        try:
            dtstp = self.__connection.get(Alex.dtstp(rbl))
            # old code :))))
            dipPrint = dtstp.split("SECTION")[1]
            dipPrint = dipPrint.split("END")[0]
            temp = dipPrint.split()
            line = 'DIP: ' + temp[0] + ' ,СОСТОЯНИЕ: ' + temp[2]
            try:
                line = line + ' ,FAULT: ' + temp[3]
            except:
                pass
            result = line
        except:
            pass
        return result

    def getThreadsState(self, rbs):
        tg = self.getObject(rbs).tg
        answer = self.__connection.get(Alex.rxapp(tg=tg))
        parsed = self.__parser.parse(answer)
        result = ''
        rbls = []
        for part in parsed:
            if 'DEV' in part.keys():
                rbl = str(int(int(part['DEV'].split('-')[1]) / 32))
                rbls.append(rbl) if rbl not in rbls else None
        for rbl in rbls:
            try:
                dtstp = self.__connection.get(Alex.dtstp(rbl))
                #old code :))))
                dipPrint = dtstp.split("SECTION")[1]
                dipPrint = dipPrint.split("END")[0]
                temp = dipPrint.split()
                line = 'DIP: ' + temp[0] + ' ,СОСТОЯНИЕ: ' + temp[2]
                try:
                    line = line + ' ,FAULT: ' + temp[3]
                except:
                    pass
                result += line
            except:
                pass
        if not rbls:
            if rbs in self.getSiuRbs():
                return f'{rbs} работает через SIU'
        return result

    def changeChannelsList(self, cellName, dchList, add=True, chgr=0):
        if chgr == 1:
            self.__connection.send(Alex.rlccc(cellName, 1, 0))
            self.__waitFor('EXECUTED', cellName)
        answer = self.__connection.send(Alex.rlcfi(cellName, dchList, chgr)) if add \
            else self.__connection.send(Alex.rlcfe(cellName, dchList, chgr))
        return self.__waitFor('EXECUTED', cellName)

    def inExternalList(self, cellName):
        print(cellName)
        answer = self.__connection.get(Alex.rldep(ext=True))
        parsed = self.__parser.parse(answer)
        #print(self.name, parsed)
        for part in parsed:
            if 'CELL' in part.keys():
                if part['CELL'] == cellName:
                    return True



       # print(parsed)
        return False

    def getHandovers(self, cellName):
        result = []
        result3g = []
        for item in self.__parser.parse(self.__connection.get(Alex.rlnrp(cellName))):
            if 'CELLR' in item.keys():
                result += item['CELLR'].split(',')
        for item in self.__parser.parse(self.__connection.get(Alex.rlnrp(cellName, utran=True))):
            if 'CELLR' in item.keys():
                result3g += item['CELLR'].split(',')
        text2g = '\n'.join(result)
        text3g = '\n'.join([f'{cell[:-1]}({cell[-1]})' for cell in result3g])
        return f"2G:\n{text2g}\n3G:\n{text3g}"


    def updateObjectsList(self):
        answer = self.__connection.get(Alex.rxtcp())
        self.__objects.clear()
        for item in self.__parser.parse(answer):
            tg = item['MO']
            cells = []
            for cell in item['CELL'].split(','):
                if cell not in cells:
                    cells.append(cell)
            group = TranferingGroup(tg, cells)
            self.__objects.append(group)

    def containsObject(self, object):
        return object in self.__objects

    def getObject(self, object) -> TranferingGroup:
        for obj in self.__objects:
            if obj == object:
                return obj
        return None

    def __waitFor(self, answer, objectName, timeout=20):
        stopWord = 'FAULT CODE'
        busyWord = 'FUNCTION BUSY'
        preAnswer = ';\r\n'
        for timepoint in range(timeout * 2):
            log = self.__connection.getAlarms()
            print(log)
            for __print in log:
                if objectName in __print or __print.startswith(preAnswer):
                    if busyWord in __print:
                        return "Функция занята, попробуйте позже"
                    elif 'INHIBITED' in __print or 'NOT ACCEPTED' in __print:
                        return 'Отклонено'
                    elif stopWord in __print:
                        if 'ALREADY DEFINED' in __print:
                            return 'Ошибка: добавление существующих данных'
                        return "Ошибка при выполнении"
                    elif answer in __print:
                        return "Выполнено"
            time.sleep(0.5)
        return "Привышен интервал ожидания ответа"

    def setRbsStateBlocked(self, rbs, state):
        object = self.getObject(rbs)
        self.__connection.getAlarms()
        if state:
            self.__connection.send(Alex.rxbli(object.tg))
        else:
            self.__connection.send(Alex.rxble(object.tg))
        return self.__waitFor('EXECUTED', object.tg)

    def addHendover(self, cell, cellr, bcchno):
        self.__connection.send(Alex.rlnri(cell, cellr))
        result = f"RLNRI: {self.__waitFor('EXECUTED', cell)}\n"
        self.__connection.send(Alex.rlnrc(cell, cellr))
        result += f"RLNRC: {self.__waitFor('EXECUTED', cell)}\n"
        self.__connection.send(Alex.rlmfi(cell, bcchno))
        result += f"RLMFI: {self.__waitFor('EXECUTED', cell)}"
        return result

    def remHendover(self, cell, cellr, bcchno):
        self.__connection.send(Alex.rlnre(cell, cellr))
        result = f"RLNRE: {self.__waitFor('EXECUTED', cell)}\n"
        self.__connection.send(Alex.rlmfe(cell, bcchno))
        result += f"RLMFE: {self.__waitFor('NEIGHBOUR RELATION DELETED', cell)}"
        return result

    def setCellHaltedState(self, cellName, state):
        __state = 'ACTIVE'
        if state:
            __state = 'HALTED'
        self.__connection.send(Alex.rlstc(cellName, state=__state))
        result = self.__waitFor('EXECUTED', cellName)
        if 'NOT ALL CHANNEL GROUPS' in result:
            result = self.__connection.send(Alex.rlstc(cellName, '0', state=__state))
            return self.__waitFor('EXECUTED', cellName)
        return result

    def getHaltedCells(self):
        result = []
        for item in self.__parser.parse(self.__connection.get(Alex.rlstp(state='HALTED'))):
            result.append(item['CELL'])
        return result

    def getSiuRbs(self):
        result = []
        answer = self.__connection.get(Alex.rrgsp())
        print(answer)
        for item in self.__parser.parse(answer):
            try:
                print(item)
                result.append(item['PSTU'])
            except:
                pass
        return result

    def putHaltedCells(self, container):
        answer = self.getHaltedCells()
        container.append('\n' + self.name)
        container += answer if answer else ['Нет захалченных секторов']

    def getDisabledTransferingGroups(self):
        result = []
        for item in self.__parser.parse(self.__connection.get(Alex.rxmsp(moty='RXOCF'))):
            if item['BLSTATE'] == 'MBL':
                mo = item['MO'].replace('RXOCF', 'RXOTG')
                object = self.getObject(mo)
                result += object.name
        return result

    def putDisabledTransferingGroups(self, container):
        answer = self.getDisabledTransferingGroups()
        container.append('\n' + self.name)
        container += answer if answer else ['Нет отключенных объектов']

    def setCellStateBarred(self, cell, cb=False):
        __state = 'no'
        if cb:
            __state = 'yes'
        self.__connection.send(Alex.rlsbc(cell, cb))
        return self.__waitFor('EXECUTED', cell)

    def getBarredCells(self):
        answer = self.__connection.get(Alex.rlsbp())
        result = []
        for item in self.__parser.parse(answer):
            if item['CB'] == 'YES':
                result.append(item['CELL'])
        return result

    def putBarredCells(self, container):
        answer = self.getBarredCells()
        container.append('\n' + self.name)
        container += answer if answer else ['Нет забаренных секторов']

    def getFailedDips(self, alarms):
        answer = self.__connection.get(Alex.dtstp())
        result = []
        for line in answer.split('\n'):
            for alarm in alarms:
                if alarm in line:
                    result.append(line)
        return '\n'.join(result)

