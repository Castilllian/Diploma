import unittest
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from cryptography.fernet import Fernet


class TestCryptoScraper(unittest.TestCase):

    def test_website_availability(self):
        url = 'https://coinmarketcap.com/ru/'
        r = requests.get(url)
        self.assertEqual(r.status_code, 200, "Ошибка: Не удалось получить доступ к веб-сайту CoinMarketCap")
        
    def test_table_existence(self):
        url = 'https://coinmarketcap.com/ru/'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        crypto_table = soup.find('table')
        self.assertIsNotNone(crypto_table, "Ошибка: Таблица не найдена на странице")

    def test_csv_creation(self):
        url = 'https://coinmarketcap.com/ru/'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        crypto_table = soup.find('table')

        if crypto_table:
            headers = []
            for header in crypto_table.find_all('th'):
                headers.append(header.text.strip())

            crypto_data = []
            for row in crypto_table.find('tbody').find_all('tr'):
                columns = row.find_all('td')
                crypto_row_data = [col.text.strip() for col in columns]
                crypto_data.append(crypto_row_data)

            df = pd.DataFrame(crypto_data, columns=headers)
            df.to_csv('crypto_data.csv', index=False)

            self.assertTrue(os.path.isfile('crypto_data.csv'), "Ошибка: Файл 'crypto_data.csv' не был сохранен")
        else:
            self.fail("Таблица не найдена на странице, тест сохранения в CSV не может быть выполнен")

    def test_encryption(self):
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)

        original_text = "Test encryption"
        encrypted_text = cipher_suite.encrypt(original_text.encode())
        decrypted_text = cipher_suite.decrypt(encrypted_text).decode()

        self.assertNotEqual(original_text, encrypted_text, "Ошибка: Шифрование не произошло")
        self.assertEqual(original_text, decrypted_text, "Ошибка: Расшифровка не произошла")


if __name__ == '__main__':
    unittest.main()
