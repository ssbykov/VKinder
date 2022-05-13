from vk_class import VKclass
from sql_class import VkinderDB
from bot_menu import menu_dict

if __name__ == '__main__':
    res_dict = {'menu_namber': '0', 'candidates': None, 'photo_list': []}
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
        arg_dict['user_id'] = arg_dict['new_message']['user_id']
        arg_dict['peer_id'] = arg_dict['new_message']['peer_id']
        arg_dict['cmids'] = arg_dict['new_message']['cmids']
        arg_dict['new_message'] = arg_dict['new_message']['text']
        buton_txt_list = [x['text'] for x in menu_dict[res_dict['menu_namber']]['keyboard']]
        if not menu_dict[res_dict['menu_namber']]['keyboard'] or arg_dict['new_message'] in buton_txt_list:
            res_dict = menu_dict[res_dict['menu_namber']]['func'](arg_dict)
            for key in (set(res_dict) & {'candidates', 'candidate', 'photo_list'}):
                arg_dict[key] = res_dict[key]
            arg_dict['vk'].answer(
                arg_dict['user_id'],
                menu_dict[res_dict['menu_namber']]['message'],
                menu_dict[res_dict['menu_namber']]['keyboard'],
                res_dict['photo_list']
            )
        else:
            # arg_dict['vk'].del_message({'peer_id': arg_dict['peer_id'], 'cmids': arg_dict['cmids']})
            arg_dict['vk'].answer(arg_dict['user_id'], 'Сорян, такой коммнды я не знаю. :(\nВыбери из предложенного.')




