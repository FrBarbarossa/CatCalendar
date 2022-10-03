import sqlite3

conn = sqlite3.connect('usersdat.db', check_same_thread=False)
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(
   userid INTEGER,
   datetime TEXT,
   picture TEXT);""")
conn.commit()


def insert_data(user_id: int, time: str, pic: str) -> bool:
    users_data = list(cur.execute("SELECT datetime FROM users WHERE userid=(?)", (user_id,)))
    print(users_data)
    if (time,) in users_data:
        del_data(user_id, time)
    cur.execute("INSERT INTO users (userid, datetime,picture) VALUES(?,?,?);", (user_id, time, pic))
    conn.commit()
    return True


def get_month_data(user_id: int) -> list:
    users_data = list(cur.execute("SELECT datetime, picture FROM users where userid = (?)", (user_id,)))
    return users_data


def del_data(user_id: int, time: str) -> None:
    cur.execute("DELETE FROM users WHERE userid=(?) AND datetime=(?)", (user_id, time))
    print(f'УДАЛЯЮ ДУПЛИКАТ{time}')
    conn.commit()
