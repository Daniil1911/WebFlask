
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
                             password_hash VARCHAR(128),
                             information VARCHAR(1280)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, login, password_hash, fname, name, information=""):#вставка записи
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (login, name,fname, password_hash,information) 
                          VALUES (?,?,?,?,?)''', (login, password_hash, fname, name,information))
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

    def update(self, user_id, name, fname, information):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET name ='"+str(name) + "', fname ='"+str(fname) + "', information ='"+str(information) + "' WHERE id = " + str(user_id))
        cursor.close()
        self.connection.commit()

    def get_info(self, user_id):
            cursor = self.connection.cursor()
            cursor.execute("SELECT a.name, a.fname, a.information FROM users a WHERE a.id = " + str(user_id))
            row = cursor.fetchone()
            return row


class UserImage:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self): #создание таблицы
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users_im 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_id INTEGER,
                             image VARCHAR(200)
                             
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_id, image):#вставка записи
        cursor = self.connection.cursor()
        fname, ffile = image  # сохранение картинки на сервер
        print(fname, ffile)
        f = open("static/img/" +str(user_id)+ fname.filename, "wb")
        f.write(ffile)
        f.close()
        cursor.execute('''INSERT INTO users_im 
                                   (user_id,image) 
                                   VALUES (?,?)''',
                       ( str(user_id), "img/" +str(user_id)+ fname.filename))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):# получение записи - возвращет список со значеняими из таблицы
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users_im WHERE user_id = " + str(user_id))
        row = cursor.fetchone()
        image =""
        if row is not None:
            image = row[2]
        return image






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

class Feed:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS feed 
                                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                   user_id INTEGER,
                                   follow_id INTEGER
                                   )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_id,follow_id):
        cursor = self.connection.cursor()

        cursor.execute('''INSERT INTO feed 
                            (user_id,follow_id) 
                            VALUES (?,?)''', (str(user_id),str(follow_id)))
        cursor.close()
        self.connection.commit()

    def get_users(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id in (select follow_id from feed where user_id =  "+ (str(user_id)+")"))
        rows = cursor.fetchall()
        return rows

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM posts WHERE user_id = (select follow_id from feed where user_id = " + (str(user_id)) + ") ORDER BY id DESC")
        rows = cursor.fetchall()
        return rows

    def delete(self, user_id,follow_id):# удаление записи из таблицы по условию ид=...
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM feed WHERE user_id = ''' + str(user_id)+'''follow_id = ''' + str(follow_id))
        cursor.close()
        self.connection.commit()

