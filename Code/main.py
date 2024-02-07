import requests
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from cryptography.fernet import Fernet
import os  # добавляем модуль для работы с файлами и папками

# Настройка логирования
logging.basicConfig(filename='Diploma/Data/scraper_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Папка для хранения данных
data_folder = 'Diploma/Data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Генерируем ключ шифрования
key = Fernet.generate_key()
cipher_suite = Fernet(key)


def encrypt_text(text):
    return cipher_suite.encrypt(text.encode())


def decrypt_text(encrypted_text):
    return cipher_suite.decrypt(encrypted_text).decode()


async def fetch(url):
    response = requests.get(url)
    return response.text


async def update_crypto_data():
    url = 'https://coinmarketcap.com/ru/'
    html = await fetch(url)
    soup = BeautifulSoup(html, 'lxml')

    # Проверяем, что таблица существует
    crypto_table = soup.find('table')
    if crypto_table:
        headers = []
        # Получаем заголовки для таблицы
        for header in crypto_table.find_all('th'):
            headers.append(header.text.strip())

        crypto_data = []
        # Собираем данные о криптовалютах
        for row in crypto_table.find('tbody').find_all('tr'):
            columns = row.find_all('td')
            crypto_row_data = [col.text.strip() for col in columns]
            crypto_data.append(crypto_row_data)

        # Создаем DataFrame с данными
        df = pd.DataFrame(crypto_data, columns=headers)

        # Шифруем данные и сохраняем в файл
        encrypted_data = encrypt_text(df.to_csv(index=False))
        with open(os.path.join(data_folder, 'crypto_data.encrypted'), 'wb') as file:
            file.write(encrypted_data)

        logging.info('Зашифрованные данные о криптовалютах успешно сохранены')
        print('Зашифрованные данные о криптовалютах успешно сохранены')
    else:
        logging.error('Ошибка: Таблица не найдена на странице')
        print("Ошибка: Таблица не найдена на странице")


# Метод для расшифровки файла и сохранения его в формате CSV
def decrypt_and_save_csv(file_path, key):
    with open(file_path, 'rb') as file:
        encrypted_data = file.read()

    # Расшифровываем данные
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode()

    # Сохраняем расшифрованные данные в CSV
    with open(os.path.join(data_folder, 'decrypted_crypto_data.csv'), 'w') as csv_file:
        csv_file.write(decrypted_data)


# Обновляем данные и ведем журнал каждый час
while True:
    try:
        asyncio.run(update_crypto_data())
        # Вызываем метод для расшифровки файла и сохранения его в формате CSV
        decrypt_and_save_csv(os.path.join(data_folder, 'crypto_data.encrypted'), key)
    except Exception as e:
        logging.error(f'Произошла ошибка при обновлении данных: {str(e)}')
    time.sleep(3600)  # Пауза в 3600 секунд (1 час)
