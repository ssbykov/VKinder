from vk_class import VKclass
from DBVkinder import VkinderDB
from bot_menu import menu_dict#, set_like

if __name__ == '__main__':
    res_dict = {'menu_namber': '1', 'candidates': None, 'photo_list': []}
    arg_dict = {'new_message': None, 'candidates': iter([])}
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
            arg_dict['vk'].edit_message(
                arg_dict['new_message']['user_id'],
                arg_dict['new_message']['text'],
                menu_dict[arg_dict['new_message']['keyboard_type']]['keyboard'],
                arg_dict['new_message']['photo_list'],
                arg_dict['new_message']['conversation_message_id']
            )




