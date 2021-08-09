class Set:
    def __init__(self, name):
        self.name = name
        self.abilities = []

    def __eq__(self, other):
        return self.name == other

    def setup(self, abilities):
        self.abilities = abilities

    def getSet(self):
        return self.abilities


class ButtonsSets:
    def __init__(self):
        self.sets = []
        navigationButtons = ['Меню', 'Назад']
        inputRbs = [['Введите название бс'], navigationButtons]
        inputCell = [['Введите название сектора'], navigationButtons]
        inputMsisdn = [['Введите MSISDN'], navigationButtons]
        self.addSet('Меню', [['Базовые станции', 'Абоненты'], ['CDR', 'Администрирование']])
        self.addSet('Базовые станции', [['Сектора', 'Адреса'], ['Потоки', 'Кабинеты'], navigationButtons])
        self.addSet('Сектора', [['Информация о секторе', 'Хендоверы'],
                                ['Управление сектором', 'Частоты', 'CRO'], navigationButtons])
        self.addSet('Кабинеты', [['Железо', 'Отключенные бс'], ['Включить бс', 'Отключить бс'], navigationButtons])
        #self.addSet('Состояние сектора', inputCell)
        self.addSet('Адреса', [['Адрес', 'Добавить адрес'], navigationButtons])
        self.addSet('CRO', [['Узнать CRO', 'Изменить CRO'], navigationButtons])
        self.addSet('Потоки', [['Состояние потока', 'Аварии по потокам', 'БС на SIU'], navigationButtons])
        self.addSet('Аварии по потокам', [['ABL', 'RDI', 'AIS'], ['ERATE', 'LOS/LOF', 'Назад']])
        self.addSet('Хендоверы', [['Список хендоверов', 'Добавить хендовер', 'Удалить хендовер'], navigationButtons])
        #self.addSet('Железо', inputRbs)
        #self.addSet('Отключить бс', inputRbs)
        #self.addSet('Включить бс', inputRbs)
        #self.addSet('Захалтить сектор', inputCell)
        #self.addSet('Расхалтить сектор', inputCell)
        #self.addSet('Забарить сектор', inputCell)
        #self.addSet('Разбарить сектор', inputCell)
        #self.addSet('Информация о секторе', inputCell)
        #self.addSet('Регистрация', inputMsisdn)
        #self.addSet('Cancel Location (CS)', inputMsisdn)
        #self.addSet('Cancel Location (PS)', inputMsisdn)
        #self.addSet('Добавить DCH канал', [['Введите название сектора и каналы через запятую'], navigationButtons])
        #self.addSet('Удалить DCH канал', [['Введите название сектора и каналы через запятую'], navigationButtons])

        self.addSet('Абоненты', [['Регистрация', 'Cancel Location (CS)',
                                  'Cancel Location (PS)'], navigationButtons])
        self.addSet('Частоты', [['Информация о секторе', 'Изменить BCCH'],
                                ['Добавить DCH канал', 'Удалить DCH канал'], navigationButtons])

        self.addSet('Управление сектором',
                    [['Захалченные сектора', 'Забаренные сектора'],
                    ['Захалтить сектор', 'Забарить сектор'],
                    ['Расхалтить сектор', 'Разбарить сектор'], navigationButtons]
                    )
        self.addSet('Администрирование', [['Пользователи', 'Права пользователя'],
                                          ['Расширить права', 'Ограничить права'], navigationButtons])

    def addSet(self, name, abilities):
        set = Set(name)
        set.setup(abilities)
        self.sets.append(set)

    def getSet(self, name):
        for set in self.sets:
            if set == name:
                return set.getSet()
        return None


class RightSet:
    def __init__(self, name):
        self.name = name
        self.rights = []

    def __eq__(self, other):
        return self.name == other

    def add(self, right):
        self.rights.append(right)


class Rights:
    def __init__(self):
        self.__rights = []
        with open('rightsList.txt', 'r+', encoding='UTF-8') as rigthsFile:
            data = rigthsFile.read()
            setName = ''
            for part in data.split('#END'):
                for rightString in part.split('\n'):
                    line = rightString.strip().replace(':', '')
                    if ':' in rightString:
                        setName = line
                    else:
                        if len(line):
                            self.addRightsToSet(setName, line)

    def addRightsToSet(self, name, right):
        self.__findRight(name).add(right)

    def findRight(self, name):
        for right in self.__rights:
            if right == name:
                return right
        return None

    def __findRight(self, name):
        __right = self.findRight(name)
        if not __right:
            __right = RightSet(name)
            self.__rights.append(__right)
        return __right

    def getRights(self, name) ->list:
        return self.__findRight(name).rights

    def getRightSetsNames(self):
        return [_right.name for _right in self.__rights]

    def getSetName(self, right):
        for __right in self.__rights:
            if right in __right.rights:
                return __right.name
        return None
