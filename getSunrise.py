from lxml import html
import requests
import ipdb
from datetime import datetime
import re

def getSunTimes(asTimeObj = False):
    url = 'https://www.sunrise-and-sunset.com/de/sun/deutschland/ulm'
    page = requests.get(url)
    tree = html.fromstring(page.content)

    aufg = tree.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody/tr[3]/td')[0].text.strip()
    unterg = tree.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody/tr[4]/td')[0].text.strip()

    # print(aufg.text.strip())
    # print(unterg.text.strip())

    date = tree.xpath('//*[@id="currentDate"]')[0].text.strip()


    if asTimeObj:
        aufg = datetime.strptime(aufg, '%H:%M').time()
        unterg = datetime.strptime(unterg, '%H:%M').time()
        date =  re.match('(\d{1,2})\. ([A-z]*) (\d{4})', date).groups()

        return {'date':date,'aufgang':aufg, 'untergang':unterg}

    else:
        return {'date':date, 'aufgang':aufg, 'untergang':unterg}


if __name__ == '__main__':
    times = getSunTimes()
    print(times)
    print(getSunTimes(asTimeObj=True))


    ipdb.set_trace()
