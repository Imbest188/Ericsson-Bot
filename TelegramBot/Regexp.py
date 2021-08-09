import re


class RegExp:
    @staticmethod
    def findMsisdn(arg):
        arg = arg.replace('+', '').replace(' ', '')
        prefix = '38072'
        result = re.findall(r'3?8?0?72\d{7}', arg)
        if len(result):
            result = result[0]
            result = prefix[:12 - len(result)] + result
        return result

    @staticmethod
    def findDip(arg):
        result = re.findall(r'\d{1,3}RBL2', arg)
        return result

    @staticmethod
    def findRbs(arg):
        arg = arg.lower().replace('lu', '').replace('g', '')
        prefix = 'LUG00'
        result = re.findall(r'^\d{1,4}$', arg.lower())
        if len(result):
            result = result[0]
            result = prefix[:6 - len(result)] + result.upper()
        return result

    @staticmethod
    def findCell(arg):
        arg = arg.lower().replace('lu', '').replace('g', '')
        arg = arg.replace('а', 'a').replace('б', 'b').replace('с', 'c')
        arg = arg.replace('_1', 'a').replace('_2', 'b').replace('_3', 'c')
        prefix = 'LUG00'
        result = re.findall(r'^\d{1,4}[abc]', arg)
        if len(result):
            result = result[0]
            result = prefix[:7 - len(result)] + result.upper()
        return result


