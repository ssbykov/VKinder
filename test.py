import vk_api
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

f = open('token.txt', 'r')
token_vk_group = f.readline()
token_vk_person = f.readline()

token_person = token_vk_person
vk_person = vk_api.VkApi(token=token_person)

def user_information():
    info = vk_person.method("status.get", {'user_id': 87343268})
    print(info)

user_information()