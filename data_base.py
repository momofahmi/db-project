import mysql.connector as dbapi # mysql
from flask import Flask, render_template, request
from dotenv import load_dotenv
import string
import random
load_dotenv()
import os
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

def game_get_comp():
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")

    cursor = connection.cursor()

    statement = """select competition_id, competitions_name
                    from competitions
                    order by competitions_name"""

    cursor.execute(statement)
    game_competitions = cursor.fetchall()
    result = [list(comp) for comp in game_competitions]

    for i in range(len(result)):
        result[i][1] = result[i][1].replace('-', ' ')
        result[i][1] = result[i][1].title()

    cursor.close()
    connection.close()

    return result

def game_get_season():
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")

    cursor = connection.cursor()

    statement = """SELECT distinct(season)
                    FROM futbalmania.games
                    order by season DESC;"""

    cursor.execute(statement)
    seasons = cursor.fetchall()

    cursor.close()
    connection.close()

    return seasons

def game_get_round():
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")

    cursor = connection.cursor()

    statement = """SELECT distinct(games_round)
                    FROM futbalmania.games
                    ORDER BY games_round;"""

    cursor.execute(statement)
    rounds = cursor.fetchall()
    return rounds

###################### FOR PLAYER ############################################################################################################################
def player_t():
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")

    cursor = connection.cursor()

    statement = """
    SELECT p.players_name, c.clubs_name ,p.position ,p.country_of_citizenship,p.player_id
    FROM players p
    INNER JOIN clubs c ON p.current_club_id = c.club_id
    ORDER BY p.players_name;
     """

    cursor.execute(statement)
    result_2 = cursor.fetchall()

    cursor.close()
    connection.close()

    return result_2

def get_available_countries():
        connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()
        statement = """SELECT DISTINCT country_of_citizenship FROM players WHERE country_of_citizenship IS NOT NULL AND country_of_citizenship != '' ORDER BY country_of_citizenship;"""
        cursor.execute(statement)
        countries = [country[0] for country in cursor.fetchall()]
        cursor.close()
        connection.close()
        return countries

def get_available_positions():
        connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()
        statement = "SELECT DISTINCT position FROM players WHERE position IS NOT NULL AND position != '' ORDER BY position;"
        cursor.execute(statement)
        positions = [position[0] for position in cursor.fetchall()]
        cursor.close()
        connection.close()
        return positions

def get_available_clubs():
        connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()
        statement = "SELECT DISTINCT c.clubs_name FROM players p JOIN clubs c ON p.current_club_id = c.club_id WHERE c.clubs_name IS NOT NULL AND c.clubs_name != '' ORDER BY c.clubs_name;"
        cursor.execute(statement)
        clubs = [club[0] for club in cursor.fetchall()]
        cursor.close()
        connection.close()
        return clubs

def get_player_details(player_id):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    statement = """
        SELECT first_name, last_name, players_name, last_season, country_of_birth, city_of_birth, 
               country_of_citizenship, date_of_birth, sub_position, position, foot, height_in_cm, 
               market_value_in_eur, highest_market_value_in_eur, contract_expiration_date, 
               agent_name, image_url, competitions_name , current_club_name,player_id ,current_club_id, 
               player_code,current_club_domestic_competition_id
        FROM players
        INNER JOIN competitions ON players.current_club_domestic_competition_id = competitions.competition_id
        WHERE player_id = %s;
    """

    cursor.execute(statement, (player_id,))
    player_data = cursor.fetchone()


    if player_data:
        player_data = list(player_data)

        if isinstance(player_data[17], str):
            player_data[17] = player_data[17].replace('-', ' ')

        player_info = {
            "first_name": player_data[0],
            "last_name": player_data[1],
            "players_name": player_data[2],
            "last_season": player_data[3],
            "country_of_birth": player_data[4],
            "city_of_birth": player_data[5],
            "country_of_citizenship": player_data[6],
            "date_of_birth": player_data[7],
            "sub_position": player_data[8],
            "position": player_data[9],
            "foot": player_data[10],
            "height_in_cm": player_data[11],
            "market_value_in_eur": player_data[12],
            "highest_market_value_in_eur": player_data[13],
            "contract_expiration_date": player_data[14],
            "agent_name": player_data[15],
            "image_url": player_data[16],
            "competitions_name": player_data[17],
            "current_club_name": player_data[18],
            "player_id": player_data[19],
            "current_club_id": player_data[20],
            "player_code": player_data[21],
            "current_club_domestic_competition_id": player_data[22]
        }
    else:
        player_info = None

    cursor.close()
    connection.close()
    return player_info

def update_player_details(player_id, **updated_data):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    update_parts = [f"{key} = %s" for key in updated_data]
    update_statement = f"UPDATE players SET {', '.join(update_parts)} WHERE player_id = %s;"

    update_values = tuple(updated_data.values()) + (player_id,)

    cursor.execute(update_statement  , update_values)
    connection.commit()
    cursor.close()
    connection.close()

def insert_new_player(new_player_data):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    cursor.execute("SELECT MAX(player_id) FROM players;")
    max_id_result = cursor.fetchone()
    max_id = max_id_result[0] if max_id_result[0] is not None else 0
    next_id = max_id + 1
    new_player_data['player_id'] = next_id

    current_club_name = new_player_data.get('current_club_name')
    cursor.execute("SELECT club_id, domestic_competition_id FROM clubs WHERE clubs_name = %s", (current_club_name,))
    club_info = cursor.fetchone()

    if club_info:
        new_player_data['current_club_id'], new_player_data['current_club_domestic_competition_id'] = club_info

    columns = ', '.join(new_player_data.keys())
    placeholders = ', '.join(['%s'] * len(new_player_data))
    insert_statement = f"INSERT INTO players ({columns}) VALUES ({placeholders});"

    insert_values = tuple(new_player_data.values())

    
    cursor.execute(insert_statement, insert_values)
    connection.commit()
    
    cursor.close()
    connection.close()


