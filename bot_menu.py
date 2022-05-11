import sys
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def node_0(kwargs={}):
    if kwargs['db_vkinder'].check_user(kwargs['user_id']):
        return {'menu_namber': '02', 'photo_list': []}
    else:
        return {'menu_namber': '01', 'photo_list': []}


def node_01(kwargs={}):
    return {'menu_namber': '01', 'photo_list': []}


def node_02(kwargs={}):
    if kwargs['new_message'] == menu_dict['01']['keyboard'][0]['text']:#'Канэчно хачу!':
        user_information_dict = kwargs['vk'].user_information(kwargs['user_id'])
        check_list = kwargs['db_vkinder'].check_user_list(kwargs['user_id'])
        kwargs['db_vkinder'].add_data('User', [{'id': kwargs['user_id'], 'name': user_information_dict['name']}])
        kwargs['vk'].answer(kwargs['user_id'], 'Подожди пока подберу для тебя кандидатов ;)')
        candidates = kwargs['vk'].pair_search(user_information_dict)
        if check_list:
            candidates = iter(list(filter(lambda x: x['id'] not in check_list, candidates)))
        else:
            candidates = iter(candidates)
        return {'menu_namber': '021', 'candidates': candidates, 'photo_list': []}
    else:
        return '022'


def node_021(kwargs={}):
    return next_candidate(kwargs['candidates'], kwargs['vk'])


def node_0221(kwargs={}):
    if kwargs['new_message'] == menu_dict['0221']['keyboard'][0]['text']:
        reaction = 1
    elif kwargs['new_message'] == menu_dict['0221']['keyboard'][1]['text']:
        reaction = 2
    elif kwargs['new_message'] == menu_dict['0221']['keyboard'][2]['text']:
        reaction = 3
    else:
        sys.exit()
    if reaction:
        kwargs['db_vkinder'].add_data('User', [{
            'id': kwargs['candidate']['id'],
            'name': f"{kwargs['candidate']['first_name']} {kwargs['candidate']['last_name']}"}])
        kwargs['db_vkinder'].add_data('Photo', kwargs['photo_list'])
        kwargs['db_vkinder'].add_data('User_viewer', [{
            'reaction': reaction,
            'viewer_id': kwargs['user_id'],
            'viewed_id': kwargs['candidate']['id']}])
    return next_candidate(kwargs['candidates'], kwargs['vk'])


def next_candidate(candidates, vk):
    photo_list = []
    while not photo_list:
        try:
            candidate = candidates.__next__()
        except StopIteration:
            pass
        photo_list = vk.get_user_photos(candidate['id'])
        if photo_list:
            menu_dict['0221']['message'] = (f"https://vk.com/id{candidate['id']}, "
                                            f"{candidate['first_name']} {candidate['last_name']}")
            return {'photo_list': photo_list, 'menu_namber': '0221', 'candidate': candidate}


menu_dict = {
    '0': {'func': node_0,
          'message': 'Привет, Красавчег!',
          'keyboard': []},
    '01': {'func': node_01,
           'message': 'Хочешь найдем тебе пару? \n Выбери вариант.',
           'keyboard': [{'text': 'Канэчно хачу!', 'color': VkKeyboardColor.NEGATIVE},
                        {'text': 'Да чота лень!', 'color': VkKeyboardColor.SECONDARY}]},
    '02': {'func': node_02,
           'message': 'Рад снова видеть тебя!. Продолжим?\n Выбери вариант.',
           'keyboard': [{'text': 'Канэчно хачу!', 'color': VkKeyboardColor.NEGATIVE},
                        {'text': 'Да чота лень!', 'color': VkKeyboardColor.SECONDARY}]},
    '021': {'func': node_021,
            'message': 'Ты готов?!',
            'keyboard': [{'text': 'ДААА!', 'color': VkKeyboardColor.NEGATIVE}]},
    '0221': {'func': node_0221,
             'keyboard': [{'text': 'Маловато!', 'color': VkKeyboardColor.SECONDARY},
                          {'text': 'Вах!', 'color': VkKeyboardColor.NEGATIVE},
                          {'text': 'Ну...', 'color': VkKeyboardColor.PRIMARY}]}
}
