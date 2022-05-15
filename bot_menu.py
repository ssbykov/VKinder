import sys
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


# функция формирования первоначального полного списка кандидатов с учетом уже просмотренных
def init_candidates(kwargs):
    user_id = kwargs['new_message']['user_id']
    user_information_dict = kwargs['vk'].user_information(user_id)
    check_list = kwargs['db_vkinder'].check_user_list(user_id)
    kwargs['db_vkinder'].add_user({'id': user_id, 'name': user_information_dict['name']})
    kwargs['vk'].answer(user_id, 'Подожди пока подберу для тебя кандидатов ;)')
    candidates = kwargs['vk'].pair_search(user_information_dict)
    if check_list:
        candidates = iter(list(filter(lambda x: x['id'] not in check_list, candidates)))
    else:
        candidates = iter(candidates)
    return {'menu_namber': '021', 'candidates': candidates, 'photo_list': []}


# функция формирования данных по кандидату для отправки в чат
def next_candidate(vk, db_vkinder, candidates, user_id):
    photo_list = []
    while not photo_list:
        try:
            candidate = candidates.__next__()
        except StopIteration:
            # дописать логику!!!
            pass
        photo_list = vk.get_user_photos(candidate['id'])
        if photo_list:
            menu_dict['0221']['message'] = (
                f"https://vk.com/id{candidate['id']}, "
                f"{candidate['first_name']} {candidate['last_name']}"
            )
            add_new_user_base(db_vkinder, candidate, photo_list, user_id)
            return {'menu_namber': '0221', 'candidate': candidate, 'photo_list': photo_list}

def add_new_user_base(db_vkinder, candidate, photo_list, user_id):
    db_vkinder.add_user({
        'id': candidate['id'],
        'name': f"{candidate['first_name']} {candidate['last_name']}"})
    db_vkinder.add_user_photos(photo_list)
    db_vkinder.add_user_viewer({
        'reaction': 1,
        'viewer_id': user_id,
        'viewed_id': candidate['id']})

#обработка первого сообщения (уроверь 1) при входе пользователя в чат (проверка наличия данных по пользователю в базе)
def node_0(kwargs: dict):
    if kwargs['db_vkinder'].check_user(kwargs['new_message']['user_id']):
        return {'menu_namber': '02', 'photo_list': []}
    else:
        return {'menu_namber': '01', 'photo_list': []}

#обработка действия (уровень 2) пользователь первый раз
def node_01(kwargs: dict):
    if kwargs['new_message']['text'] == menu_dict['01']['keyboard'][0]['text']:
        return init_candidates(kwargs)
    elif kwargs['new_message']['text'] == menu_dict['01']['keyboard'][1]['text']:
        return {'menu_namber': '0', 'photo_list': []}

#обработка действия (уровень 2) пользователь уже был
def node_02(kwargs: dict):
    if kwargs['new_message']['text'] == menu_dict['01']['keyboard'][0]['text']:
        return init_candidates(kwargs)
    elif kwargs['new_message']['text'] == menu_dict['01']['keyboard'][1]['text']:
        return {'menu_namber': '0', 'photo_list': []}

#обработка действия (уроверь 3) запуск показа анкет
def node_021(kwargs: dict):
    if kwargs['new_message']['text'] == menu_dict['021']['keyboard'][0]['text']:
        return next_candidate(kwargs['vk'], kwargs['db_vkinder'], kwargs['candidates'], kwargs['new_message']['user_id'])
    elif kwargs['new_message']['text'] == menu_dict['021']['keyboard'][1]['text']:
        return {'menu_namber': '0', 'photo_list': []}

#уроверь работы с сообщением с анкетой кандидата
def node_0221(kwargs: dict):
    for kb in menu_dict['0221']['keyboard']:
        if kwargs['new_message']['text'] == kb['text']:
            reaction = kb['reaction']
            break
    if reaction:
        kwargs['db_vkinder'].udate_user_viewer({
            'reaction': reaction,
            'viewer_id': kwargs['new_message']['user_id'],
            'viewed_id': kwargs['candidate']['id']})
        return next_candidate(kwargs['vk'], kwargs['db_vkinder'], kwargs['candidates'],
                              kwargs['new_message']['user_id'])
    else:
        return {'menu_namber': '0', 'photo_list': []}

def set_like(kwargs: dict):
    attachment = kwargs['db_vkinder'].get_user_photos(kwargs['new_message']['viewed_id'])
    params ={
        'attachment': attachment,
        'message': kwargs['new_message']['text'],
        'peer_id': kwargs['new_message']['peer_id'],
        'conversation_message_id': kwargs['new_message']['conversation_message_id'],
        'keyboard': kwargs['new_message']['keyboard']
    }
    photo_id = kwargs['db_vkinder'].like_user_photo(
        kwargs['new_message']['viewed_id'],
        kwargs['new_message']['photo_like']
    )
    kwargs['vk'].like(
        kwargs['new_message']['user_id'],
        kwargs['new_message']['viewed_id'],
        photo_id
    )
    kwargs['vk'].edit_message(params)

menu_dict = {
    '0': {'func': node_0,
          'message': 'Пока, Красавчег!',
          'keyboard': []},
    '01': {'func': node_01,
           'message': 'Привет, Красавчег!\nХочешь найдем тебе пару? \n Выбери вариант.',
           'keyboard': [{'text': 'Канэчно хачу!', 'color': VkKeyboardColor.NEGATIVE},
                        {'text': 'Да чота лень!', 'color': VkKeyboardColor.SECONDARY}]},
    '02': {'func': node_02,
           'message': 'Привет, Красавчег!\nРад снова видеть тебя!. Продолжим?\n Выбери вариант.',
           'keyboard': [{'text': 'Канэчно хачу!', 'color': VkKeyboardColor.POSITIVE},
                        {'text': 'Да чота лень!', 'color': VkKeyboardColor.NEGATIVE}]},
    '021': {'func': node_021,
            'message': 'Ты готов?!',
            'keyboard': [{'text': 'ДААА!', 'color': VkKeyboardColor.POSITIVE},
                         {'text': 'Не, передумал.', 'color': VkKeyboardColor.NEGATIVE}]},
    '0221': {'func': node_0221,
             'keyboard': [{'text': 'Ну не знаю...', 'color': VkKeyboardColor.PRIMARY, 'reaction': 1},
                          {'text': 'Вах!', 'color': VkKeyboardColor.POSITIVE, 'reaction': 2},
                          {'text': 'Ну нет!', 'color': VkKeyboardColor.NEGATIVE, 'reaction': 3},
                          {'text': 'Достаточно.', 'color': VkKeyboardColor.PRIMARY, 'reaction': 0},
                          {'text': ''}]}
}