def delete_player(player_id):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    statement = """DELETE FROM players WHERE player_id = %s;"""

    cursor.execute(statement, (player_id,))
    connection.commit()
    
    cursor.close()
    connection.close()

    return True

################################### FOR APPEARANCE ############################################################################################################
def get_appearances_data():
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")

    cursor = connection.cursor()

    statement = """
    SELECT a.appearances_date, a.player_name, 
    c.clubs_name,a.appearance_id
    FROM appearances a
    JOIN clubs c ON a.player_club_id = c.club_id
    ORDER BY a.appearances_date DESC;
     """

    cursor.execute(statement)
    result_5 = cursor.fetchall()

    cursor.close()
    connection.close()

    return result_5

def get_available_competitions():
        connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()
        statement = """
        SELECT DISTINCT REPLACE(competitions_name, '-', ' ') AS competition_name
        FROM competitions
        WHERE competitions_name IS NOT NULL AND competitions_name != ''
        ORDER BY REPLACE(competitions_name, '-', ' ');
        """

        cursor.execute(statement)
        countries = [country[0] for country in cursor.fetchall()]
        cursor.close()
        connection.close()
        return countries

def get_appearance_details(appearance_id):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    statement = """
        SELECT 
        a.appearance_id, 
        a.game_id, 
        a.player_id, 
        wc.clubs_name AS player_club_name, 
        a.appearances_date, 
        a.player_name, 
        c.competitions_name, 
        a.yellow_cards, 
        a.red_cards, 
        a.goals, 
        a.assists, 
        a.minutes_played,
        wcc.clubs_name AS player_current_club_name
        FROM appearances a
        JOIN clubs wc ON a.player_club_id = wc.club_id
        JOIN clubs wcc ON a.player_current_club_id = wcc.club_id
        INNER JOIN competitions c ON a.competition_id = c.competition_id
        WHERE a.appearance_id = %s;
        """

    cursor.execute(statement, (appearance_id,))
    appearance_data = cursor.fetchone()


    if appearance_data:
        appearance_data = list(appearance_data)

        if isinstance(appearance_data[6], str):
            appearance_data[6] = appearance_data[6].replace('-', ' ')

        appearance_info = {
            "appearance_id": appearance_data[0],
            "game_id": appearance_data[1],
            "player_id": appearance_data[2],
            "clubs_name": appearance_data[3],
            "appearances_date": appearance_data[4],
            "player_name": appearance_data[5],
            "competitions_name": appearance_data[6],
            "yellow_cards": appearance_data[7],
            "red_cards": appearance_data[8],
            "goals": appearance_data[9],
            "assists": appearance_data[10],
            "minutes_played": appearance_data[11],
            "player_current_club_name": appearance_data[12]
        }
    else:
        appearance_info = None

    cursor.close()
    connection.close()
    return appearance_info

def update_appearance_details(appearance_id, **updated_data):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    update_parts = [f"{key} = %s" for key in updated_data]
    update_statement = f"UPDATE appearances SET {', '.join(update_parts)} WHERE appearance_id = %s;"

    update_values = tuple(updated_data.values()) + (appearance_id,)

    cursor.execute(update_statement, update_values)
    connection.commit()
    cursor.close()
    connection.close()

def insert_new_appearance(new_appearance_data):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    player_id = new_appearance_data.get('player_id')
    if player_id:
        cursor.execute("SELECT current_club_id, players_name FROM players WHERE player_id = %s", (player_id,))
        player_info = cursor.fetchone()
        if player_info:
            new_appearance_data['player_current_club_id'], new_appearance_data['player_name'] = player_info

    columns = ', '.join(new_appearance_data.keys())
    placeholders = ', '.join(['%s'] * len(new_appearance_data))
    insert_statement = f"INSERT INTO appearances ({columns}) VALUES ({placeholders});"

    insert_values = tuple(new_appearance_data.values())

    cursor.execute(insert_statement, insert_values)
    connection.commit()
    
    cursor.close()
    connection.close()

def delete_appearance(appearance_id):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    statement = """DELETE FROM appearances WHERE appearance_id = %s;"""

    cursor.execute(statement, (appearance_id,))
    connection.commit()
    
    cursor.close()
    connection.close()

    return True




######################### FOR QUESTION IN MCQ #################################################################################
def question_game():
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
    
    cursor = connection.cursor(dictionary=True)

    statement = """SELECT players_name,country_of_citizenship 
    FROM players 
    WHERE highest_market_value_in_eur >= 50000000 
    AND last_season > 2017 
    AND players_name IS NOT NULL 
    AND country_of_citizenship IS NOT NULL 
    ORDER BY RAND() 
    LIMIT 1;"""
   
    cursor.execute(statement)
    result_3 = cursor.fetchall()
    cursor.close()
    connection.close()

    return result_3



def random_value():
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
    
    cursor = connection.cursor(dictionary=True)

    statement = """ SELECT country_of_citizenship 
    FROM players 
    WHERE highest_market_value_in_eur >= 50000000 
    AND last_season > 2015 
    AND country_of_citizenship IS NOT NULL
    AND country_of_citizenship != '' 
    ORDER BY RAND() 
    LIMIT 1;"""
   
    cursor.execute(statement)
    random_value = cursor.fetchall()

    cursor.close()
    connection.close()

    return random_value

