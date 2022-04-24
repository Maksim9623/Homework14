from flask import Flask, jsonify
import sqlite3


def main():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False

    def db_connection(query):
        # Функция для подключения к Б/Д
        with sqlite3.connect("netflix.db") as connection:
            cursor = connection.cursor()
            result = cursor.execute(query)
            res = result.fetchall()
            return res

    @app.route('/movie/<title>/')
    def data_from_movie(title):
        # Вьшка и функция по поиску в Б/Д по одному полю
        query = f"""
            SELECT `title`, `country`, `release_year`, listed_in AS genre, `description`
            FROM netflix
            WHERE `title` = '{title}' 
            ORDER BY release_year DESC 
            LIMIT 1
        """
        response = db_connection(query)[0]
        response_json = {
            "title": response[0],
            "country": response[1],
            "release_year": response[2],
            "genre": response[3],
            "description": response[4]
        }
        return jsonify(response_json)

    @app.route('/movie/<int:year>/to/<int:end>/')
    def year_from_movie(year, end):
        # Вьшка и функция по поиску в Б/Д по нескольким полям
        query = f"""
                SELECT `title`, `release_year`
                FROM netflix
                WHERE release_year BETWEEN {year} AND {end}
                LIMIT 100
            """
        response = db_connection(query)
        response_json = []
        for film in response:
            response_json.append({
                "title": film[0],
                "release_year": film[1],

            })
        return jsonify(response_json)

    @app.route('/rating/<group>/')
    def rating_from_movie(group):
        # Вьшка и функция по поиску в Б/Д с
        levels = {
            'children': ['G'],
            'family': ['G', 'PG', 'PG-13'],
            'adult': ['R', 'NC-17']
        }
        if group in levels:
            level = '\", \"'.join(levels[group])
            level = f'\"{level}\"'
        else:
            return jsonify([])

        query = f"""
                    SELECT `rating`, `rating`, `description`
                    FROM netflix
                    WHERE rating IN ({level})                    
                """
        response = db_connection(query)
        response_json = []
        for film in response:
            response_json.append({
                "title": film[0],
                "release_year": film[1],
                "description": film[2]
            })
        return jsonify(response_json)

    @app.route('/genre/<genre>/')
    def genre_from_movie(genre):
        # Вьшка и функция по поиску в Б/Д с
        query = f"""
                       SELECT `title`, `description`, listed_in 
                       FROM netflix
                       WHERE listed_in LIKE '%{genre}%'
                       ORDER BY release_year DESC 
                       LIMIT 10                
                   """
        response = db_connection(query)
        response_json = []
        for film in response:
            response_json.append({
                "title": film[0],
                "description": film[1].strip()  # strip() убирает последние значение
            })
        return jsonify(response_json)

    def name_actors(name1, name2):
        """ функция для проверки актеров, которые играю не больше 2-х раз """
        query = f"""
               SELECT `cast`
               FROM netflix
               WHERE `cast` LIKE '%{name1}%'
               AND `cast` LIKE '%{name2}%'                            
        """
        response = db_connection(query)
        actors = []
        for hero in response:
            actors.extend(hero[0].split(', '))  # добавлет в словарь актеров и разделяет запятой и пробелом
        actor = []
        for cast in actors:
            if cast not in [name1, name2]:
                if actors.count(cast) > 2:
                    actor.append(cast)

        actor = set(actor)  # убирает повтороение имен
        return actor

    # print(name_actors('Rose McIver', 'Ben Lamb'))
    """ проверка (шаг 5), использовать без #"""

    def type_picture(type_film, years, genre):
        """ функция для получения картин и ее описание """

        query = f"""
               SELECT `type`,`title`, `description`
               FROM netflix
               WHERE `type` = '{type_film}'  
               AND `release_year` = {years} 
               AND `listed_in` LIKE '%{genre}%'                   
        """
        response = db_connection(query)
        response_json = []
        for film in response:
            response_json.append({
                "type": film[0],
                "title": film[1],
                "description": film[2]
            })
        return response_json

    # print(type_picture('Movie', 2019, 'Documentaries'))
    """ проверка (шаг 6), получение картин с их описанием """

    app.run(debug=False)


if __name__ == '__main__':
    main()
