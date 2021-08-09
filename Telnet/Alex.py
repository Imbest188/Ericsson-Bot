class EricssonBscCommands:
    @staticmethod
    def rxasp(moty='RXOCF') -> str:
        return "RXASP:MOTY=" + moty + ";"

    @staticmethod
    def rlcrp(cell='ALL'):
        return "RLCRP:CELL=" + cell + ";"

    @staticmethod
    def rlstp(cell='ALL', state='HALTED'):
        return "RLSTP:CELL=" + cell + ",STATE=" + state + ";"

    @staticmethod
    def rlstc(cell, chgr='ALL', state='HALTED'):
        return "RLSTC:CELL=" + cell + f", CHGR={chgr}, STATE=" + state + ";"

    @staticmethod
    def rldep(cell='ALL', ext=False):
        extarg = ''
        if ext:
            extarg = ',EXT'
        return f"RLDEP:CELL={cell}{extarg};"

    @staticmethod
    def rlcfp(cell):
        return "RLCFP:CELL=" + cell + ";"

    @staticmethod
    def rlcfi(cell, dchArray, chgr=0):
        return f"RLCFI:CELL={cell},DCHNO={'&'.join(dchArray)},CHGR={chgr};"

    @staticmethod
    def rxapp(tg):
        return f"RXAPP:MO={tg};"

    @staticmethod
    def dtstp(dip=''):
        if not dip:
            dip = 'ALL'
        elif not dip.endswith('RBL2'):
            dip += 'RBL2'
        return f"DTSTP:DIP={dip};"

    @staticmethod
    def rrgsp():
        return 'RRSGP: SCGR = ALL;'

    @staticmethod
    def rlcfe(cell, dchArray, chgr=0):
        return f"RLCFE:CELL={cell},DCHNO={'&'.join(dchArray)},CHGR={chgr};"

    @staticmethod
    def rlccc(cell, chgr=0, sdcch=0):
        return f'RLCCC: CELL = {cell}, CHGR = {chgr}, SDCCH = {sdcch};'

    @staticmethod
    def rlnrp(cell, utran=False):
        utranString = ''
        if utran:
            utranString = ',UTRAN'
        return "RLNRP:CELL=" + cell + ",CELLR=ALL" + utranString + ';'

    @staticmethod
    def rlstc(cell, state='HALTED'):
        return "RLSTC:CELL=" + cell + ",STATE=" + state + ";"

    @staticmethod
    def rxtcp(cell=''):
        cellArg = ''
        if len(cell):
            cellArg = ",CELL=" + cell
        return "RXTCP:MOTY=RXOTG" + cellArg + ";"

    @staticmethod
    def rxmsp(moty='RXOTG', tg=''):
        if len(tg):
            return "RXMSP:MO=" + tg + ",SUBORD;"
        return "RXMSP:MOTY=" + moty + ";"

    @staticmethod
    def rxbli(tg, trx=None):
        mo = 'RXOTG-'
        if mo in tg:
            mo = ''
        if trx:
            trx = '-' + trx
            mo = 'RXOTRX'
        else:
            trx = ''
        text = f"RXBLI:MO={mo}{tg}{trx},SUBORD,FORCE;"
        return text

    @staticmethod
    def rxble(tg, trx=None):
        mo = 'RXOTG-'
        if mo in tg:
            mo = ''
        if trx:
            trx = '-' + trx
            mo = 'RXOTRX'
        else:
            trx = ''
        text = f"RXBLE:MO={mo}{tg}{trx},SUBORD;"
        return text

    @staticmethod
    def rlsbc(cell, state=False, cro=None):
        __state = 'NO'
        if state:
            __state = 'YES'
        if cro != None:
            return f'RLSBC:CELL={cell},CRO={cro};'
        return f'RLSBC:CELL={cell},cb={__state};'

    @staticmethod
    def rlsbp(cell='ALL'):
        return f'RLSBP:CELL={cell};'

    @staticmethod
    def rlnri(cell, cellr):
        return f'RLNRI:CELL={cell},CELLR={cellr},SINGLE;'

    @staticmethod
    def rlnrc(cell, cellr):
        cs = 'YES' if cell[:-1] == cellr[:-1] else 'NO'
        return f'RLNRC:CELL={cell},CELLR={cellr},CAND=BOTH,CS={cs},KHYST=6,KOFFSETP=0,' \
               f'LHYST=8,LOFFSETP=0,TRHYST=4,TROFFSETP=0,AWOFFSET=10,BQOFFSET=10;'

    @staticmethod
    def rlnre(cell, cellr):
        return EricssonBscCommands().rlnri(cell, cellr).replace('RLNRI', 'RLNRE').replace(',SINGLE', '')

    @staticmethod
    def rlmfi(cell, mbсch):
        return f'RLMFC:CELL={cell},MBCCHNO={mbсch},MRNIC;'

    @staticmethod
    def rlmfe(cell, mbсch):
        return f'RLMFE:CELL={cell},MBCCHNO={mbсch};'


class EricssonMscCommands:
    @staticmethod
    def mgtrp(msisdn) -> str:
        return f'MGTRP:MSISDN={msisdn};'

    @staticmethod
    def mgssp(imsi) -> str:
        return f'MGSSP:IMSI={imsi};'
