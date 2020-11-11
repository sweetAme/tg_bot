from bot import bot, chat_id
from config import db_connect
from datetime import date, datetime
import time

@db_connect
def add_to_supported(group_name, cur):
    # group_name is a list of strings like this ["Stray", "kids"]
    group_name = ' '.join(group_name)
    group_name = group_name.replace('\'', "\\\'")
    sql = "INSERT INTO supported_groups(artist) VALUES (\"{}\")".format(group_name)
    cur.execute(sql)

@db_connect
def remove_from_supported(group_name, cur):
    # group_name is a list of strings like this ["Stray", "kids"]
    group_name = ' '.join(group_name)
    group_name = group_name.replace('\'', "\\\'")
    sql = "DELETE FROM supported_groups WHERE artist = '{}'".format(group_name)
    query = cur.execute(sql)

    return query

@db_connect
def get_grouplist_bot(cur):
    sql = "SELECT artist FROM supported_groups"
    query = cur.execute(sql)
    
    if query == 0:
        return 'Список поддерживаемых групп пуст.'

    data = cur.fetchall()

    clean_data = ''
    for element in data:
        clean_data += (str(element[0]) + '\n')

    return clean_data
    
@db_connect
def get_grouplist(cur):
    sql = "SELECT artist FROM supported_groups"
    query = cur.execute(sql)
    data = cur.fetchall()

    if query == 0:
        return []

    clean_data = []
    for item in data:
        clean_data.append(item[0])

    return clean_data

def message_chat(msg):
    bot.send_message(chat_id, msg)
    print('Sent notification to chat {}. Message: {}'.format(chat_id, msg))

def get_time(timedelta):
    total_seconds = timedelta.seconds
    total_seconds -= 21600 # KST to MSC
    time_struct = time.gmtime(total_seconds)
    result = time.strftime("%H:%M:%S", time_struct)

    return result

def send_notification(release_info):
    artist = release_info[2]
    album = release_info[3]
    album_type = release_info[4]
    title_track = release_info[5]

    message = 'Только что вышел клип {} - {}\nАльбом: {} ({})'.format(artist, title_track, album, album_type)
    message_chat(message)

@db_connect
def get_today_data(artist_list, cur):
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    current_time = datetime.now()
    current_time = current_time.strftime("%H:%M:%S")

    artists = str(artist_list)[1:-1]
    sql = "SELECT * FROM kpop_november WHERE date = '{}' AND artist in ({})".format(today, artists)

    query = cur.execute(sql)
    print('query = ', query)

    data = cur.fetchall()
    data = list(data)

    return data

@db_connect
def clean_table(cur):
    sql = "DELETE FROM kpop_november;"
    cur.execute(sql)

class ReleaseInstance:
    
    def __init__(self, date, time, artist, album, album_type, title_track):
        self.date = date
        self.time = time
        self.artist = artist
        self.album = album
        self.album_type = album_type
        self.title_track = title_track

    @db_connect
    def save_to_db(self, cur):
        # If time == '?' we should change it
        if len(self.time) < 1:
            self.time = '00:00'

        try:
            sql = "INSERT INTO kpop_november(date, time, artist, album, album_type, title_track) VALUES ('{}', '{}', '{}', '{}', '{}', '{}');".format(
                '2020-11-{}'.format(self.date),
                self.time,
                self.artist,
                self.album,
                self.album_type,
                self.title_track
            )
            cur.execute(sql)

            print('++ Successfully added {} - {} to database'.format(self.artist, self.title_track))
        except:
            print('There was an error adding records to the DB')
            print( 'error data:',
                '2020-11-{}'.format(self.date),
                self.time,
                self.artist,
                self.album,
                self.album_type,
                self.title_track, '\n'
            )