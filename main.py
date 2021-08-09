from Telnet.ControllerPool import BaseStationsControllersPool as BSC
from Telnet.ControllerPool import MobileSwitchingCentersPool as MSC
from TelegramBot.Bot import Bot
from TelegramBot.Regexp import RegExp

from TelegramBot.UserList import Rights
import time

if __name__ == '__main__':
    '''print(RegExp().findRbs('LUG999'),
    RegExp().findCell('LUG99'),
    RegExp().findCell('LUG999A'),
    RegExp().findCell('LUG'),
    RegExp().findRbs('UG999'))'''

    '''pool = MSC()
    pool.addController('10.20.202.20', 'Smena', 'Ericsson1@', 'MSC01')
    pool.addController('10.56.135.16', 'Administrator', 'Admin023', 'MSS02')
    print(pool.getVlrRegistrationInfo('380721531479'))
    print(pool.getVlrRegistrationInfo('380721531479'))

    print(pool.getVlrRegistrationInfo('380721531479'))
    print(pool.getVlrRegistrationInfo('380721531479'))
    print(pool.getVlrRegistrationInfo('380721531479'))'''

    #pool = BSC()
    #pool.addController('10.140.3.7', 'ts_user', 'apg43l2@', 'BSC04')
    #pool.addController('10.140.27.68', 'ts_user', 'apg43l1@', 'BSC05')
    #print(pool.getHardwareState('LUG304A'))
    #RegExp().findCell('LU1023A')
    while True:
        if 1:
            bot = Bot()
        #except:
        #    time.sleep(10)
        #r = Rights()
    #print(r.getRightSetsNames())
    #print(r.getRights(name="Просмотр"))
    '''
    pool = BSC()
    pool.addController('10.140.3.7', 'ts_user', 'apg43l2@', 'BSC04')
    pool.addController('10.140.27.68', 'ts_user', 'apg43l1@', 'BSC05')
    #pool.addController('172.25.157.99', 'administrator', 'Administrator1@', 'BSC03')
    #print(pool.getCellState('LUG304A'))
    #print(pool.getBarredCells())
    #print(pool.setCellBarredState('LUG304A', True))
    #print(pool.getBarredCells())
    #print(pool.setCellBarredState('LUG304A', False))
    #print(pool.getBarredCells())
    #print(pool.setCellHaltedState('LUG304A', True))
    #print(pool.setCellHaltedState('LUG304A', False))
    print(pool.getCellState('LUG015A'))
    print(pool.getCellState('LUG815C'))
    print(pool.getCellState('LUG816C'))
    print(pool.setCellHaltedState('LUG304A', False))
    print(pool.setObjectStateBlocked('LUG304A', True))
    print(pool.setObjectStateBlocked('LUG304A', False))
    print(pool.setCellHaltedState('LUG304A', True))
    print(pool.getDisabledTransferingGroups())
    print(pool.getHaltedCells())
    '''
