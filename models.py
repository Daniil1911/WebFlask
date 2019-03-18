
class UserModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self): #создание таблицы
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             login VARCHAR(50),
                             name VARCHAR(50),
                             fname VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, login, password_hash, fname, name):#вставка записи
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (login, name,fname, password_hash) 
                          VALUES (?,?,?,?)''', (login, password_hash, fname, name))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):# получение записи - возвращет список со значеняими из таблицы
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = " + str(user_id))
        row = cursor.fetchone()
        return row

    def get_all(self):#возвращает список списков записей
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, login, password_hash):# проверка что запись существует
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE login = ? AND password_hash = ?", (login, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False, None)



class PostModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS posts 
                                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                   title VARCHAR(100),
                                   content VARCHAR(1000),
                                   user_id INTEGER,
                                   image VARCHAR(200),
                                   views VARCHAR(100)
                                   )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id,image, views):
        cursor = self.connection.cursor()
        fname,ffile = image #сохранение картинки на сервер
        print(fname,ffile)
        f = open("static/img/"+fname.filename,"wb")
        f.write(ffile)
        f.close()
        cursor.execute('''INSERT INTO posts 
                            (title, content, user_id,image,views) 
                            VALUES (?,?,?,?,?)''', (title, content, str(user_id),"img/"+fname.filename, views))
        cursor.close()
        self.connection.commit()

    def get(self, posts_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM posts WHERE id = "+ (str(posts_id)))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM posts WHERE user_id = " + (str(user_id)) + " ORDER BY id DESC")
        else:
            cursor.execute("SELECT * FROM posts")
        rows = cursor.fetchall()
        return rows

    def delete(self, posts_id):# удаление записи из таблицы по условию ид=...
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM posts WHERE id = ''' + str(posts_id))
        cursor.close()
        self.connection.commit()

    def add_view(self, posts_id):# изменение записи в таблице (в примере - меняет количество просмотров записи)
        data = self.get(posts_id)
        cursor = self.connection.cursor()
        cursor.execute(''' UPDATE posts SET views ='''+str(int(data[5])+1) + ''' WHERE id = ''' + str(posts_id))
        cursor.close()
        self.connection.commit()
