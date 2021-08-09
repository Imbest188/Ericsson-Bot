from Telnet.EricssonBsc import EricssonBsc
from Telnet.EricssonMsc import EricssonMsc
from threading import Thread
from concurrent.futures import ThreadPoolExecutor


class MobileSwitchingCentersPool:
    __pool = []

    def getChannelsOutput(self):
        result = []
        for obj in self.__pool:
            result.append({'OBJECT': obj.name, 'ALARMS': obj.getChannelOutput()})
        return result

    def reconnect(self):
        for msc in self.__pool:
            msc.connect()

    def addController(self, host, login, password, name='MSC'):
        msc = EricssonMsc(host, login, password, name)
        self.__pool.append(msc)

    def __multipleExecution(self, function, arg):
        threads = []
        result = []
        for msc in self.__pool:
            print('send to', msc.name)
            thread = Thread(target=getattr(msc, function), args=(arg, result,), daemon=True)
            threads.append(thread)
            thread.start()
        for thr in threads:
            thr.join()
        return result

    def __sendCommand(self, command, arg):
        result = []
        for msc in self.__pool:
            result.append(msc.name)
            result.append(getattr(msc, command)(arg))
        return result

    def getVlrRegistrationInfo(self, msisdn):
        #answer = self.__multipleExecution('putRegistration', msisdn)
        answer = self.__sendCommand('getRegistration', msisdn)
        result = msisdn + ' не зарегистрирован'
        for part in answer:
            if len(part.replace('Неизвестно', '')) > len(result):
                result = part
        return result


class BaseStationsControllersPool(MobileSwitchingCentersPool):
    __pool = []

    def addController(self, host, login, password, name='BSC'):
        bsc = EricssonBsc(host, login, password, name)
        self.__pool.append(bsc)

    def __containsObjectAnywhere(self, object):
        find = []
        for bsc in self.__pool:
            if bsc.containsObject(object):
                find.append(bsc)
        if not len(find):
            return False
        return find

    def __objectExistsOn(self, object) -> EricssonBsc:
        find = self.__containsObjectAnywhere(object)
        if not find:
            for bsc in self.__pool:
                bsc.updateObjectsList()
            return self.__containsObjectAnywhere(object)
        return find

    def __multipleExecution(self, function):
        threads = []
        result = []
        for bsc in self.__pool:
            thread = Thread(target=getattr(bsc, function), args=(result,), daemon=True)
            threads.append(thread)
            thread.start()
        for thr in threads:
            thr.join()
        return '\n'.join(result)

    def __sendCommand(self, command, objectName, arg):
        owners = self.__objectExistsOn(objectName)
        if not owners:
            return f'Объект {objectName} не найден'
        result = []
        for bsc in owners:
            result.append(bsc.name)
            result.append(getattr(bsc, command)(objectName, arg))
        return '\n'.join(result)

    def getCellState(self, cellName):
        owners = self.__objectExistsOn(cellName)
        if not owners:
            return f'Сектор {cellName} не найден'
        answer = ''
        for bsc in owners:
            answer += bsc.name + '\n';
            answer += bsc.getCellState(cellName) + '\n'
        return answer

    def setCellHaltedState(self, cellName, state):
        return self.__sendCommand("setCellHaltedState", cellName, state)

    def setObjectStateBlocked(self, objectName, state):
        return self.__sendCommand("setRbsStateBlocked", objectName, state)

    def setCellBarredState(self, cellName, state):
        return self.__sendCommand("setCellStateBarred", cellName, state)

    def getHaltedCells(self):
        return self.__multipleExecution("putHaltedCells")

    def getDisabledTransferingGroups(self):
        return self.__multipleExecution("putDisabledTransferingGroups")

    def getBarredCells(self):
        return self.__multipleExecution("putBarredCells")

    def getCellsFromObject(self, object):
        owners = self.__objectExistsOn(object)
        if owners:
            return getattr(owners[0], 'getObject')(object).cells
        return []

    def getCellInfo(self, cellName):
        owners = self.__objectExistsOn(cellName)
        if not owners:
            return f'Сектор {cellName} не найден'
        answer = ''
        for bsc in owners:
            answer += bsc.name + '\n';
            answer += bsc.getCellInfo(cellName) + '\n'
        return answer

    def getHandovers(self, cellName):
        owners = self.__objectExistsOn(cellName)
        if not owners:
            return f'Сектор {cellName} не найден'
        answer = ''
        for bsc in owners:
            answer += bsc.name + '\n';
            answer += bsc.getHandovers(cellName) + '\n'
        return answer

    def getCro(self, cellName):
        owners = self.__objectExistsOn(cellName)
        if not owners:
            return f'Сектор {cellName} не найден'
        answer = ''
        for bsc in owners:
            answer += bsc.name + '\n';
            answer += bsc.getCellCRO(cellName) + '\n'
        return answer

    def getOwners(self, cellName):
        owners = self.__objectExistsOn(cellName)
        return owners

    def setCro(self, cellName, cro):
        owners = self.__objectExistsOn(cellName)
        if not owners:
            return f'Сектор {cellName} не найден'
        answer = ''
        for bsc in owners:
            answer += bsc.name + '\n'
            answer += bsc.setCellCRO(cellName,cro) + '\n'
        return answer

    def addHendover(self, cellName, cellr, bcchno):
        owners = self.__objectExistsOn(cellName)
        if not owners:
            return f'Сектор {cellName} не найден'
        answer = ''
        for bsc in owners:
            answer += bsc.name + '\n'
            answer += bsc.addHendover(cellName, cellr, bcchno)
        return answer

    def remHendover(self, cellName, cellr, bcchno):
        owners = self.__objectExistsOn(cellName)
        if not owners:
            return f'Сектор {cellName} не найден'
        answer = ''
        for bsc in owners:
            answer += bsc.name + '\n'
            answer += bsc.remHendover(cellName, cellr, bcchno)
        return answer

    def changeChannelsList(self, cellName, dchList, add=True, chgr=0):
        owners = self.__objectExistsOn(cellName)
        if not owners:
            return f'Сектор {cellName} не найден'
        answer = ''
        for bsc in owners:
            answer += bsc.name + '\n';
            result = bsc.changeChannelsList(cellName, dchList, add, chgr)
            print(result)
            answer += result + '\n'
        return answer

    def getHardwareState(self, rbs):
        owners = self.__objectExistsOn(rbs)
        if not owners:
            return f'Объект {rbs} не найден'
        answer = ''
        for bsc in owners:
            answer += f'{bsc.name}\n{rbs}\n'
            answer += bsc.getHardwareState(rbs) + '\n'
        return answer

    def getThreadsState(self, rbs):
        owners = self.__objectExistsOn(rbs)
        if not owners:
            return f'Объект {rbs} не найден'
        answer = ''
        for bsc in owners:
            answer += f'{bsc.name}\n{rbs}\n'
            answer += bsc.getThreadsState(rbs) + '\n'
        return answer

    def getRblState(self, __bsc, rbl):
        for bsc in self.__pool:
            if bsc.name == __bsc:
                return bsc.getThreadState(rbl)
        return f'Нет такого контроллера {__bsc}'

    def getSiuRbs(self):
        result = ''
        for bsc in self.__pool:
            result += '\n'.join(bsc.getSiuRbs()) + '\n\n'
        return result

    def getFailedDips(self, fail):
        result = ''
        for bsc in self.__pool:
            answer = bsc.getFailedDips(fail.split('/'))
            if not answer:
                answer = 'Нет'
            result += f"{bsc.name}\n{answer}\n\n"
        return result

    def reconnect(self):
        for bsc in self.__pool:
            bsc.connect()
