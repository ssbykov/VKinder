import vk_api
from vk import user_information

# личный токен профиля (не группы)
f = open('token-person.txt', 'r')
token = f.readline()

vk = vk_api.VkApi(token=token)
# Делаем поиск тут т.к токен группы не подходит для метода поиска и приходиться использовать личный токен
def user_search():
    info = user_information()

    data = vk.method("users.search", {f"q":" ","sort":"0","offset":"0","count":"100", "city":{info[2]}, "sex":{info[0]}, "status":"1", "age_from":{info[1]-3}, "age_to":{info[1]+3}})
    id = data['items'][0]['id']
    search_request = [f'https://vk.com/id{id}', data['items'][0]['first_name'], data['items'][0]['last_name']]
    return search_request
