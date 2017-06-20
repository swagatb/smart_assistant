from chatterbot import ChatBot

chatbot = ChatBot(
    'My Mirror',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
)

chatbot.train("chatterbot.corpus.english")


def get_response(text):
    return chatbot.get_response(text).text
