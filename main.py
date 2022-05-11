import sys
from vk_class import VKclass
from sql_class import VkinderDB
from bot_menu import menu_dict

if __name__ == '__main__':
    res_dict = {'menu_namber': '0', 'candidates': None}
    arg_dict = {'new_message': None}
    f = open('token_vk.txt', 'r')
    token = f.readline().strip()
    token_group = f.readline().strip()
    arg_dict['vk'] = VKclass(token, token_group)
    f = open('db_pass.txt', 'r')
    db_pass = f.readline().strip()
    arg_dict['db_vkinder'] = VkinderDB('postgres', db_pass, 'vkinder')
    arg_dict['db_vkinder'].create_database()
    arg_dict['db_vkinder'].create_database_tables()
    user_id = ''
    photo_list = []
    arg_dict['candidates'] = iter([])
    while arg_dict['new_message'] != 'q':
        arg_dict['new_message'] = arg_dict['vk'].new_message()
        arg_dict['user_id'] = arg_dict['new_message']['user_id']
        arg_dict['new_message'] = arg_dict['new_message']['text']
        res_dict = menu_dict[res_dict['menu_namber']]['func'](arg_dict)
        if 'candidates' in res_dict:
            arg_dict['candidates'] = res_dict['candidates']
        if 'candidate' in res_dict:
            arg_dict['candidate'] = res_dict['candidate']
        if 'photo_list' in res_dict:
            arg_dict['photo_list'] = res_dict['photo_list']
        arg_dict['vk'].answer(
            arg_dict['user_id'],
            menu_dict[res_dict['menu_namber']]['message'],
            menu_dict[res_dict['menu_namber']]['keyboard'],
            res_dict['photo_list']
        )



