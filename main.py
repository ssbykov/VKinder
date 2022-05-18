from vk_class import VKclass
from DBVkinder import VkinderDB
from bot_menu import menu_dict
import sys

if __name__ == '__main__':
    res_dict = {'menu_namber': '1', 'candidates': None, 'photo_list': []}
    arg_dict = {'new_message': None, 'candidates': iter([])}
    f = open('pass_vkinder.txt', 'r')
    token, token_group, group_id, db_pass = [x.strip() for x in f.readlines()]
    try:
        arg_dict['vk'] = VKclass(token, token_group, group_id)
    except Exception as e:
        print(e)
        sys.exit()
    arg_dict['db_vkinder'] = VkinderDB('postgres', db_pass, 'vkinder')
    arg_dict['db_vkinder'].create_database()
    arg_dict['db_vkinder'].create_database_tables()
    user_id = ''
    while arg_dict['new_message'] != 'q':
        arg_dict['new_message'] = arg_dict['vk'].new_message()
        if arg_dict['new_message']['type'] in ['MESSAGE_NEW', 'LIKE_LIST', 'NEW_LIST']:
            if arg_dict['new_message']['type'] == 'NEW_LIST':
                res_dict['menu_namber'] = '22'
            elif arg_dict['new_message']['type'] == 'LIKE_LIST':
                res_dict['menu_namber'] = '32'
            if res_dict['menu_namber'] == '1'\
                    or arg_dict['new_message']['text'] in menu_dict[res_dict['menu_namber']]['buttons']:
                res_dict = menu_dict[res_dict['menu_namber']]['func'](arg_dict)
                for key in (set(res_dict) & {'candidates', 'candidate', 'photo_list'}):
                    arg_dict[key] = res_dict[key]
                arg_dict['vk'].answer(
                    arg_dict['new_message']['user_id'],
                    menu_dict[res_dict['menu_namber']]['message'],
                    menu_dict[res_dict['menu_namber']]['keyboard'],
                    res_dict['photo_list']
                )
            else:
                arg_dict['vk'].answer(arg_dict['new_message']['user_id'],
                                      'Сорян, такой коммнды я не знаю. :(\nЛучше выбери из предложенного.')
        elif arg_dict['new_message']['type'] == 'LIKE':
            like_flag, photo_list = arg_dict['vk'].photo_like(
                arg_dict['new_message']['user_id'],
                arg_dict['new_message']['owner_id'],
                arg_dict['new_message']['photo_like'])
            arg_dict['db_vkinder'].update_user_photo(arg_dict['new_message']['photo_like'], like_flag)
            arg_dict['vk'].edit_message(
                arg_dict['new_message']['user_id'],
                arg_dict['new_message']['text'],
                menu_dict[arg_dict['new_message']['keyboard_type']]['keyboard'],
                photo_list,
                arg_dict['new_message']['conversation_message_id']
            )