#######################################################################################################################################
 
     
def club_list():
    #xto get the clublist
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")

    cursor = connection.cursor()

    statement =  '''
                    SELECT distinct(clubs_name), country_name, club_id, domestic_competition_id
                    FROM clubs
                    JOIN competitions
                    ON clubs.domestic_competition_id = competitions.domestic_league_code; 
                '''

    cursor.execute(statement)
    clubslist = cursor.fetchall()

    cursor.close()
    connection.close()

    return clubslist


def clubgame_list(club_id):
    #xto get the clublist
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")

    cursor = connection.cursor()

    statement =  '''
                    SELECT 
                        c1.clubs_name as club_name,
                        c2.clubs_name AS opponent_name,
                        cg.own_goals as goal_for,
                        cg.opponent_goals AS goal_against,
                        cg.own_manager_name,
                        cg.opponent_manager_name,
                        
                        CASE 
                            WHEN cg.hosting = 'Home' THEN c1.stadium_name
                            ELSE c2.stadium_name
                        END AS stadium_name
                    FROM 
                        futbalmania.club_games AS cg
                        JOIN clubs c1 ON cg.club_id = c1.club_id  
                        JOIN clubs c2 ON cg.opponent_id = c2.club_id
                    WHERE c1.club_id = %s; 
                '''
    cursor.execute(statement, (club_id, ))
    clubslist = cursor.fetchall()

    cursor.close()
    connection.close()

    return clubslist
def game_get_clubs():
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")

    cursor = connection.cursor()

    statement = """SELECT distinct(A.club_id), (A.clubs_name) FROM futbalmania.clubs A
                    WHERE A.club_id in (SELECT B.home_club_id FROM futbalmania.games B)
	                OR A.club_id in (SELECT C.away_club_id FROM futbalmania.games C)
                    order by A.clubs_name;"""

    cursor.execute(statement)
    seasons = cursor.fetchall()     

    cursor.close()
    connection.close()

    return seasons

def game_get_games(game_competitions_list, game_season_list, game_rounds_list, game_clubs_list, page_num):
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")

    cursor = connection.cursor()

    statement = """SELECT A.game_id, B.competitions_name, A.games_round, A.home_club_name, A.home_club_goals, A.away_club_goals, A.away_club_name, A.games_date
                    FROM futbalmania.games A
                    JOIN futbalmania.competitions B on A.competition_id = B.competition_id
                    %s
                    order by games_date DESC
                    LIMIT 20 OFFSET %s;"""

    where_statement = "WHERE TRUE" #By default is true, so we can concatenate "AND (<condition>)" for all category without check
    comp_sel = ""
    game_season_sel = ""
    game_rounds_sel = ""
    game_clubs_sel = ""

    if len(game_competitions_list) == 0: #DONE
        comp_sel = "TRUE"
    else:
        comp_sel = "FALSE" # 0 OR <variable> = <variable>; we can use this
        for x in game_competitions_list:
            comp_sel = comp_sel + " OR A.competition_id = '%s' " %str(x)
    where_statement = where_statement + " AND ( " + comp_sel + ")"

    if len(game_season_list) == 0: #DONE
        game_season_sel = "TRUE"
    else:
        game_season_sel = "FALSE" # 0 OR <variable> = <variable>; we can use this
        for x in game_season_list:
            game_season_sel = game_season_sel + " OR A.season = %s " %str(x)
    where_statement = where_statement + " AND ( " + game_season_sel + ")"

    if len(game_rounds_list) == 0: #DONE
        game_rounds_sel = "TRUE"
    else:
        game_rounds_sel = "FALSE" # 0 OR <variable> = <variable>; we can use this
        for x in game_rounds_list:
            game_rounds_sel = game_rounds_sel + " OR A.games_round = '%s' " %str(x)
    where_statement = where_statement + " AND ( " + game_rounds_sel + ")"

    if len(game_clubs_list) == 0: #DONE
        game_clubs_sel = "TRUE"
    else:
        game_clubs_sel = "FALSE" # 0 OR <variable> = <variable>; we can use this
        for x in game_clubs_list:
            game_clubs_sel = game_clubs_sel + " OR A.home_club_id = %s OR A.away_club_id = %s " %(str(x), str(x))
    where_statement = where_statement + " AND ( " + game_clubs_sel + ")"

    print(where_statement)

    cursor.execute(statement %(where_statement, str( (page_num - 1)*20 ) ) )
    games = cursor.fetchall()
    result = [list(comp) for comp in games]

    for i in range(len(result)):
        result[i][1] = result[i][1].replace('-', ' ')
        result[i][1] = result[i][1].title()
    
    return result

def games_delete_game(game_id):

    try:
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()

        statement = """DELETE FROM games WHERE game_id = %s;"""

        cursor.execute(statement %str(game_id))
        connection.commit()
    except dbapi.DatabaseError:
        connection.rollback()
        print("Database error")
    finally:
        cursor.close()
        connection.close()

    return True

