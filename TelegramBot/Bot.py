from telegram import Update
from telegram.ext import Updater, MessageHandler, CallbackQueryHandler, CallbackContext, Filters
from threading import Thread
from TelegramBot.Keyboard import Keyboard
from TelegramBot.UserList import Users
from TelegramBot.Rights import Rights, ButtonsSets
from TelegramBot.Regexp import RegExp

from Telnet.ControllerPool import BaseStationsControllersPool as BSC
from Telnet.ControllerPool import MobileSwitchingCentersPool as MSC


from Telnet.Alex import EricssonBscCommands as Alex
class Bot:
    def __init__(self, token="**TELEGRAM_TOKEN**"):
        self.updater = Updater(token)
        self.users = Users()
        self.keyboard = Keyboard()
        self.buttonSets = ButtonsSets()
        self.pool = BSC()
        self.mssPool = MSC()
        #self.mss_
        self.__initBsc()
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.messageHandler))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.buttonHandler))

        self.__startPolling()#Thread()

    def __initEricssonObject(self, poolObject, host, login, password, name):
        poolObject.addController(host, login, password, name)

    def __initBsc(self):
        threads = []

        threads.append(Thread(target=self.__initEricssonObject,
                              args=(self.pool, '**IP**', '**LOGIN**', '**PWD**', 'BSC04'), daemon=True))
        threads.append(Thread(target=self.__initEricssonObject,
                              args=(self.pool, '**IP**', '**LOGIN**', '**PWD**', 'BSC05'), daemon=True))
        threads.append(Thread(target=self.__initEricssonObject,
                              args=(self.mssPool, '**IP**', '**LOGIN**', '**PWD**', 'MSS02'), daemon=True))
        threads.append(Thread(target=self.__initEricssonObject,
                              args=(self.mssPool, '**IP**', '**LOGIN**', '**PWD**', 'MSC01'), daemon=True))

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def __startPollingThread(self):
        Thread(target=self.__startPolling, daemon=True).start()

    def __startPolling(self):
        while True:
            self.updater.start_polling()
            self.updater.idle()

    def buttonHandler(self, update: Update, context: CallbackContext) -> None:
        result = update.callback_query.data
        k = Keyboard()
        b = ButtonsSets()
        if b.getSet(result):
            print('+')
        k.createInlineKeyboard(b.getSet(result))
        update.message.reply_text('555', reply_markup=k.createReplyKeyboard())

    def addNewUser(self, user):
        username = user.first_name
        if user.last_name:
            username += ' ' + user.last_name
        self.users.newUser(user.id, username)

    def messageHandler(self, update: Update, context: CallbackContext) -> None:
        if 1:
            self.__messageHandler(update)
        #except:
        #    self.pool.reconnect()
        #    self.mssPool.reconnect()

    def __messageHandler(self, update: Update) -> None:
        user = update.message.from_user
        if not self.users.checkUser(user.id):
            self.addNewUser(user)
        text = update.message.text
        print(text)
        result = ''
        if '/start' in text:
            set = self.buttonSets.getSet('Меню')
            update.message.reply_text('Выберите действие:', reply_markup=self.keyboard.createReplyKeyboard(set))
            return
        elif text == 'Назад':
            set = None
            while not set:
                try:
                    setName = self.users.userCallBackstate(user.id)
                    menu = self.users.getUserState(user.id)
                    set = self.buttonSets.getSet(setName)
                except:
                    pass
            update.message.reply_text(menu + ' <--', reply_markup=self.keyboard.createReplyKeyboard(set))
            return


        self.users.writeAction(user.id, text) # - типа лог


        set = self.buttonSets.getSet(text)
        if set:
            if self.users.userStateChanged(user.id, text):
                update.message.reply_text(text, reply_markup=self.keyboard.createReplyKeyboard(set))
            else:
                update.message.reply_text('Недоступно')
                return

        state = self.users.getUserState(user.id)

        if state == 'Адрес' or 'где' in text.lower():
            if not self.users.userStateChanged(user.id, 'Адрес', onlyCheck=True):
                update.message.reply_text('Недоступно')
                return
            text = text.lower().replace('где ', '')
            while len(text) < 3:
                text = '0' + text
            adress = ''
            try:
                with open('adresses.txt', 'r', encoding='UTF-8') as adrFile:
                    data = adrFile.read()
                    for line in data.split('\n'):
                        parts = line.split(';')
                        if len(parts) > 1:
                            for obj in parts[0].split('/'):
                                if obj and obj.lower() in text:
                                    try:
                                        if int(obj) == int(text):
                                            update.message.reply_text(line.replace(';', ' '))
                                            return
                                    except:
                                        pass
                                    adress += line.replace(';', ' ') + '\n'
            except:
                pass
            if not adress:
                adress = 'Нет данных'
            update.message.reply_text(adress)
            return

        rbsName = RegExp.findRbs(text)
        cellName = RegExp.findCell(text)
        msisdn = RegExp.findMsisdn(text)

        prestate = 0
        if text in ['Железо', 'Отключить бс', 'Включить бс', 'Состояние потока', 'Адрес']:
            prestate = 1
        elif text in ['Захалтить сектор', 'Расхалтить сектор', 'Забарить сектор',
                      'Разбарить сектор', 'Информация о секторе', 'Удалить DCH канал',
                      'Добавить DCH канал', 'Список хендоверов', 'Узнать CRO']:
            prestate = 2
        elif text in ['Регистрация', 'Cancel Location (CS)', 'Cancel Location (PS)']:
            prestate = 3
        elif text in ['Добавить хендовер', 'Удалить хендовер']:
            prestate = 4
        elif text == 'Изменить CRO':
            prestate = 5
        if prestate > 0:
            reply = 'название БС'
            if prestate == 2:
                reply = 'имя сектора'
            elif prestate == 3:
                reply = 'MSISDN'
            elif prestate == 4:
                reply = 'сектор А и сектор Б через пробел'
            elif prestate == 5:
                reply = 'сектор и новое CRO через пробел'
            if self.users.userStateChanged(user.id, text):
                update.message.reply_text(f'Введите {reply}:')
            else:
                update.message.reply_text('Недоступно')

        #'Cancel Location (CS)', 'Cancel Location (PS)']:

        if cellName:
            header = 'Результат выполнения:'
            answer = ''
            if state == 'Захалтить сектор':
                update.message.reply_text(f'Халтим сектор {cellName}')
                answer = self.pool.setCellHaltedState(cellName, True)
            elif state in ['Добавить хендовер', 'Удалить хендовер']:
                cells = text.split(' ')
                if len(cells) > 1:
                    cellr = RegExp.findCell(cells[1])
                if cellName == cellr:
                    update.message.reply_text(f'Так нельзя :) {cellName} <-> {cellr}')
                    return
                update.message.reply_text(f'{state} {cellName} <-> {cellr}')
                cellAInfo = self.pool.getCellInfo(cellName)
                cellBInfo = self.pool.getCellInfo(cellr)
                if 'BCCH' in cellAInfo and 'BCCH' in cellBInfo:
                    bcch1 = cellAInfo.split('BCCH: ')[1].split('\n')[0].strip()
                    bcch2 = cellBInfo.split('BCCH: ')[1].split('\n')[0].strip()
                    bsc1 = self.pool.getOwners(cellName)
                    if len(bsc1):
                        bsc1 = bsc1[0]
                    bsc2 = self.pool.getOwners(cellr)
                    if len(bsc2):
                        bsc2 = bsc2[0]

                    if bsc1.name != bsc2.name:
                        update.message.reply_text('Межконтроллерный хендовер')
                        cellAext = bsc2.inExternalList(cellName)
                        cellBext = bsc1.inExternalList(cellr)
                        update.message.reply_text(f"На {bsc1.name} {cellr} как "
                                                  f"EXT {'' if cellBext else 'не'} прописана")
                        update.message.reply_text(f"На {bsc2.name} {cellName} как "
                                                  f"EXT {'' if cellAext else 'не'} прописана")
                        if not cellAext or not cellBext:
                            update.message.reply_text('Обратитесь на смену')
                            return
                    if bcch1 and bcch2:
                        result = []
                        if 'Добавить' in state:
                            result.append(self.pool.addHendover(cellName, cellr, bcch2))
                            result.append(self.pool.addHendover(cellr, cellName, bcch1))
                        else:
                            result.append(self.pool.remHendover(cellName, cellr, bcch2))
                            result.append(self.pool.remHendover(cellr, cellName, bcch1))
                        update.message.reply_text('\n'.join(result))
                        return
                else:
                    update.message.reply_text(f'Не удалось получить информацию '
                                              f'о секторе {cellName if "BCCH" not in cellAInfo else cellr}')
                return
            elif state == 'Расхалтить сектор':
                update.message.reply_text(f'Расхалчиваем сектор {cellName}')
                answer = self.pool.setCellHaltedState(cellName, False)
            elif state == 'Узнать CRO':
                answer = self.pool.getCro(cellName)
                update.message.reply_text(answer)
                return
            elif state == 'Изменить CRO':
                cro = text.split(' ')[-1]
                try:
                    int(cro)
                    answer = self.pool.setCro(cellName, cro=cro)
                except:
                    answer = 'Не удалось изменить CRO'
                update.message.reply_text(answer)
                return
            elif state == 'Забарить сектор':
                update.message.reply_text(f'Халтим сектор {cellName}')
                answer = self.pool.setCellBarredState(cellName, True)
            elif state == 'Разбарить сектор':
                update.message.reply_text(f'Расхалчиваем сектор {cellName}')
                answer = self.pool.setCellBarredState(cellName, False)
            elif state == 'Информация о секторе':
                update.message.reply_text(self.pool.getCellInfo(cellName))
                return
            elif state == 'Список хендоверов':
                update.message.reply_text(self.pool.getHandovers(cellName))
                return
            elif state == 'Добавить DCH канал' or state == 'Удалить DCH канал':
                messageParts = text.split(' ')
                dchSet = []
                if len(messageParts) > 1:
                    dchSet = messageParts[1].replace(' ', '').split(',')
                answer = 'Необходимо ввести DCH частоты'
                if len(dchSet):
                    add = False
                    if 'Добавить' in state:
                        update.message.reply_text(f'Добавление каналов (новые EGSM не поддерживаются) '
                                                  f'( {", ".join(dchSet)} ) на {cellName}')
                        add = True
                    else:
                        update.message.reply_text(f'Удаление каналов ( {", ".join(dchSet)} ) на {cellName}')
                    set1 = []
                    set2 = []
                    for dch in dchSet:
                        try:
                            __dch = int(dch)
                            if __dch > 974:
                                set2.append(dch)
                            else:
                                set1.append(dch)
                        except:
                            pass


                    if set2:
                        if set1:
                            update.message.reply_text(f"Каналы: {','.join(set1)}\n" +
                                                      self.pool.changeChannelsList(cellName, set1, add=add))

                        update.message.reply_text(f"Каналы: {','.join(set2)} (CHGR1)\n" +
                                                  self.pool.changeChannelsList(cellName, set2, add=add, chgr=1))
                        return
                    else:
                        answer = self.pool.changeChannelsList(cellName, dchSet, add=add)
                update.message.reply_text(answer)
                return

            else:
                if self.users.userStateChanged(user.id, 'Состояние сектора', onlyCheck=True):
                    header = f'Состояние сектора {cellName}\n'
                    answer = self.pool.getCellState(cellName)
                else:
                    answer = 'Недоступно'

            update.message.reply_text(header)
            update.message.reply_text(answer)
        elif rbsName:
            header = 'Результат выполнения:'
            answer = ''
            if state == 'Железо':
                answer = self.pool.getHardwareState(rbsName)
                update.message.reply_text(answer)
                return
            elif state == 'Отключить бс':
                update.message.reply_text(f'Отключаем бс {rbsName}')
                answer = self.pool.setObjectStateBlocked(rbsName, True)
            elif state == 'Добавить адрес':
                try:
                    rbs = text.split(' ')[0]
                    __adress = text.replace(rbs, '').strip()
                    with open('adresses.txt', 'a+') as adrfile:
                        adrfile.write(f'\n{rbs};{__adress}')
                    answer = 'Добавлено'
                except:
                    answer = 'Ошибка'
            elif state == 'Состояние потока':
                update.message.reply_text(f'Состояние потоков на {rbsName}')
                answer = self.pool.getThreadsState(rbsName)
                bsc = answer.split('\n')[0]
                rbls = RegExp.findDip(answer)
                for i in range(len(rbls)):
                    rbls[i] = f"//{bsc}_{rbls[i]}"
                if len(rbls):
                    set = [rbls, ['Меню', 'Назад']]
                    __keyboard = self.keyboard.createReplyKeyboard(set)
                    update.message.reply_text(answer, reply_markup=__keyboard)
                    return
                update.message.reply_text(answer)
                return
            elif state == 'Включить бс':
                update.message.reply_text(f'Включаем бс {rbsName}')
                answer = self.pool.setObjectStateBlocked(rbsName, False)
            elif state in ['Захалтить сектор', 'Расхалтить сектор', 'Забарить сектор',
                      'Разбарить сектор', 'Информация о секторе', 'Список хендоверов']:
                answer = 'Выберите сектор'
                buttonSet = [self.pool.getCellsFromObject(rbsName)]
                buttonSet.append(['Меню', 'Назад'])
                __keyboard = self.keyboard.createReplyKeyboard(buttonSet)
                update.message.reply_text(answer, reply_markup=__keyboard)
                return
            elif self.users.userStateChanged(user.id, 'Состояние сектора', onlyCheck=True):
                cells = self.pool.getCellsFromObject(rbsName)
                if object and cells:
                    header = f'Состояние секторов на {rbsName}\n'
                    update.message.reply_text(header)
                    for cell in cells:
                        result = self.pool.getCellState(cell)
                        update.message.reply_text(result)
                    return
                else:
                    answer = 'Объект не найден'
            else:
                update.message.reply_text('Недоступно')
            update.message.reply_text(header)
            update.message.reply_text(answer)
            return
        elif msisdn:
            if state == 'Регистрация':
                result = self.mssPool.getVlrRegistrationInfo(msisdn)
                if 'CELL ID' in result:
                    cell = result.split('CELL ID:')[1].split('\n')[0][:-1].strip()
                    print(cell)
                    update.message.reply_text(result)
                    adress = ''
                    try:
                        with open('adresses.txt', 'r', encoding='UTF-8') as adrFile:
                            data = adrFile.read()
                            for line in data.split('\n'):
                                parts = line.split(';')
                                if len(parts) > 1:
                                    for obj in parts[0].split('/'):
                                        try:
                                            if int(obj) == int(cell):
                                                update.message.reply_text(line.replace(';', ' '))
                                                return
                                        except:
                                            pass
                                        if obj and obj.lower() == cell:
                                            adress += line.replace(';', ' ') + '\n'
                    except:
                        pass
                    if adress:
                        update.message.reply_text(adress)
                    return
        if text in ['Права пользователя', 'Расширить права', 'Ограничить права']:
            if not self.users.userStateChanged(user.id, text):
                result = 'Недоступно'
        if text in ['ABL', 'RDI', 'AIS', 'ERATE', 'LOS/LOF']:
            if self.users.userStateChanged(user.id, 'Состояние потока', onlyCheck=True):
                update.message.reply_text(self.pool.getFailedDips(text))
                return
            else:
                result = 'Недоступно'
        if text == 'БС на SIU':
            if self.users.userStateChanged(user.id, 'БС на SIU', onlyCheck=True):
                result = self.pool.getSiuRbs()
        if text == 'Захалченные сектора':
            if self.users.userStateChanged(user.id, 'Сектора', onlyCheck=True):
                result = self.pool.getHaltedCells()
        if text == 'Забаренные сектора':
            if self.users.userStateChanged(user.id, 'Сектора', onlyCheck=True):
                result = self.pool.getBarredCells()
        if text == 'Отключенные бс':
            result = self.pool.getDisabledTransferingGroups()
        if text in ['Пользователи', 'Права пользователя']:
            __header = f'{text}:\n'
            result = __header + '\n'.join(self.users.getUsers())
        if text.startswith('/id'):
            #try:
            uid = int(text.split()[0].replace('/id', ''))
            result = f'Права пользователя {uid}:\n' + '\n'.join(self.users.getUserRights(uid))

            if state == 'Расширить права':
                for right in self.users.allAbilities():
                    if not self.users.checkAbility(uid, right):
                        self.users.giveAbility(uid, right)
                        name = self.users.getUserName(uid)
                        update.message.reply_text(f'Пользователю {name} добавлен набор {right}')
                        return
            elif state == 'Ограничить права':
                __rights = self.users.allAbilities()
                __rights.reverse()
                for right in __rights:
                    print(right, self.users.checkAbility(uid, right))
                    if self.users.checkAbility(uid, right):
                        self.users.takeAbility(uid, right)
                        name = self.users.getUserName(uid)
                        update.message.reply_text(f'Пользователю {name} удален набор {right}')
                        return
            #self.keyboard.createReplyKeyboard()
        if text.startswith('//'):
            if self.users.userStateChanged(user.id, 'Состояние потока', onlyCheck=True):
                text = text.replace('//', '')
                result = ''
                try:
                    rbs, rbl = text.split('_')
                    result = self.pool.getRblState(rbs, rbl)
                except:
                    result = 'Ошибка'
                update.message.reply_text(result)
            else:
                update.message.reply_text('Недоступно')
            return
        if result:
            update.message.reply_text(result)
