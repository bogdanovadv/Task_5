import sqlite3
from newsapi import NewsApiClient
from flask import Flask, request, jsonify

app = Flask(__name__)

news_api_token = ""
host = '127.0.0.1'
port = 8080

def new_db():
    sql_req('''CREATE TABLE IF NOT EXISTS users
                            (id	INTEGER PRIMARY KEY AUTOINCREMENT, user INTEGER NOT NULL)
                   ''')
    sql_req('''CREATE TABLE IF NOT EXISTS categories
                            (id	INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, user_id INTEGER NOT NULL,
                            FOREIGN KEY(user_id) REFERENCES users(id))
                   ''')
    sql_req('''CREATE TABLE IF NOT EXISTS keywords
                            (id	INTEGER PRIMARY KEY AUTOINCREMENT, keyword TEXT NOT NULL, user_id INTEGER NOT NULL,
                            FOREIGN KEY(user_id) REFERENCES users(id))
                   ''')

def sql_req(query):
    try:
        connection = sqlite3.connect('bot.db')
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        result = True
    except sqlite3.Error:
        result = False
    finally:
        if connection:
            connection.close()
        return result

def sql_req_ans(query):
    set_q = []
    try:
        connection = sqlite3.connect('bot.db')
        cursor = connection.cursor()
        q = cursor.execute(query).fetchall()
        for x in q:
            set_q.insert(-1, x[0])
        connection.commit()
        connection.close()
    except sqlite3.Error:
        print("Ошибка")
    finally:
        if connection:
            connection.close()
        return set_q


@app.route('/users', methods=['POST'])
def users():
    if request.method == 'POST':
        new_db()
        id = request.form['id'];
        if sql_req(f'''INSERT INTO users (user) SELECT ('{id}') WHERE NOT EXISTS (SELECT 1 FROM users WHERE user = '{id}')'''):
            print(id)
            return jsonify({"status": "Ok"})
    return jsonify({"status": "No"})

@app.route('/subscriptions/categories', methods=['GET','POST','DELETE'])
def subscriptions_categories():
    if request.method == 'GET':
        id = request.args.get('id')
        categories = sql_req_ans(f'''SELECT category FROM categories JOIN users ON users.id = user_id WHERE users.user = {id}''')
        return jsonify(categories)
    if request.method == 'POST':
        id = request.form['id']
        category = request.form['category']
        if sql_req(f'''INSERT INTO categories (category, user_id) VALUES ("{category}", (SELECT id FROM users WHERE user = {id}))'''):
            return jsonify({"status": "Категория добавлена"})
    if request.method == 'DELETE':
        id = request.form['id']
        category = request.form['category']
        if sql_req(f'''DELETE FROM categories WHERE category = "{category}" and user_id = (SELECT id FROM users WHERE user = {id})'''):
            return jsonify({"status": "Категория удалена"})

@app.route('/subscriptions/keywords', methods=['GET','POST','DELETE'])
def subscriptions_keywords():
    if request.method == 'GET':
        id = request.args.get('id')
        keywords = sql_req_ans(f'''SELECT keyword FROM keywords JOIN users ON users.id = user_id WHERE users.user = {id}''')
        return jsonify(keywords)
    if request.method == 'POST':
        id = request.form['id']
        keyword = request.form['keyword']
        if sql_req(f'''INSERT INTO keywords (keyword, user_id) VALUES ("{keyword}", (SELECT id FROM users WHERE user = {id}))'''):
            return jsonify({"status": "Ключевое слово добавлено"})
    if request.method == 'DELETE':
        id = request.form['id']
        keyword = request.form['keyword']
        if sql_req(f'''DELETE FROM keywords WHERE keyword = "{keyword}" and user_id = (SELECT id FROM users WHERE user = {id})'''):
            return jsonify({"status": "Ключевое слово удалено"})

@app.route('/news', methods=['GET'])
def news():
    if request.method == 'GET':
        if request.args.get('keyword'):
            newsapi = NewsApiClient(api_key=news_api_token)
            all_articles = newsapi.get_everything(q=request.args.get('keyword'), sort_by='relevancy', page_size=10)
            return all_articles
        if request.args.get('category'):
            newsapi = NewsApiClient(api_key=news_api_token)
            top_headlines = newsapi.get_top_headlines(category=request.args.get('category'))
            return top_headlines

if __name__ == '__main__':
    app.run(host=host, port=port)