def games_add_game(game_datas):

    try:
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()

        check_club_statement = """SELECT club_id FROM clubs where clubs_name = '%s';"""

        cursor.execute(check_club_statement %(game_datas["home_club_name"]) )
        home_name = cursor.fetchone()
        home_id = home_name[0]

        cursor.execute(check_club_statement %(game_datas["away_club_name"]) )
        away_name = cursor.fetchone()
        away_id = away_name[0]

        if not home_id or not away_id:
            raise ValueError('Non-Existing Club(s)')
        
        max_game_id_statement = """Select game_id from games order by game_id DESC limit 1;"""

        cursor.execute(max_game_id_statement)
        max_name = cursor.fetchone()
        new_id = max_name[0] + 1
        
        insertion_statement = """INSERT INTO games(game_id, competition_id, season, games_round, games_date, home_club_id, away_club_id, home_club_goals, away_club_goals, home_club_position, away_club_position, home_club_manager_name, away_club_manager_name, stadium, attendance, referee, url, home_club_formation, away_club_formation, home_club_name, away_club_name, games_aggregate, competition_type)
                                 VALUES(%s, '%s', %s, '%s', '%s', %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"""

        cursor.execute(insertion_statement %(new_id, game_datas["competition_id"], game_datas["season"],  game_datas["game_round"],
                                             game_datas["date"], home_id, away_id, game_datas["home_club_goals"],
                                             game_datas["away_club_goals"], game_datas["home_club_position"],
                                             game_datas["away_club_position"], game_datas["home_club_manager"],
                                             game_datas["away_club_manager"], game_datas["stadium"], game_datas["attendance"],
                                             game_datas["referee"], "", game_datas["home_club_formation"],
                                             game_datas["away_club_formation"], game_datas["home_club_name"],
                                             game_datas["away_club_name"], "", game_datas["competition_type"]))
        
        connection.commit()

    except dbapi.DatabaseError:
        connection.rollback()
        print("Database error - Add Games")
    except ValueError:
        connection.rollback()
        print('Non-Existing Club(s)')
    finally:
        cursor.close()
        connection.close()

    return True

def game_update_get_all(game_id):

    try:
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor(dictionary=True)

        statement = """SELECT * FROM games where game_id = %s"""

        cursor.execute(statement %game_id)

        results = cursor.fetchone()
        return results
    except dbapi.DatabaseError:
        print("Database Error - game_update_get_all")
    finally:
        cursor.close()
        connection.close()

def game_update_game(updated_game, game_id):

    try:
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()

        check_club_statement = """SELECT club_id FROM clubs where clubs_name = '%s';"""

        cursor.execute(check_club_statement %(updated_game["home_club_name"]) )
        home_name = cursor.fetchone()

        cursor.execute(check_club_statement %(updated_game["away_club_name"]) )
        away_name = cursor.fetchone()

        if home_name and away_name:
            away_id = away_name[0]
            home_id = home_name[0]
        else:
            print(home_name)
            print(away_name)
            raise TypeError('No input?')

        check_comp_statement = """SELECT competitions_name FROM competitions where competition_id = '%s';"""
        cursor.execute(check_comp_statement %(updated_game["competition_id"]) )
        temp = cursor.fetchone()
        comp_name = temp[0]

        updated_game["home_club_id"] = home_id
        updated_game["away_club_id"] = away_id
        updated_game["home_club_name"] = "'" + updated_game["home_club_name"] + "'"
        updated_game["away_club_name"] = "'" + updated_game["away_club_name"] + "'"
        updated_game["competition_id"] = "'" + updated_game["competition_id"] + "'"

        update_parts = [f"{key} = %s" for key in updated_game]
        update_statement = f"UPDATE games SET {', '.join(update_parts)} WHERE game_id = %s;"

        for i in updated_game:
            if( updated_game[i] == 'None'):
                updated_game[i] = 'NULL'

        update_values = tuple(updated_game.values()) + (game_id,)

        print(update_statement %update_values)
        cursor.execute(update_statement %update_values)
        connection.commit()

        pass
    except dbapi.DatabaseError:
        connection.rollback()
        print("Database Error - Update Game")
    except TypeError:
        connection.rollback()
        print("Type Error")
    finally:
        cursor.close()
        connection.close()
    
def games_details_get_game(game_id):

    results = []

    try:
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()

        statement = """SELECT home.clubs_name, away.clubs_name, A.home_club_goals, A.away_club_goals, A.home_club_position, A.away_club_position,
                        A.home_club_manager_name, A.away_club_manager_name, B.competitions_name, A.season, A.games_round, A.games_date, A.stadium,
                        A.attendance, A.referee, A.home_club_formation, A.away_club_formation, A.game_id
                        FROM games A
                        LEFT JOIN competitions B ON A.competition_id = B.competition_id
                        LEFT JOIN clubs home ON A.home_club_id = home.club_id
                        LEFT JOIN clubs away ON A.away_club_id = away.club_id
                        WHERE a.game_id = %d;"""

        cursor.execute(statement %game_id)

        results = cursor.fetchall()[0]
        results = [comp for comp in results]
        results[8] = results[8].replace('-', ' ')
        results[8] = results[8].title()

        pass
    except dbapi.DatabaseError:
        print("Database error - Select Game details")
    finally:
        cursor.close()
        connection.close()

    return results

def games_details_get_event( game_id ):
    
    results = []

    try:
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()

        statement = """SELECT A.game_event_id, A.game_id, A.minute, A.game_events_type,
                        B.clubs_name, C.players_name, in_player.players_name,
                        asist_player.players_name, A.description
                        FROM game_events A
                        LEFT JOIN clubs B ON B.club_id = A.club_id
                        LEFT JOIN players C ON C.player_id = A.player_id
                        LEFT JOIN players in_player ON in_player.player_id = A.player_in_id
                        LEFT JOIN players asist_player ON asist_player.player_id = A.player_assist_id
                        where A.game_id = %d
                        order by A.minute;"""

        cursor.execute(statement %game_id)

        results = cursor.fetchall()
        results = [list(comp) for comp in results]

        for i in range(len(results)):
            if results[i][8][0] == ',':
                results[i][8] = str(results[i][8]).replace(',', ' ', 1)

        #print(results)
        pass
    except dbapi.DatabaseError:
        print("Database error - Select Game Events")
    finally:
        cursor.close()
        connection.close()
        return results
    
