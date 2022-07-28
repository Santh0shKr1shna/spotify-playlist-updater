import requests
from bs4 import BeautifulSoup


class Scrapper(object):
    def __init__(self, *args, **kwargs):
        url = ""
        response = ""

    def scrapped_data (self):

        url = "https://www.billboard.com/charts/hot-100/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        track_name = []
        artist = []

        data = soup.findAll('div', attrs={'class': 'o-chart-results-list-row-container'})

        for store in data:
            tname = store.h3.text
            track_name.append(tname.strip())

            aname = store.find('span', class_='u-line-height-normal@mobile-max').text
            artist.append(aname.strip())

        file = open('billboards_hot100.txt', 'w')

        res = []
        for i in range(100):
            l_file = [str(i + 1), ' || ' + track_name[i], ' || ' + artist[i] + '\n']
            l = [str(i + 1), track_name[i], artist[i]]
            res.append(l)
            file.writelines(l_file)

        file.close()

        return res


#obj = scrapper()
#print(obj.scrapped_data())
