import sys
from vk_class import VKclass
from sql_class import VkinderDB

if __name__ == '__main__':
    f = open('token_vk.txt', 'r')
    token = f.readline().strip()
    token_group = f.readline().strip()
    vk = VKclass(token, token_group)
    f = open('db_pass.txt', 'r')
    db_pass = f.readline().strip()
    db_vkinder = VkinderDB('postgres', db_pass, 'vkinder')
    db_vkinder.create_database()
    db_vkinder.create_database_tables()
    new_message = ''
    message_id = 0
    user_id = ''
    candidates = iter([])
    while new_message != 'q':
        new_message = vk.new_message()
        user_id = new_message['user_id']
        if message_id == 0:
            # check_user = db_vkinder.check_user(user_id)
            # if check_user:
            #     vk.answer(user_id, 3, 'Рады снова видеть Вас!.\n Выбери вариант.', True, False)
            # else:
            vk.answer(user_id, message_id, 'Хочешь найдем тебе пару? \n Выбери вариант.', True, False)
            message_id = 1
        elif message_id == 1:
            if new_message['text'] == 'Канэчно хачу!':
                user_information_dict = vk.user_information(user_id)
                check_list = db_vkinder.check_user_list(user_id)
                db_vkinder.add_data('User', [{'id': user_id, 'name': user_information_dict['name']}])
                vk.answer(user_id, 2, 'Подождите пока мы подберем для вас кандидатов...', False, False)
                candidates = vk.pair_search(user_information_dict)
                if check_list:
                    candidates = iter(list(filter(lambda x: x['id'] not in check_list, candidates)))
                else:
                    candidates = iter(candidates)
                reaction = 0
            elif new_message['text'] == 'Маловато!':
                reaction = 1
            elif new_message['text'] == 'Вах!':
                reaction = 2
            elif new_message['text'] == 'Ну...':
                reaction = 3
            else:
                sys.exit()
            if reaction:
                db_vkinder.add_data('User', [{'id': candidate['id'], 'name': candidate_name}])
                db_vkinder.add_data('Photo', photo_list)
                db_vkinder.add_data('User_viewer', [{'reaction': reaction, 'viewer_id': user_id, 'viewed_id': candidate['id']}])
            photo_list = []
            while not photo_list:
                try:
                    candidate = candidates.__next__()
                except StopIteration:
                    pass
                candidate_name = f"{candidate['first_name']} {candidate['last_name']}"
                cand_str = f"https://vk.com/id{candidate['id']}, {candidate_name}"
                photo_list = vk.get_user_photos(candidate['id'])
                if photo_list:
                    vk.answer(user_id, message_id, cand_str, True, True, photo_list)



