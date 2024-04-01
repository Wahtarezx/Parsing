from bs4 import BeautifulSoup
import json
import requests
import csv


def get_data():
    url = 'https://www.labirint.ru/genres/2308/'
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0',
    }

    req = requests.get(url, headers=headers)

    with open('index.html', 'w') as file:
        file.write(req.text)

    with open('index.html', 'r') as file:
        scr = file.read()

    soup_for_page = BeautifulSoup(scr, 'lxml')
    pages_count = soup_for_page.find_all(class_='pagination-number')[-1]
    pages_count = int(pages_count.get_text())

    books_info = []

    with open('data/result/books.csv', 'w', encoding='UTF-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                "Название",
                "Цена",
                "Скидка",
                "Описание",
                "Ссылка",
                "Автор",
            )
        )

    for page in range(1, pages_count + 1):
        url = f'https://www.labirint.ru/genres/2308/?page={page}'

        req = requests.get(url, headers=headers)

        with open(f'data/books_page_{page}.html', 'w') as file:
            file.write(req.text)

        with open(f'data/books_page_{page}.html', 'r') as file:
            src = file.read()

        soup = BeautifulSoup(scr, 'lxml')
        all_books = soup.find_all('div', class_='genres-carousel__item')
        for book in all_books:
            try:
                title = book.find('div').get('data-name')
            except:
                title = 'Нет названия'
            try:
                price = book.find('div').get('data-price')
            except:
                price = 'Нет цены'
            try:
                price_with_discount = book.find('div').get('data-discount-price')
            except:
                price_with_discount = 'Нет цены со скидкой'
            try:
                description = book.find_all('a', class_='cover genres-cover')[0].get('title')
            except:
                description = 'Нет описания'
            try:
                link = 'https://www.labirint.ru' + book.find_all('a', class_='product-title-link')[0].get('href')
            except:
                link = 'Нет ссылки'
            try:
                author = book.find_all('div', class_='product-author')[0].find('a').get('title')
            except:
                author = 'Нет автора'
            try:
                discount = round((int(price) - int(price_with_discount)) / int(price) * 100)
            except:
                discount = 'Нет скидки'

            books_info.append({
                'title': title,
                'price': price,
                'discount': discount,
                'description': description,
                'link': link,
                'author': author
            })

            with open('data/result/books.csv', 'a', encoding='UTF-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    (
                        title,
                        price,
                        discount,
                        description,
                        link,
                        author,
                    )
                )

        print(f'[INFO] скопированно {page}/{pages_count} страниц')

    with open('data/result/books.json', 'a') as file:
        json.dump(books_info, file, indent=4, ensure_ascii=False)


def main():
    get_data()


if __name__ == '__main__':
    main()