def games_events_delete_event(game_event_id):

    try:
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()

        statement = """DELETE FROM game_events WHERE game_event_id = '%s';"""

        cursor.execute(statement %str(game_event_id))
        connection.commit()
    except dbapi.DatabaseError:
        connection.rollback()
        print("Database error")
    finally:
        cursor.close()
        connection.close()

    return True

def games_details_add_game_events(game_datas):

    try:
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()

        check_club_statement = """SELECT club_id FROM clubs where clubs_name = '%s';"""

        cursor.execute(check_club_statement %(game_datas["club"]) )
        club_x = cursor.fetchone()
        club_id = club_x[0]

        check_player_statement = """SELECT player_id FROM players where players_name = '%s';"""

        cursor.execute(check_player_statement %(game_datas["player"]) )
        player_x = cursor.fetchone()
        player_id = player_x[0]

        check_other_player_statement = """SELECT player_id FROM players where players_name = '%s';"""

        cursor.execute(check_other_player_statement %(game_datas["in_player"]) )
        other_x = cursor.fetchone()
        if other_x and game_datas["event"] == 'Substitutions':
            other_player_id = other_x[0]
        else:
            other_player_id = 'NULL'

        if not player_id:
            raise ValueError('Non-Existing Club(s)')
        
        #Generate new game_event_id - original database uses some hash code for key
        while(True):

            res = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

            key_unique_statement = """SELECT count(*) FROM game_events where game_event_id = '%s';"""

            cursor.execute(key_unique_statement %(res) )
            temp = cursor.fetchone()
            key_i = temp[0]

            if(key_i == 1):
                continue
            else:
                break

        insertion_statement = """INSERT INTO game_events(game_event_id, game_events_date, game_id, minute, game_events_type,
                                club_id, player_id, description, player_in_id, player_assist_id)
                                VALUES ('%s', %s, %s, %s, '%s', %s, %s, '%s', %s, %s);"""

        cursor.execute(insertion_statement %(res, 'NULL', game_datas['game_id'], game_datas['minute'], game_datas['event'],
                                             club_id, player_id, game_datas['details'], other_player_id, 'NULL') )
        

        connection.commit()

        pass
    except dbapi.DatabaseError:
        connection.rollback()
        print("Database error - Add Game Event")
    except ValueError:
        connection.rollback()
        print("Value error - Non-existing Player")
    finally:
        cursor.close()
        connection.close()

    #if not home_id or not away_id:
    #raise ValueError('Non-Existing Club(s)')
        
def game_update_game_event(updated_game, player_names, game_id):

    try:
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()

        check_club_statement = """SELECT club_id FROM clubs where clubs_name = %s;"""
        print(player_names)

        cursor.execute(check_club_statement %player_names["club"])
        club_x = cursor.fetchone()
        club_id = club_x[0]


        check_club_statement = """SELECT player_id FROM players where players_name = %s;"""

        cursor.execute(check_club_statement %player_names["player_name"] )
        home_name = cursor.fetchone()

        if player_names["player_in_name"]:
            cursor.execute(check_club_statement %player_names["player_in_name"] )
            away_name = cursor.fetchone()
        if away_name:
            player_in_id = away_name[0]
        else:
            player_in_id = 'NULL'

        if home_name:
            players_id = home_name[0]
        else:
            raise TypeError('No input?')

        updated_game["player_id"] = players_id
        updated_game["player_in_id"] = player_in_id
        updated_game["club_id"] = club_id

        update_parts = [f"{key} = %s" for key in updated_game]
        update_statement = f"UPDATE game_events SET {', '.join(update_parts)} WHERE game_event_id = %s;"

        update_values = tuple(updated_game.values()) + ( "'" + game_id + "'",)

        print(update_statement %update_values)

        cursor.execute(update_statement %update_values)
        connection.commit()
        print("success")

        pass
    except dbapi.DatabaseError:
        connection.rollback()
        print("Database Error - Update Game")
    except TypeError:
        connection.rollback()
        print("Type Error")
    finally:
        cursor.close()
        connection.close()

def event_update_get_all(event_id):
    try:
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor(dictionary=True)

        statement = """SELECT A.*, B.clubs_name, C.players_name as player_name, D.players_name as player_in_name
                        FROM game_events A
                        LEFT JOIN clubs B ON A.club_id = B.club_id
                        LEFT JOIN players C ON A.player_id = C.player_id
                        LEFT JOIN players D ON A.player_in_id = D.player_id
                        where game_event_id = '%s';"""

        cursor.execute(statement %event_id)

        results = cursor.fetchone()
        return results
    except dbapi.DatabaseError:
        print("Database Error - game_update_get_all")
    finally:
        cursor.close()
        connection.close()
        
def player_get_events_in_game(game_id, player_id):

    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    statement = """SELECT game_events_type, description FROM game_events
                   WHERE game_id = %s AND player_id = %s"""
    
    cursor.execute(statement %(game_id, player_id))

    results = cursor.fetchall()
    return results

