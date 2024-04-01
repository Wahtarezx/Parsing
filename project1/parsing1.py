from bs4 import BeautifulSoup
import json
import requests
import csv

url = 'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
              'image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,'
                  ' like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0'
}

req = requests.get(url, headers=headers)
src = req.text

with open('index.html', 'w') as file:
    file.write(src)

with open('index.html', 'r') as file:
    src = file.read()

categories_dict = {}

soup = BeautifulSoup(src, 'lxml')
all_products_links = soup.find_all(class_='mzr-tc-group-item-href')
for item in all_products_links:
    item_text = item.text
    item_href = 'https://health-diet.ru' + item['href']
    print(f'{item_text}: {item_href}')

    categories_dict[item_text] = item_href

with open('categories_dict.json', 'w') as file:
    json.dump(categories_dict, file, indent=4, ensure_ascii=False)

with open('categories_dict.json', 'r') as file:
    data = json.load(file)

count_of_iterations = int(len(data)) - 1
count = 0
print(f'Всего итераций {count_of_iterations}')
for category_name, category_href in data.items():

    rep = [' ', ', ', ',', '-', "'"]
    for item in rep:
        if item in category_name:
            category_name = category_name.replace(item, '_')

    req = requests.get(url=category_href, headers=headers)
    src = req.text

    with open(f'data/{count}_{category_name}.html', 'w') as file:
        file.write(src)

    with open(f'data/{count}_{category_name}.html', 'r') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    alert_block = soup.find(class_='uk-alert-danger')
    if alert_block:
        continue

    table_headers = soup.find(class_='uk-table mzr-tc-group-table uk-table-hover'
                                     ' uk-table-striped uk-table-condensed').find('tr').find_all('th')
    product = table_headers[0].text
    calories = table_headers[1].text
    proteins = table_headers[2].text
    fats = table_headers[3].text
    carbohydrates = table_headers[4].text

    with open(f'data/{count}_{category_name}.csv', 'w', encoding='UTF-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                product,
                calories,
                proteins,
                fats,
                carbohydrates,
            )
        )

    products_data = soup.find(class_='uk-table mzr-tc-group-table uk-table-hover'
                                     ' uk-table-striped uk-table-condensed').find('tbody').find_all('tr')

    products_info = []

    for item in products_data:
        products_tds = item.find_all('td')

        title = products_tds[0].find('a').text
        calories = products_tds[1].text
        proteins = products_tds[2].text
        fats = products_tds[3].text
        carbohydrates = products_tds[4].text

        products_info.append({
            'Title': title,
            'Calories': calories,
            'Proteins': proteins,
            'Fats': fats,
            'Carbohydrates': carbohydrates,
        })

        with open(f'data/{count}_{category_name}.csv', 'a', encoding='UTF-8') as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    title,
                    calories,
                    proteins,
                    fats,
                    carbohydrates,
                )
            )

        with open(f'data/{count}_{category_name}.json', 'a', encoding='UTF-8') as file:
            json.dump(products_info, file, indent=4, ensure_ascii=False)

    count += 1

    print(f'#Итерация {count}, {category_name} записан')

    count_of_iterations -= 1

    if count_of_iterations == 0:
        print('Сбор данных завершен!')
        break

    print(f'Осталось {count_of_iterations} итераций')
