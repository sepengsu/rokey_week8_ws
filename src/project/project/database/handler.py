import sqlite3, os, cv2
from ament_index_python import get_package_share_directory

try:
    dir_path = get_package_share_directory('project')
    dir_path = os.path.join(dir_path, 'database')
    raise Exception
except:
    dir_path = os.path.dirname(os.path.abspath(__file__)) # src/project/project/database/handler.py
    dir_path = os.path.dirname(dir_path) # src/project/project/database
    if os.path.basename(dir_path) == 'project': # src/project/project
        dir_path = os.path.join(dir_path, 'database') # src/project/project/database
    else: # src/project
        dir_path = os.path.join(dir_path, 'project', 'database')
    

class DetectDBHandler:
    def __init__(self):
        self.db_path = os.path.join(dir_path, 'detect.db')
        self.img_dir = os.path.join(dir_path, 'images')
        self.img_id = 0
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detect(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT,
                box TEXT,
                class TEXT,
                max_color TEXT,
                size TEXT,
                img_id STRING
            )
        ''')
        self.conn.commit()

    def insert(self, cur_time, box, class_, max_color, size, img_id, frame):
        self.cursor.execute('''
            INSERT INTO detect(time, box, class, max_color, size, img_id)
            VALUES(?,?,?,?,?,?)
        ''',(cur_time, box, class_, max_color, size, img_id))

        self.conn.commit()
        self.img_id += 1
        name = f'{self.img_id}.jpg'
        x, y, w, h = box
        cropped_frame = frame[y:y+h, x:x+w]
        cv2.imwrite(os.path.join(self.img_dir, name), cropped_frame) # 이미지 저장

    def get(self):
        self.cursor.execute('''
            SELECT * FROM detect
        ''')
        return self.cursor.fetchall() # list of tuple

class LoginDBHandler:
    def __init__(self):
        self.db_path = os.path.join(dir_path, 'login.db')
        self.conn = sqlite3.connect(self.db_path) # db 연결
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS login(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT
            )
        ''')
        self.conn.commit()

    def insert(self, username, password):
        self.cursor.execute('''
            INSERT INTO login(username, password)
            VALUES(?,?)
        ''',(username, password))
        self.conn.commit()

    def get_users(self):
        self.cursor.execute('''
            SELECT username, password FROM login
        ''')
        users = {}
        for user in self.cursor.fetchall():
            users[user[0]] = user[1] # {username: password}
        return users
    
    def check(self, username, password):
        self.cursor.execute('''
            SELECT * FROM login
            WHERE username = ? AND password = ?
        ''',(username, password))
        return self.cursor.fetchall() # 일치한 정보가 있으면 1개, 없으면 0개
    
    def delete(self, username, password):
        self.cursor.execute('''
            DELETE FROM login
            WHERE username = ? AND password = ?
        ''',(username, password))
        self.conn.commit()

    def update(self, username, password, new_username, new_password):
        self.cursor.execute('''
            UPDATE login
            SET username = ?, password = ?
            WHERE username = ? AND password = ?
        ''',(new_username, new_password, username, password))
        self.conn.commit()

if __name__ == '__main__':
    login = LoginDBHandler()
    login.create_table()
    login.insert('jaenote', '1234')
    login.insert('jaewon', '1234')
    print(login.get())

    detect = DetectDBHandler()
    detect.create_table()
    