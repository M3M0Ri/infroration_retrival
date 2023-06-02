import requests
from bs4 import BeautifulSoup
import pandas

def extract():
    result = []
    main_url = 'https://www.asriran.com/fa/archive?service_id=-1&sec_id=-1&cat_id=-1&rpp=100&from_date=1401/01/01&to_date=1401/01/28&p='
    counter = 1
    while counter < 14:
        url = main_url + str(counter)
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')
        archive_section = soup.find('div', attrs={'class': 'news_archive_container'})
        articles = archive_section.findAll('article', attrs={'class': 'vizhe_cv col-xs-12 col-sm-6'})
        for article_section in articles:
            article = article_section.div
            content_section = article.find('div', attrs={'class': 'vizhe_lead'})
            date_section = article.find('span', attrs={'class': 'tarikh_archive'})

            title = article.h2.a.text
            relative_url = article.h2.a['href']
            article_url = 'https://www.asriran.com' + relative_url
            article_id = relative_url.split('/')[3]
            content = content_section.text
            date = date_section.text

            result.append({'title': title, 'date':date, 'content': content, 'article_url': article_url, 'article_id': article_id})
        print(len(result))
        print(f"page {counter} processed")
        counter += 1
    
    write_to_csv(result)


def write_to_csv(dict_list):
    title =[]
    date = []
    article_url = []
    article_id = []
    content = []

    for row in dict_list:
        title.append(row['title'])
        date.append(row['date'])
        content.append(row['content'])
        article_url.append(row['article_url'])
        article_id.append(row['article_id'])

    df = pandas.DataFrame({'title': title, 'date': date, 'article_url': article_url, 'article_id': article_id, 'content': content})
    df.to_csv('articles.csv', encoding='utf-8')


extract()
