from TelegramBot.Rights import Rights


class User:
    def __init__(self, id, name):
        if type(id) == str:
            id = int(id)
        self.__id = id
        self.__name = name
        self.__rights = ['Стандартные']
        self.__state = 'Меню'
        self.__prevStates = []
        self.__cells = []
        self.__rbs = ''
        self.__lastId = None

    def setObject(self, rbs=None, cells=None):
        self.__rbs = rbs
        self.__cells = cells

    def getObject(self, cells=False):
        if cells:
            return self.__cells
        if not self.__rbs:
            return self.__cells
        return self.__rbs

    def moveTo(self, state):
        if state == 'Меню':
            self.__prevStates.clear()
        else:
            self.__prevStates.append(self.__state)
        self.__state = state

    def backState(self):
        if len(self.__prevStates):
            newState = self.__prevStates.pop()
            print(newState)
            self.__state = newState
            return newState
        return 'Меню'

    def giveAbility(self, ability):
        if ability not in self.__rights:
            self.__rights.append(ability)

    def takeAwayAbility(self, ability):
        self.__rights.remove(ability)

    def getAbilities(self):
        return self.__rights

    def getId(self):
        return self.__id

    def getName(self):
        return self.__name

    def getState(self):
        return self.__state

    def checkRights(self, ability):
        return ability in self.__rights

    def __eq__(self, other):
        return self.__id == other

    def getLastId(self):
        return self.__lastId


class Users:
    def __init__(self):
        self.__users = []
        self.__rightsEnum = Rights()
        self.__initUsers()

    def __addUser(self, id, name):
        check = self.__getUser(id)
        if check:
            return check
        user = User(id, name)
        self.__users.append(user)
        return user

    def newUser(self, id, name):
        self.__addUser(id, name)
        self.__updateUsers()

    def __getUser(self, id) -> User:
        for user in self.__users:
            if user == id:
                return user
        return None

    def getUserState(self, id):
        user = self.__getUser(id)
        if not user:
            return None
        return user.getState()

    def __updateUsers(self):
        with open("users", 'w+') as userFile:
            data = ''
            for user in self.__users[1:]:
                line = f'{user.getId()};{user.getName()};{",".join(user.getAbilities())}\n'
                data += line
            userFile.write(data)

    def __initUsers(self):
        adminId = 548374829
        admin = self.__addUser(adminId, 'Admin')
        adminRights = self.__rightsEnum.getRightSetsNames()
        print(adminRights)
        for right in adminRights:
            admin.giveAbility(right)
        try:
            with open("users", 'r+') as userFile:
                data = userFile.read()
                for line in data.split('\n'):
                    if len(line) > 2:
                        id, name, rights = line.split(';')
                        if id not in self.__users:
                            user = self.__addUser(id, name)
                            for ability in rights.split(','):
                                user.giveAbility(ability)
        except:
            print('Userlist not loaded')

    def giveAbility(self, userId, ability):
        user = self.__getUser(userId)
        if user:
            user.giveAbility(ability)
            self.__updateUsers()

    def takeAbility(self, userId, ability):
        user = self.__getUser(userId)
        if user:
            user.takeAwayAbility(ability)
            self.__updateUsers()

    def checkAbility(self, userId, ability):
        setName = ''
        if ability in self.__rightsEnum.getRightSetsNames():
            setName = ability
        else:
            setName = self.__rightsEnum.getSetName(ability)
        if setName:
            user = self.__getUser(userId)
            if user:
                return user.checkRights(setName)
        return False

    def checkUser(self, userId):
        return userId in self.__users

    def getUserName(self, uid):
        user = self.__getUser(uid)
        return user.getName() if user else None

    def allAbilities(self):
        return self.__rightsEnum.getRightSetsNames()

    def userStateChanged(self, userId, newState, onlyCheck=False):
        user = self.__getUser(userId)
        if user:
            if user.checkRights(self.__rightsEnum.getSetName(newState)):
                if not onlyCheck:
                    user.moveTo(newState)
                self.writeAction(userId, newState)
                return True
        return False

    def writeAction(self, uid, action):
        try:
            with open('actions.log', 'a+') as log:
                line = f'{uid} make {action}\n'
                log.write(line)
        except:
            pass

    def userCallBackstate(self, userId):
        user = self.__getUser(userId)
        if user:
            print('+')
            return user.backState()
        return 'Меню'

    def userChangeObject(self, userId, rbs=None, cell=None):
        user = self.__getUser(userId)
        if cell:
            cell = [cell]
        if user:
            user.setObject(rbs=rbs, cells=cell)

    def getUserObject(self, userId, cell=True):
        user = self.__getUser(userId)
        user.getObject(cell)

    def getUsers(self):
        return [f'/id{user.getId()} {user.getName()}' for user in self.__users]

    def getUserRights(self, uid):
        user = self.__getUser(uid)
        if user:
            return user.getAbilities()
        return []

    def getUserLastId(self, uid):
        user = self.__getUser(uid)
        if user:
            return user.getLastId()
        return None
