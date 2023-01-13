import telebot
from telebot import types
from kafka import KafkaConsumer,KafkaProducer

class Connect_Kafka: #Универсальный класс, через через методы которого можно создать объеты продюсера и консьюмера кафки. В качестве аргументов для создания объекта класса принимает названия топиков для продюсера, консьюмера и адрес, к которому подключается кафка. Потом, через вывзовы соответстсующих методов объекта возвращаются новые объеты - продюсер или консьюмер кафки.
    def __init__(self, topic_name_producer, topic_name_consumer, servers): #Конструктор класса, где заполняются поля названий топиков и адрес
        self._topic_name_producer=topic_name_producer
        self._topic_name_consumer=topic_name_consumer
        self._servers=servers
    def connect_kafka_producer(self): #Метод, возвращающий объект (массив), состоящий из объекта продюсера и названия топика, куда будет писать продюсер. Сделано так, чтобы при каждом вызове метода publish_message из класса Kafka_Functions не надо было передавать имя топика, куда писать продюсер будет.
        producer=[None,None]
        try:
            producer[0] = KafkaProducer(bootstrap_servers=[self._servers], api_version=(0, 10)) #Подключение продюсера к брокеру сообщений
            producer[1] = self._topic_name_producer #Второй элемент массива - имя топика продюсера
        except Exception as ex: #Обрабатываемое исключение при выполнении двух предыдущих строк
            print('Exception while connecting Kafka producer')
            print(str(ex))
        finally:
            return producer # В любом случае, было исключени или нет, возвращаем объект, возможно, сотоящий из [None,None]
    def connect_kafka_consumer(self): #Метод, аналогичный предыдущему для подключения консьюмера к брокеру сообщений
        consumer=None
        try:
            consumer=KafkaConsumer(self._topic_name_consumer,bootstrap_servers=self._servers)
        except Exception as ex:
            print('Exceprion while connecting Kafka consumer')
            print(str(ex))
        finally:
            return consumer

class Kafka_Functions: #Класс, через объект которого можно принимать и отправлять сообщения на сервер брокера
    def __init__(self, producer, consumer): #Коснтруктор, который принимает объект "моего продюсера" (массив из объекта продюсера и имени его топка) и объект конмьюмера
        self._producer=producer
        self._consumer=consumer
    def publish_message(self,value): #Метод, с помощью которого переводим сообщение в байты и отправляем сообщение брокеру через метод объекта "моего продюсера" под 0 индексом, название топика, соответственно, под 1 индексом.
        try:
            key_bytes = bytes('raw', encoding='utf-8')
            value_bytes = bytes(value, encoding='utf-8')
            self._producer[0].send(self._producer[1], key=key_bytes, value=value_bytes)
            self._producer[0].flush()
            print('Message published successfully.')
        except Exception as ex: #Обрабатываемое исключение при выолнении строк кода выше
            print('Exception in publishing message')
            print(str(ex))
    def recieve_message(self): #Метод, аналогичный предыдущему, для принятия по однму сообщению от брокера за каждый вызов метода.
        recieved_message=None
        try:
            recieved_message=next(self._consumer)
        except Exception as ex:
            print('Exceprion while recieving message from Kafka Consumer')
            print(str(ex))
        finally:
            return recieved_message

class Bot_Functions: #Класс, описывающий всевозможные фнукции бота
    def __init__(self,kafka_functions): #Конструктор, через который принимается объект Kafka_Functions для основного метода бота (get_sentence_mood), чтобы можно было посредством методов из класса Kafka_Functions отправить и принять сообщение от сервера
        self._kafka_functions=kafka_functions
    def say_hello(self):
        return "Вы кто такие? Я вас не звал, идите нахуй!"
    def who_is_pidor(self):
        return "Пидор - это я, пидоры - это мы, пидоры - это лучшие люди страны!"
    def analys(self):
        return "Я же вначале тебе написал: ПРОСТО НАБЕРИ ТЕКСТ ДЛЯ АНАЛИЗА НАСТРОЕНИЯ, А НЕ НАЖИМАЙ КНОПОЧКИ, НЕ ТРОГАЙ СВЕЧУ (лишний раз) !!!"
    def get_sentence_mood(self,message):
        self._kafka_functions.publish_message(message) #Отправляем сообщение на сервер через брокер сообщений
        msg = self._kafka_functions.recieve_message() # Принимаем сообщение от сервера через брокер сообщений
        if msg.value.decode('ascii')=='positive': # Декодируем сообщение, так как остылается и принимается оно как набор байтов
            return "А где товарищ депрессия? Ведь это сообщение ПОЗИТИВНОЕ :) !"
        else:
            return "Мысли позитивно! Иначе так и будешь мне присылать НЕГАТИВНЫЕ сообщения :(!"