def get_players(game_id, club_name):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor(dictionary=True)

        
    query = """
    SELECT a.player_name, p.position 
    FROM appearances a 
    JOIN players p ON a.player_id = p.player_id
    JOIN clubs c ON c.club_id = a.player_club_id
    WHERE a.game_id = %s AND c.clubs_name = %s
	ORDER BY POSITION;
    """

    cursor.execute(query, (game_id, club_name))
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result

def get_available_countries():
        connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()
        statement = """SELECT DISTINCT country_of_citizenship FROM players WHERE country_of_citizenship IS NOT NULL AND country_of_citizenship != '' ORDER BY country_of_citizenship;"""
        cursor.execute(statement)
        countries = [country[0] for country in cursor.fetchall()]
        cursor.close()
        connection.close()
        return countries

def get_available_positions():
        connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()
        statement = "SELECT DISTINCT position FROM players WHERE position IS NOT NULL AND position != '' ORDER BY position;"
        cursor.execute(statement)
        positions = [position[0] for position in cursor.fetchall()]
        cursor.close()
        connection.close()
        return positions

def get_available_clubs():
        connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()
        statement = "SELECT DISTINCT c.clubs_name FROM players p JOIN clubs c ON p.current_club_id = c.club_id WHERE c.clubs_name IS NOT NULL AND c.clubs_name != '' ORDER BY c.clubs_name;"
        cursor.execute(statement)
        clubs = [club[0] for club in cursor.fetchall()]
        cursor.close()
        connection.close()
        return clubs

def question_game():
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
    
    cursor = connection.cursor(dictionary=True)

    statement = """SELECT players_name,country_of_citizenship 
    FROM players 
    WHERE highest_market_value_in_eur >= 50000000 
    AND last_season > 2017 
    AND players_name IS NOT NULL 
    AND country_of_citizenship IS NOT NULL 
    ORDER BY RAND() 
    LIMIT 1;"""
   
    cursor.execute(statement)
    result_3 = cursor.fetchall()
    cursor.close()
    connection.close()

    return result_3



def random_value():
    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
    
    cursor = connection.cursor(dictionary=True)

    statement = """ SELECT country_of_citizenship 
    FROM players 
    WHERE highest_market_value_in_eur >= 50000000 
    AND last_season > 2015 
    AND country_of_citizenship IS NOT NULL
    AND country_of_citizenship != '' 
    ORDER BY RAND() 
    LIMIT 1;"""
   
    cursor.execute(statement)
    random_value = cursor.fetchall()

    cursor.close()
    connection.close()

    return random_value

def get_player_details(player_id):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    statement = """
        SELECT first_name, last_name, players_name, last_season, country_of_birth, city_of_birth, 
               country_of_citizenship, date_of_birth, sub_position, position, foot, height_in_cm, 
               market_value_in_eur, highest_market_value_in_eur, contract_expiration_date, 
               agent_name, image_url, competitions_name , current_club_name,player_id ,current_club_id, 
               player_code,current_club_domestic_competition_id
        FROM players
        INNER JOIN competitions ON players.current_club_domestic_competition_id = competitions.competition_id
        WHERE player_id = %s;
    """

    cursor.execute(statement, (player_id,))
    player_data = cursor.fetchone()


    if player_data:
        player_data = list(player_data)

        if isinstance(player_data[17], str):
            player_data[17] = player_data[17].replace('-', ' ')

        player_info = {
            "first_name": player_data[0],
            "last_name": player_data[1],
            "players_name": player_data[2],
            "last_season": player_data[3],
            "country_of_birth": player_data[4],
            "city_of_birth": player_data[5],
            "country_of_citizenship": player_data[6],
            "date_of_birth": player_data[7],
            "sub_position": player_data[8],
            "position": player_data[9],
            "foot": player_data[10],
            "height_in_cm": player_data[11],
            "market_value_in_eur": player_data[12],
            "highest_market_value_in_eur": player_data[13],
            "contract_expiration_date": player_data[14],
            "agent_name": player_data[15],
            "image_url": player_data[16],
            "competitions_name": player_data[17],
            "current_club_name": player_data[18],
            "player_id": player_data[19],
            "current_club_id": player_data[20],
            "player_code": player_data[21],
            "current_club_domestic_competition_id": player_data[22]
        }
    else:
        player_info = None

    cursor.close()
    connection.close()
    return player_info

def update_player_details(player_id, **updated_data):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    update_parts = [f"{key} = %s" for key in updated_data]
    update_statement = f"UPDATE players SET {', '.join(update_parts)} WHERE player_id = %s;"

    update_values = tuple(updated_data.values()) + (player_id,)

    cursor.execute(update_statement, update_values)
    connection.commit()
    cursor.close()
    connection.close()

def insert_new_player(new_player_data):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    cursor.execute("SELECT MAX(player_id) FROM players;")
    max_id_result = cursor.fetchone()
    max_id = max_id_result[0] if max_id_result[0] is not None else 0
    next_id = max_id + 1
    new_player_data['player_id'] = next_id

    current_club_name = new_player_data.get('current_club_name')
    cursor.execute("SELECT club_id, domestic_competition_id FROM clubs WHERE clubs_name = %s", (current_club_name,))
    club_info = cursor.fetchone()

    if club_info:
        new_player_data['current_club_id'], new_player_data['current_club_domestic_competition_id'] = club_info

    columns = ', '.join(new_player_data.keys())
    placeholders = ', '.join(['%s'] * len(new_player_data))
    insert_statement = f"INSERT INTO players ({columns}) VALUES ({placeholders});"

    insert_values = tuple(new_player_data.values())

    
    cursor.execute(insert_statement, insert_values)
    connection.commit()
    
    cursor.close()
    connection.close()

