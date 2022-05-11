import vk_api
import time
from datetime import date
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

class VKclass:

    def __init__(self, token, token_group):
        self.token = token
        self.token_group = token_group
        self.vk = vk_api.VkApi(token=self.token_group)
        self.vk_user = vk_api.VkApi(token=self.token)
        self.longpoll = VkLongPoll(self.vk)

    def new_message(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW  and event.to_me:
                return {'user_id':event.user_id, 'text':event.text}

    def answer(self, user_id: int, message_id: int, message: str, keyboard: bool, photo_post: bool, photo_list = []):
        params = {
            'user_id': user_id,
            'message': message,
            'random_id': 0
        }
        if keyboard:
            keyboard = self._keyboard(message_id)
            params['keyboard'] = keyboard.get_keyboard()
        if photo_post and photo_list:
            params['attachment'] = ''
            if photo_list:
                for photo in photo_list:
                    params['attachment'] += f"photo{photo['user_id']}_{photo['id']},"
        self.vk.method('messages.send', params)

    def _keyboard(self, message_id: int):
        keyboard_dict = {
            0: [{'text': 'Канэчно хачу!', 'color': VkKeyboardColor.NEGATIVE},
                {'text': 'Да чота лень!', 'color': VkKeyboardColor.SECONDARY}],
            1: [{'text': 'Маловато!', 'color': VkKeyboardColor.SECONDARY},
                {'text': 'Вах!', 'color': VkKeyboardColor.NEGATIVE},
                {'text': 'Ну...', 'color': VkKeyboardColor.PRIMARY}],
            3: [{'text': 'Хачу Вах!', 'color': VkKeyboardColor.NEGATIVE},
                {'text': 'Продолжить просмотр!', 'color': VkKeyboardColor.SECONDARY}]
        }

        keyboard = VkKeyboard(one_time=True)
        for button in keyboard_dict[message_id]:
            keyboard.add_button(button['text'], button['color'])
        return keyboard

    def get_user_photos(self, user_id: int):
        params = {'owner_id': user_id, 'album_id': 'profile', 'extended': 1}
        user_photos = self.vk_user.method('photos.get', params)
        if len(user_photos['items']):
            photo_list = [{
                'id': photo['id'],
                'url_photo': photo['sizes'][-1]['url'],
                'user_id': photo['owner_id'],
                'likes': photo['likes']['count']
            } for photo in user_photos['items']]
            photo_list = sorted(photo_list, key=lambda p: p['likes'], reverse=True)[:3]
            return photo_list

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

    def pair_search(self, params: dict, offset = '0'):
        candidates = []
        for birth_year in range(params['birth_year'] + 4, params['birth_year'] + 11):
            add_candidates = self.vk_user.method('users.search',{
                'offset': offset,
                'count': '1000',
                'fields': ['photo', 'has_photo'],
                'city': params['city_person'],
                'sex': params['sex'],
                'status': '1',
                'birth_year': birth_year,
                'age_from': params['age'] - 10,
                'age_to': params['age'] - 5,
                'has_photo': 1
            })
            add_candidates = list(filter(lambda x: x['is_closed'] == False, add_candidates['items']))
            candidates += add_candidates
            time.sleep(0.3)
        return candidates