class Bot_Output: #Класс, который, в зависимости от того, какой аргумент будет передан основному методу этого класса (result), вызовет соответствующий метод класса функций бота (Bot_Functions) и вернет его нам для последующего вывода клиенту в телеграме
    def __init__(self,func): #Конструктор, принимающий объект класса функций бота (Bot_Functions)
        self._func = func
    def result(self,user_text):
        if (user_text=="Кто пидор?"):
            return self._func.who_is_pidor()
        elif (user_text=="Привет"):
            return self._func.say_hello()
        elif (user_text=="Анализ текста"):
            return self._func.analys()
        else:
            return self._func.get_sentence_mood(user_text)


bot = telebot.TeleBot('5988110099:AAGn3-Sw5MSG7L8r6rJ_XdIh1eDoEh2sZiQ') #Создание объекта бота телеграм
kafka=Connect_Kafka('recieveMessage','sendMessage','broker:29090')  #Создаем объект, через который впоследствии создадим другие объекты - продюсера и консьюмера кафки
producer=kafka.connect_kafka_producer()#Создаем продюсер
consumer=kafka.connect_kafka_consumer()#Создаем консьюмер
kafka_functions=Kafka_Functions(producer,consumer)#Создаем объект, через который впоследствии будем вызывать методы для работы с продюсером и консьюмером кафки
func=Bot_Functions(kafka_functions) #Создаем объект, через который можно будет вызывать функции бота
output=Bot_Output(func) #Создаем объект, через который будет вызываться соответствующая функция бота и возвращаться результат ее работы

@bot.message_handler(commands=['start']) #Используем декоратор message_handler с параметром commands=['start'], чтобы сказать, что функция снизу start (message) будет являться функцией обработки команды start боту
def start(message): 
    name = f'Привет, <b><u>' \
           f'{message.from_user.first_name} {message.from_user.last_name}' \
           f'</u></b>'
    bot.send_message(message.chat.id, name, parse_mode='html')
    bot.send_message(message.chat.id, "Для анализа текста на настроение просто введите его в сообщении боту (бот только что из Англии, рускаго ни знаит), и отправьте его, в ответе получите настроение текста :)",parse_mode='html')
    bot.send_message(message.chat.id, "Для вывода дополнительных функций введите команду /help", parse_mode='html')
    bot.send_message(message.chat.id, "ВНИМАНИЕ: НЕСАНКЦИОНИРОВАННЫЙ ДОСТУП К БОТУ ВЛЕЧЕТ ЗА СОБОЙ ИЗБИЕНИЕ ССАНЫМИ ТРЯПКАМИ!!!", parse_mode='html')

@bot.message_handler(commands=['help']) #Используем декоратор message_handler с параметром commands=['help'], чтобы сказать, что функция снизу help (message) будет являться функцией обработки команды help боту
def help(message):
    markup = types.ReplyKeyboardMarkup()
    hello = types.KeyboardButton('Привет')
    pidor = types.KeyboardButton('Кто пидор?')
    text = types.KeyboardButton('Анализ текста')
    markup.add(hello, pidor, text)
    bot.send_message(message.chat.id, 'Выберите нужную команду:', reply_markup=markup)

@bot.message_handler() #Используем декоратор message_handler без параметров, чтобы сказать, что функция снизу нужна для обработки всех остальных сообщений
def get_user_text(message): 
    bot.send_message(message.chat.id,output.result(message.text),parse_mode='html') #Отправляем ответ в телеграм, в котором содержится результат вызова метода result класса Bot_Output в зависимости от принятого от пользователя сообщения
bot.polling(none_stop=True, interval=0) #Постоянный опрос на наличие новых сообщений от сервера Telegram
