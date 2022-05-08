import sys

from vk_class import VKclass

if __name__ == '__main__':
    f = open('token_vk.txt', 'r')
    token = f.readline().strip()
    token_group = f.readline().strip()
    vk = VKclass(token, token_group)
    new_message = ''
    message_id = 0
    user_id = ''
    while new_message != 'q':
        new_message = vk.new_message()
        user_id = new_message['user_id']
        if message_id == 0:
            vk.answer(user_id, message_id, 'Хочешь найдем тебе пару? \n Выбери вариант.', False)
            message_id = 1
        elif message_id == 1:
            if new_message['text'] == 'Канэчно хачу!':
                candidates = iter(vk.user_information(user_id))
                candidate = candidates.__next__()
            elif new_message['text'] == 'Дальше!':
                candidate = candidates.__next__()
            else:
                sys.exit()
            cand_str = f"https://vk.com/id{candidate['id']}, {candidate['first_name']}, {candidate['last_name']}"
            vk.answer(user_id, message_id, cand_str, True, candidate['id'])