def insert_new_club(new_club_data):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    cursor.execute("SELECT MAX(club_id) FROM clubs;")
    max_id_result = cursor.fetchone()
    max_id = max_id_result[0] if max_id_result[0] is not None else 0
    next_id = max_id + 1
    new_club_data['club_id'] = next_id
    #new_club_data['foreigners_percentage'] = int(new_club_data['foreigners_numbers']) * 100 / int(new_club_data['squad_size'])


    """  
    current_club_name = new_player_data.get('current_club_name')
    cursor.execute("SELECT club_id, domestic_competition_id FROM clubs WHERE clubs_name = %s", (current_club_name,))
    club_info = cursor.fetchone()

    if club_info:
        new_player_data['current_club_id'], new_player_data['current_club_domestic_competition_id'] = club_info
    """
    #columns = ', '.join(new_club_data.keys())
    #colx = ', '.join(new_club_data.values())
    #placeholders = ', '.join(['%s'] * len(new_club_data))

    #insert_statement = f"INSERT INTO players ({columns}) VALUES ({placeholders});"

    #insert_values = tuple(new_player_data.values())

    
    #cursor.execute(insert_statement, insert_values)
    #connection.commit()
    #print(columns)
    keystr = ""
    for key in new_club_data.keys():
        keystr += key + ","
    keystr=keystr[0:-1]

    valuestr = ""
    for value in new_club_data.values():
        
        valuestr += f"'{value}'" + ","
    valuestr=valuestr[0:-1]
    

    #print(keystr)

    #print(valuestr)
    insert_statement = f"INSERT INTO clubs ({keystr}) VALUES ({valuestr});"
    print(insert_statement)
    cursor.execute(insert_statement)
    connection.commit()
    cursor.close()
    connection.close()

def delete_player(player_id):
    connection = dbapi.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    statement = """DELETE FROM players WHERE player_id = %s;"""

    cursor.execute(statement, (player_id,))
    connection.commit()
    
    cursor.close()
    connection.close()

    return True





def get_transfer_list(request):
        if request.method == 'POST':
            connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")

            cursor = connection.cursor()
            min_value = int(request.form.get('minvalue'))
            max_value = int(request.form.get('maxvalue'))
            min_age = request.form.get('minage')
            max_age = request.form.get('maxage')
            position = request.form.get('position')
            sub_position = request.form.get('subposition')
            foot=request.form.get("foot")
            nationality = request.form.get('nationality')
            team = request.form.get('team')

            position_pattern = f"%{position}%"
            sub_position_pattern = f"%{sub_position}%"
            foot_pattern = f"%{foot}%"
            nationality_pattern = f"%{nationality}%"
            team_pattern = f"%{team}%"

            statement = """SELECT A.sub_position, A.first_name, A.last_name, TIMESTAMPDIFF(YEAR, A.date_of_birth, CURDATE()) AS age, 
                           A.current_club_name, A.foot, A.height_in_cm, A.market_value_in_eur,
                           A.contract_expiration_date, MAX(B.player_valuations_date) as latest, A.player_id
                           FROM futbalmania.players A
                           Join futbalmania.player_valuations B on A.player_id = B.player_id
                           Join futbalmania.clubs C ON  A.current_club_id = C.club_id
                           WHERE B.market_value_in_eur BETWEEN %s AND %s
                           AND A.position LIKE %s
                           AND A.sub_position LIKE %s
                           AND A.foot LIKE %s
                           AND A.country_of_citizenship LIKE %s
                           AND A.current_club_name LIKE %s
                           AND TIMESTAMPDIFF(YEAR, A.date_of_birth, CURDATE()) BETWEEN %s AND %s
                           AND B.last_season = 2023
                           GROUP BY A.sub_position, A.first_name, A.last_name, age, 
                           A.current_club_name, A.foot, A.height_in_cm, A.market_value_in_eur, A.contract_expiration_date, A.player_id 
                           ORDER BY latest DESC;
                           """
            
            cursor.execute(statement, (min_value, max_value, position_pattern, sub_position_pattern, foot_pattern, nationality_pattern, team_pattern, min_age, max_age))
            result =cursor.fetchall()
            cursor.close()
            connection.close()    
            return result

def get_competition_country(request):
        if request.method == 'POST':
            connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
            cursor = connection.cursor()
            country = request.form.get('country')

            statement="""SELECT A.competitions_name, A.sub_type, A.country_name, A.competition_id
                         FROM futbalmania.competitions A
                         WHERE A.country_name = %s
                         GROUP BY A.competition_id, A.competitions_name, A.sub_type
                         ORDER BY A.competitions_name"""
            
            cursor.execute(statement, (country, ))
            result =cursor.fetchall()
            cursor.close()
            connection.close()    
            return result
        
def create_competition(request):
        if request.method == 'POST':
            connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
            cursor = connection.cursor()
            id = request.form.get('id')
            name = request.form.get('name')
            statement = """ INSERT INTO futbalmania.competitions
                            (competition_id,
                            competition_code,
                            competitions_name,
                            sub_type,
                            competitions_type,
                            country_id,
                            country_name,
                            domestic_league_code,
                            confederation,
                            url)
                            VALUES
                            (%s, %s, %s, "europa_league", "international_cup", -1, "", "", "europa_league", "");"""  
            
            cursor.execute(statement, (id, name, name))
            connection.commit()
            cursor.close()
            connection.close() 

