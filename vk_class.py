import vk_api
import time
from datetime import date
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


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
                    'cmids': event.message['conversation_message_id'],
                    'text': event.message['text'],
                    'type': 'MESSAGE_NEW'
                }
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                if event.object['payload']['type'] == 'like':
                    return {
                        'user_id': event.object['user_id'],
                        'text': 'Список "Вах"!',
                        'type': 'LIKE_LIST',
                    }
                if event.object['payload']['type'] == 'new':
                    return {
                        'user_id': event.object['user_id'],
                        'text': 'Новые',
                        'type': 'NEW_LIST',
                    }
                else :
                    params = {
                        'peer_id': event.object['peer_id'],
                        'user_id': event.object['user_id'],
                        'conversation_message_ids': event.object['conversation_message_id']
                    }
                    response = self.vk.method('messages.getByConversationMessageId', params)['items'][0]
                    photo_like = event.object['payload']['type']
                    photo_like_key = list(photo_like.keys())[0]
                    owner_id = response['text'].replace('https://vk.com/id', '').split(',')[0]
                    if photo_like_key == 'like':
                        keyboard_type = '41'
                    else:
                        keyboard_type = '42'
                    photo_list = self.photo_like(event.object['user_id'], owner_id, photo_like[photo_like_key])
                    return {
                        'viewed_id': owner_id,
                        'text': response['text'],
                        'conversation_message_id': event.object['conversation_message_id'],
                        'user_id': event.object['user_id'],
                        'type': 'LIKE',
                        'keyboard_type': keyboard_type,
                        'photo_list': photo_list,
                    }

    #изменение сообщения с анкетой
    def edit_message(self, user_id: int, message: str, keyboard, photo_list, conversation_message_id):
        edit_params = {
            'peer_id': user_id,
            'message': message,
            'conversation_message_id': conversation_message_id
        }
        params = edit_params | self.get_params(keyboard, photo_list)
        self.vk.method('messages.edit', params)

    #формирования ссобщения пользователю
    def answer(self, user_id: int, message: str, keyboard=[], photo_list=[]):
        answer_params = {
            'user_id': user_id,
            'message': message,
            'random_id': 0
        }
        params = answer_params | self.get_params(keyboard, photo_list)
        self.vk.method('messages.send', params)

    #формирование параметров клавиатуры и фото для передачи сообщения с анкетой
    def get_params(self, keyboard: list, photo_list: list):
        params = {}
        if keyboard:
            keyboard = self._keyboard(keyboard, photo_list)
            params['keyboard'] = keyboard.get_keyboard()
        if photo_list:
            params['attachment'] = ''
            if photo_list:
                for photo in photo_list:
                    params['attachment'] += f"photo{photo['user_id']}_{photo['id']},"
        return params

    # формирования клавиатуры для сообщения
    def _keyboard(self, keyboard_list: list, photo_list):
        keyboard = VkKeyboard(inline=True)
        for button in keyboard_list:
            if 'text' in list(button.keys()):
                if button['text']:
                    keyboard.add_button(button['text'], button['color'])
                else:
                    keyboard.add_line()
            else:
                if keyboard_list[-1]['label'] == 'Новые':
                    type_key = 'like_like'
                else:
                    type_key = 'like'
                for bn in range(len(photo_list)):
                    if photo_list[bn]['like']:
                        keyboard.add_callback_button(
                            f'Фото {bn + 1}',
                            VkKeyboardColor.NEGATIVE,
                            payload={'type': {type_key: str(photo_list[bn]['id'])}}
                        )
                    else:
                        keyboard.add_callback_button(
                            f'Фото {bn + 1}',
                            VkKeyboardColor.SECONDARY,
                            payload={'type': {type_key: str(photo_list[bn]['id'])}}
                        )
                keyboard.add_callback_button(button['label'], button['color'], payload=button['payload'])
        return keyboard

    #метод запроса фотографий по кандидату из соцсети
    def get_user_photos(self, user_id: int):
        params = {'owner_id': user_id, 'album_id': 'profile', 'extended': 1}
        user_photos = self.vk_user.method('photos.get', params)
        if len(user_photos['items']):
            photo_list = [{
                'id': photo['id'],
                'user_id': photo['owner_id'],
                'likes': photo['likes']['count'],
                'like': photo['likes']['user_likes']
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

    #добавление/удаление лайка к фото
    def photo_like(self, user_id, owner_id, photo_id):
        params = {'type': 'photo', 'user_id': user_id, 'owner_id': owner_id, 'item_id': photo_id}
        check_like = self.vk_user.method('likes.isLiked', params)
        if not check_like['liked']:
            self.vk_user.method('likes.add', params)
        else:
            self.vk_user.method('likes.delete', params)
        return self.get_user_photos(owner_id)

    #получение списка избранных
    def get_like_list(self, like_list):
        params = {'user_ids': like_list}
        check_like = self.vk.method('users.get', params)
        return list(check_like)
