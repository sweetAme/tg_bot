import MySQLdb

# MySQL database config
HOST = ''
USER = ''
PASSWORD = ''
DB = ''

def db_connect(func):
    def inner(*args, **kwargs):
        db = MySQLdb.connect(
            host=HOST, 
            user=USER, 
            passwd=PASSWORD, 
            db=DB
        )
        cur = db.cursor()
        args += (cur, )
        result = func(*args, **kwargs)
        db.commit()
        cur.close()
        db.close()
        return result
    return inner