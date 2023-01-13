from transformers import AutoTokenizer, AutoConfig, AutoModelForSequenceClassification
from kafka import KafkaConsumer, KafkaProducer

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

class InitialiseModel: #Класс, который в конструкторе инициализирует обученную и сохраненную модель и с помощью метода return_model возвращает тюпл из конфига, токенайзера и модели для последующей обработки сообщений обученной моделью.
    _label2id = {
        "negative": 0,
        "positive": 1,
    }
    _id2label = {
        0: "negative",
        1: "positive",
    }
    def __init__(self,model_path): #Коснтруктор, который принимает путь до файлов модели и в поля класса инициализирует конфиг, токенайзер и модель
        self._config = AutoConfig.from_pretrained(model_path, label2id=self._label2id, id2label=self._id2label)
        self._tokenizer = AutoTokenizer.from_pretrained(model_path)
        self._model = AutoModelForSequenceClassification.from_pretrained(model_path, config=self._config)
    def return_model(self): #Метод, возвращаюий тюпл из объектов конфига, токенайзера и модели
        return self._config,self._tokenizer,self._model

kafka=Connect_Kafka('sendMessage','recieveMessage','broker:29090') #Создаем объект, через который впоследствии создадим другие объекты - продюсера и консьюмера кафки
producer=kafka.connect_kafka_producer() #Создаем продюсер
consumer=kafka.connect_kafka_consumer() #Создаем консьюмер
kafka_functions=Kafka_Functions(producer,consumer) #Создаем объект, через который впоследствии будем вызывать методы для работы с продюсером и консьюмером кафки
initialised_model=InitialiseModel(".//model//") # Создаем объект класса с "инициализрованной" моделью.
config,tokenizer,model=initialised_model.return_model() #Возвращаем конфиг, токенайзер и модель

for message in consumer: #Цикл, который будет постоянно (пока жив брокер) ожидать появление сообщения, принимать его, обрабатывать с помощью нейросети и отсылать клиенту через вызов метода publish_message
    tensor = tokenizer(message.value.decode('ascii'), padding="max_length",  truncation=True, max_length=512, return_tensors="pt")
    logits = model(**tensor).logits
    predicted_class_id = logits.argmax().item()
    kafka_functions.publish_message(model.config.id2label[predicted_class_id])
