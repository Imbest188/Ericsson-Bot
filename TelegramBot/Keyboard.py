from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


class Keyboard:
    def __init__(self):
        self.buttons = []

    def addButton(self, name, function):
        button = Button(name, function)
        self.buttons.append(button)

    def createInlineKeyboard(self, set):
        reply_markup = InlineKeyboardMarkup(self.__createInlineKeyboard(set))
        return reply_markup

    def createReplyKeyboard(self, set):
        reply_markup = ReplyKeyboardMarkup(self.__createKeyboard(set))
        return reply_markup

    def __createInlineKeyboard(self, set):
        keyboard = [
            [button.getInlineButton() for button in self.__getButtons(set)]
        ]
        return keyboard

    def __createKeyboard(self, set):
        keyboard = []
        print(set)
        for part in set:
            keyboard.append([KeyboardButton(button) for button in part])
        return keyboard

    def __getButtons(self, set):
        result = []
        for button in self.buttons:
            if button in set:
                result.append(button)
        return result


class Button:
    def __init__(self, text, function):
        self.text = text
        self.function = function

    def getInlineButton(self):
        return InlineKeyboardButton(self.text, callback_data=self.function)

    def getButton(self):
        return KeyboardButton(self.text)