def change_tournament(request):
        if request.method == 'POST':
            connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
            cursor = connection.cursor()
            id = request.form.get('id')
            if 'ban_id' in request.form:
                statement = """ DELETE FROM futbalmania.competitions
                                WHERE competition_id = %s;"""
                cursor.execute(statement, (id, ))

            elif 'new_name' in request.form:
                 name = request.form.get('name')
                 statement = """ UPDATE futbalmania.competitions
                                 SET competitions_name = %s
                                 WHERE competition_id = %s; """
                 cursor.execute(statement, (name, id))
            
            connection.commit()
            cursor.close()
            connection.close() 
     
def update_value(request):
        if request.method == 'POST':
            connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
            cursor = connection.cursor()

            name = request.form.get('name')
            surname = request.form.get('surname')
            team = request.form.get('team')
            value = int(request.form.get('value'))
            team_pattern = f"%{team}%"

            statement = """ SELECT A.player_id, A.current_club_id, A.current_club_domestic_competition_id 
                            FROM futbalmania.players A
                            WHERE A.first_name = %s
                            AND A.last_name = %s
                            AND A.current_club_name LIKE %s
                            LIMIT 1;"""
            
            cursor.execute(statement, (name, surname, team_pattern))
            result =cursor.fetchall()
            if result:
                print(result[0][0], value, result[0][1], result[0][2])
            else:
                print("No results found.")

            if 'insert' in request.form:
                statement2 = """ INSERT INTO futbalmania.player_valuations 
                                VALUES (%s, YEAR(CURDATE()), NOW(), CURDATE(), DATE_ADD(CURDATE(), INTERVAL - WEEKDAY(CURDATE()) DAY),
                                %s, 1, %s, %s); 
                                """
                cursor.execute(statement2, (result[0][0], value, result[0][1], result[0][2]))

            elif 'update' in request.form:
                statement2 = """UPDATE futbalmania.player_valuations 
                                SET market_value_in_eur = %s
                                WHERE player_id = %s AND current_club_id = %s AND player_club_domestic_competition_id = %s
                                AND player_valuations_date = (
                                SELECT MAX(player_valuations_date) 
                                FROM (
                                SELECT player_valuations_date
                                FROM futbalmania.player_valuations
                                WHERE player_id = %s AND current_club_id = %s AND player_club_domestic_competition_id=%s 
                                ) AS subquery
                                );
                                 """
                cursor.execute(statement2, (value, result[0][0], result[0][1], result[0][2], result[0][0], result[0][1], result[0][2]))
                
            elif 'delete' in request.form:
                statement2 =  """   DELETE FROM futbalmania.player_valuations
                                    WHERE player_id = %s
                                    AND current_club_id = %s
                                    AND player_club_domestic_competition_id = %s
                                    AND market_value_in_eur = %s
                                    AND player_valuations_date = (
                                        SELECT MAX(player_valuations_date)
                                        FROM (
                                        SELECT player_valuations_date
                                        FROM futbalmania.player_valuations
                                        WHERE player_id = %s
                                            AND current_club_id = %s
                                            AND player_club_domestic_competition_id = %s
                                        ) AS subquery
                                    );
                                 """
                cursor.execute(statement2, (result[0][0], result[0][1], result[0][2], value, result[0][0], result[0][1], result[0][2]))

            connection.commit()
            cursor.close()
            connection.close() 
    
    
def get_leagues(season, country):
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()

        statement = """ 
                    SELECT 
                        game_id,
                        games.competition_id,
                        season,
                        games_round,
                        games_date,
                        home_club_id,
                        away_club_id,
                        home_club_goals,
                        away_club_goals,
                        c1.clubs_name AS home_club_name,
                        c2.clubs_name AS away_club_name
                        FROM games
                        JOIN clubs c1 ON c1.club_id = games.home_club_id
                        JOIN clubs c2 ON c2.club_id = games.away_club_id
                        JOIN competitions c3 ON c3.competition_id = games.competition_id
                    where 
                    c3.competition_id = %s AND
                    season = %s AND
                    c3.sub_type = "first_tier"
                     ;
         """


        cursor.execute(statement, (season,country, ))

       # cursor.execute(statement)
        result =cursor.fetchall()
        cursor.close()
        connection.close()    
        return result

def getnameofleague():

        
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()

        statement = """ 
                   SELECT 
                        
                        distinct(games.competition_id)
                        
                        
                        FROM games
                   
                        JOIN competitions c3 ON c3.competition_id = games.competition_id
                    where 
                
                    c3.sub_type = "first_tier"
         """



        cursor.execute(statement)
        result =cursor.fetchall()
        cursor.close()
        connection.close()    
        return result

def seasonofleague():

        
        connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
        cursor = connection.cursor()

        statement = """ 
                    SELECT 
                          distinct(season)
                        FROM competitions 
                        JOIN games ON competitions.competition_id = games.competition_id
                    where 
                    sub_type = "first_tier";
                    ORDER BY season ASC

         """



        cursor.execute(statement)
        result =cursor.fetchall()
        cursor.close()
        connection.close()    
        return result

def line_ups():

    connection = dbapi.connect(host = HOST, port = PORT, user = USER, password=PASSWORD, database="futbalmania")
    cursor = connection.cursor()

    statement = """
                SELECT distinct(game_lineups_position) 
                FROM game_lineups;
            """     

    cursor.execute(statement)
    result =cursor.fetchall()
    cursor.close()
    connection.close()
    return result