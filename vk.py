import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

f = open('token.txt', 'r')
token_vk = f.readline()

token = token_vk

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request.lower() == "привет" or "привет!":
                write_msg(event.user_id, f"Хай, {event.user_id} напиши команду 'найти пару' для начала поиска")
            elif request.lower() == 'найти пару' or 'наити пару!':
                write_msg(event.user_id, f"Временно идут тех работы")
            elif request.lower() == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")