import requests
import json
from tqdm import tqdm

def get_vk_photos(user_id, vk_token):
    url = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': user_id,
        'access_token': vk_token,
        'photo_sizes': 1,
        'count': 1000,
        'v': '5.131'
    }
    response = requests.get(url, params=params)
    data = response.json()

    if 'error' in data:
        print(f"Ошибка API ВКонтакте: {data['error']['error_msg']}")
        return []

    return data['response']['items']

def upload_to_yadisk(photo_url, file_name, ya_token):
    headers = {
        'Authorization': f'OAuth {ya_token}'
    }
    upload_url = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload',
                              headers=headers,
                              params={'path': f'photos/{file_name}', 'overwrite': True}).json().get('href')

    if not upload_url:
        print("Не удалось получить URL для загрузки на Яндекс.Диск.")
        return

    photo_response = requests.get(photo_url)
    requests.put(upload_url, data=photo_response.content)

def main():
    user_id = input("Введите ID пользователя ВК: ")
    vk_token = input("Введите токен ВК: ").split('=')[1]
    ya_token = input("Введите токен Яндекс.Диска: ").split('=')[1]

    photos = get_vk_photos(user_id, vk_token)

    if not photos:
        print("Нет доступных фотографий для загрузки.")
        return

    likes_dict = {}

    for photo in photos:
        likes_count = photo['likes']['count']
        creation_date = photo['date']

        if likes_count not in likes_dict:
            likes_dict[likes_count] = []

        likes_dict[likes_count].append((photo, creation_date))

    sorted_photos = []

    for likes_count in sorted(likes_dict.keys(), reverse=True):
        # Сортируем по дате создания внутри одного количества лайков
        sorted_photos.extend(sorted(likes_dict[likes_count], key=lambda x: x[1], reverse=True))

    json_data = []

    for photo_info in tqdm(sorted_photos):
        photo, _ = photo_info
        # Получаем максимальный размер для каждой фотографии
        max_size_photo = max(photo['sizes'], key=lambda s: s['width'] * s['height'])
        file_name = f"{photo['likes']['count']}.jpg"

        upload_to_yadisk(max_size_photo['url'], file_name, ya_token)

        json_data.append({
            "file_name": file_name,
            "size": f"{max_size_photo['width']}x{max_size_photo['height']}"
        })

    with open('photos.json', 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

if __name__ == '__main__':
    main()