import vk_api
import time
from datetime import date
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import requests


class VKclass:
    URL = 'https://api.vk.com/method/'
    def __init__(self, token, token_group):
        self.token = token
        self.token_group = token_group
        self.vk = vk_api.VkApi(token=self.token_group)
        self.vk_user = vk_api.VkApi(token=self.token)
        self.longpoll = VkBotLongPoll(self.vk, group_id=213108918)

#метод обработки нового сообщения от пользователя
    def new_message(self):
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.obj.message['text'] != '':
                return {
                    'user_id': event.message['from_id'],
                    'peer_id': event.message['peer_id'],
                    'cmids': event.message['conversation_message_id'],
                    'text': event.message['text'],
                    'type': 'MESSAGE_NEW'
                }
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                if event.object['payload']['type']:
                    params = {
                        'access_token': self.token_group,
                        'v': '5.131',
                        'peer_id': event.object['peer_id'],
                        'user_id': event.object['user_id'],
                        'conversation_message_ids': event.object['conversation_message_id']
                    }
                    response = requests.get(self.URL + 'messages.getByConversationMessageId', params)
                    response = response.json()['response']['items'][0]
                    photo_like = int(event.object['payload']['type'])
                    keyboard = self._keyboard_edit(response['keyboard']['buttons'], photo_like)
                    return {
                        'viewed_id': response['text'].replace('https://vk.com/id', '').split(',')[0],
                        'text': response['text'],
                        'conversation_message_id': event.object['conversation_message_id'],
                        'peer_id': event.object['peer_id'],
                        'user_id': event.object['user_id'],
                        'type': 'MESSAGE_EVENT',
                        'photo_like': photo_like,
                        'keyboard': keyboard
                    }
                else:
                    pass

    def edit_message(self, params):
        self.vk.method('messages.edit', params)

#формирование клавиатуры для изменяемого сообщения
    def _keyboard_edit(self, keyboard_dict: dict, photo_like):
        keyboard = VkKeyboard(inline=True)
        keyboard_colors = {
            'positive': VkKeyboardColor.POSITIVE,
            'default': VkKeyboardColor.SECONDARY,
            'negative': VkKeyboardColor.NEGATIVE,
            'primary': VkKeyboardColor.PRIMARY
        }
        if keyboard_dict[1][photo_like-1]['color'] == 'negative':
            keyboard_dict[1][photo_like-1]['color'] = 'default'
        else:
            keyboard_dict[1][photo_like-1]['color'] = 'negative'
        for button in keyboard_dict[0]:
            keyboard.add_button(button['action']['label'], keyboard_colors[button['color']])
        keyboard.add_line()
        for button in keyboard_dict[1]:
            keyboard.add_callback_button(
                button['action']['label'],
                keyboard_colors[button['color']],
                payload=button['action']['payload'])
        return keyboard.get_keyboard()

    def send_message(self, params):
        self.vk_user.method('messages.send', params)

    #формирования ссобщения пользователю
    def answer(self, user_id: int, message: str, keyboard=[], photo_list=[]):
        params = {
            'user_id': user_id,
            'message': message,
            'random_id': 0
        }
        if keyboard:
            keyboard = self._keyboard(keyboard, photo_list)
            params['keyboard'] = keyboard.get_keyboard()
        if photo_list:
            params['attachment'] = ''
            if photo_list:
                for photo in photo_list:
                    params['attachment'] += f"photo{photo['user_id']}_{photo['id']},"
        self.vk.method('messages.send', params)

    # формирования клавиатуры для сообщения
    def _keyboard(self, keyboard_list: list, photo_list):
        keyboard = VkKeyboard(inline=True)
        for button in keyboard_list:
            if button['text']:
                keyboard.add_button(button['text'], button['color'])
        if len(photo_list):
            keyboard.add_line()
            for bn in range(len(photo_list)):
                if photo_list[bn]['like']:
                    keyboard.add_callback_button(f'Фото {bn + 1}', VkKeyboardColor.NEGATIVE, payload={"type": str(bn + 1)})
                else:
                    keyboard.add_callback_button(f'Фото {bn + 1}', VkKeyboardColor.SECONDARY, payload={"type": str(bn + 1)})
            keyboard.add_callback_button('Список "Вах!"', VkKeyboardColor.POSITIVE, payload={"type": 0})
        return keyboard

    #метод запроса фотографий по кандидату из соцсети
    def get_user_photos(self, user_id: int):
        params = {'owner_id': user_id, 'album_id': 'profile', 'extended': 1}
        user_photos = self.vk_user.method('photos.get', params)
        if len(user_photos['items']):
            photo_list = [{
                'id': photo['id'],
                'url_photo': photo['sizes'][-1]['url'],
                'user_id': photo['owner_id'],
                'likes': photo['likes']['count'],
                'like': False
            } for photo in user_photos['items']]
            photo_list = sorted(photo_list, key=lambda p: p['likes'], reverse=True)[:3]
            return photo_list

    #запрос информации по ползователю из соцсети для получения параметров для формирования списка кандидатов
    def user_information(self, user_id: int):
        params = {'user_ids': user_id, 'fields': 'bdate,sex,city'}
        user_inf = self.vk.method('users.get', params)
        user_year = int(user_inf[0]['bdate'][-4:])
        age = int(date.today().year) - user_year
        if user_inf[0]['sex'] == 2:
            sex = 1
        elif user_inf[0]['sex'] == 1:
            sex = 2
        else:
            sex = 0
        city_person = user_inf[0]['city']['id']
        return {
            'name': f"{user_inf[0]['first_name']} {user_inf[0]['last_name']}",
            'age': age,
            'birth_year': user_year,
            'sex': sex,
            'city_person': city_person
        }

    #запрос анкет кандидатов из соцсети
    def pair_search(self, params: dict, offset='0'):
        candidates = []
        for birth_year in range(params['birth_year'] + 4, params['birth_year'] - 4, -1):
            add_candidates = self.vk_user.method('users.search', {
                'offset': offset,
                'count': '1000',
                'fields': ['photo', 'has_photo'],
                'city': params['city_person'],
                'sex': params['sex'],
                'status': '1',
                'birth_year': birth_year,
                'age_from': params['age'] - 3,
                'age_to': params['age'] + 3,
                'has_photo': 1
            })
            add_candidates = list(filter(lambda x: x['is_closed'] == False, add_candidates['items']))
            candidates += add_candidates
            time.sleep(0.3)
        return candidates

    def like(self, user_id, owner_id, photo_id):
        params = {'type': 'photo', 'user_id': user_id, 'owner_id': owner_id, 'item_id': photo_id}
        check_like = self.vk_user.method('likes.isLiked', params)
        if not check_like['liked']:
            params = {'type': 'photo', 'owner_id': owner_id, 'item_id': photo_id}
            self.vk_user.method('likes.add', params)
        else:
            self.vk_user.method('likes.delete', params)
