import schedule
import time
import datetime
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from models import ReleaseInstance, add_to_supported, clean_table, get_grouplist
from models import get_today_data, message_chat, send_notification, get_time

def notifier():
    artists_list = get_grouplist()
    data = get_today_data(artists_list)

    for item in data:
        print(item)

    additional_second = 0
    while len(data) > 0:
        event_timedelta = data[0][1]
        event_timedelta += datetime.timedelta(seconds = additional_second)
        event_time = get_time(event_timedelta)
        print('Next event time:', event_time)

        def job(event_time=event_time):
            print('Event at {}'.format(event_time))
            send_notification(data[0])
            return schedule.CancelJob

        schedule.every().day.at(event_time).do(job).tag('kpop-release')

        while True:
            schedule.run_pending_tag('kpop-release')
            time.sleep(1)
            if len(schedule.jobs) == 2: # jobs with 'run' tag
                break

        data.pop(0)
        additional_second += 5

def update_db():
    session = HTMLSession()
    url = 'https://www.reddit.com/r/kpop/wiki/upcoming-releases/2020/november'
    response = session.get(url)

    soup = BeautifulSoup(response.text, features='lxml')
    table = soup.find_all('tr')

    # Every time table is cleaned and created as new
    clean_table()

    current_date = ''
    current_time = ''
    for row in table:
        # Casting to string type to use string methods
        row = str(row)
        row_elements = row.split('<td>')[1:7]
        
        if len(row_elements) > 1:
        
            # Clean release date
            try:
                date = row_elements[0]
                clean_date = [i for i in list(date) if i.isdigit()]

                if len(clean_date) == 0:
                    raise IndexError
                
                row_elements[0] = ''.join(clean_date)
                current_date = ''.join(clean_date)

            except IndexError:
                row_elements[0] = current_date

            # Insert release time if it is absent
            try:
                time = row_elements[1]
                if time == '?</td>\n':
                    time = None

                if time == None or time == '</td>\n':
                    raise IndexError

                row_elements[1] = time
                current_time = time

            except:
                row_elements[1] = current_time


            # Getting rid of HTML tags
            clean_fields = []
            for item in row_elements:
                item = item.replace('</td>\n', '')
                item = item.replace('<em>', '')
                item = item.replace('</em>', '')
                item = item.replace('\'', "\\\'") # SQL doesn't like special characters

                # Bizarre way to get rid of links, should probably use regex
                while 'href' in item:
                    point = item.find('nofollow')
                    item = item[point:]
                    point = item.find('>')
                    item = item[point+1:]
                    item = item.replace('</a>', '')

                clean_fields.append(item)

            try:
                date = clean_fields[0]
                time = clean_fields[1]
                artist = clean_fields[2]
                album = clean_fields[3]
                album_type = clean_fields[4]
                title_track = clean_fields[5]
            except:
                print('OST releases start here. Not supported')
                continue

            release = ReleaseInstance(date, time, artist, album, album_type, title_track)
            release.save_to_db()


if __name__ == '__main__':
    schedule.every().day.at('01:10:00').do(update_db).tag('run')
    schedule.every().day.at('01:15:00').do(notifier).tag('run')

    while True:
        schedule.run_pending_tag('run')
        time.sleep(1)