from flask import Flask, render_template, url_for, request , session ,redirect, url_for, flash
import random
import requests
from data_base import *
import random

class Clubs:
    def __init__(self, country, season):
        self.country = country
        self.season = season
        self.clubs = []
        self.flag = "https://www.nationsonline.org/flags/" + country.lower() + "_flag.gif"

    def setCountry(self,country):
        self.country = country

    def setSeason(self,season):
        self.season = season

    def setClubs(self,ctry, ssn,clbs):
        for clb in clbs:
            if self.country == ctry and self.season == ssn:
                self.clubs.append(clb)
        

    

    def __repr__(self):
        return f"Club( '{self.country}', '{self.season}', '{self.clubs}')"












app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route("/")
@app.route("/home")
def home():
    x = line_ups()

    x = [item[0] for item in x]

    #print(x)
    return render_template('home.html')

############################## PLAYER PAGE #########################################
@app.route("/player")
def player():
    search_query = request.args.get('search', '')
    country_filter = request.args.get('country', '')
    position_filter = request.args.get('position')
    club_filter = request.args.get('club')
    page = request.args.get('page', 1, type=int)
    per_page = 30

    available_countries = get_available_countries()
    available_positions = get_available_positions()
    available_clubs = get_available_clubs()

    player_values = player_t()  

    if search_query:
        player_values = [player for player in player_values if search_query.lower() in player[0].lower()]

    if club_filter:
        player_values = [player for player in player_values if player[1] == club_filter]
    
    if position_filter:
        player_values = [player for player in player_values if player[2] == position_filter]
      
    if country_filter:
        player_values = [player for player in player_values if player[3] == country_filter] 

    total = len(player_values)
    start = (page - 1) * per_page
    end = start + per_page
    players_on_page = player_values[start:end]

    total_pages = total // per_page + (1 if total % per_page > 0 else 0)
    return render_template('player.html', title='Player', result=players_on_page,  countries=available_countries, positions=available_positions, clubs=available_clubs ,page=page, total_pages=total_pages,search_query=search_query, country_filter=country_filter, position_filter=position_filter, club_filter=club_filter)

@app.route("/player/<int:player_id>")
def player_details(player_id):
    player_info = get_player_details(player_id)

    if not player_info:
        return "Player not found", 404

    return render_template('player_details.html', player=player_info)

@app.route("/player/add", methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        new_player_data = {
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'players_name': request.form.get('players_name'),
                'last_season': request.form.get('last_season'),
                'player_code': request.form.get('player_code'),  
                'country_of_birth': request.form.get('country_of_birth'),
                'city_of_birth': request.form.get('city_of_birth'),
                'country_of_citizenship': request.form.get('country_of_citizenship'),
                'date_of_birth': request.form.get('date_of_birth'),  
                'sub_position': request.form.get('sub_position'),
                'position': request.form.get('position'),
                'foot': request.form.get('foot'),
                'height_in_cm': request.form.get('height_in_cm'),  
                'market_value_in_eur': request.form.get('market_value_in_eur'),  
                'highest_market_value_in_eur': request.form.get('highest_market_value_in_eur'),  
                'contract_expiration_date': request.form.get('contract_expiration_date'),  
                'agent_name': request.form.get('agent_name'),
                'image_url': request.form.get('image_url'),
                'current_club_name': request.form.get('current_club_name')

        }      
        insert_new_player(new_player_data)
        return redirect(url_for('player'))
    
    player = {'first_name': '', 'last_name': '', 'players_name': '', 'last_season': '', 'player_code': '', 'country_of_birth': '', 'city_of_birth': '', 'country_of_citizenship': '', 'date_of_birth': '', 'sub_position': '', 'position': '', 'foot': '', 'height_in_cm': '', 'market_value_in_eur': '', 'highest_market_value_in_eur': '', 'contract_expiration_date': '', 'agent_name': '', 'image_url': '', 'current_club_name': ''}

      

    return render_template('add_player.html', player=player)


@app.route("/club/add", methods=['GET', 'POST'])
def add_club():
    data = club_list()
    country = [i[1] for i in data]
    lcode = [i[3] for i in data]
    
    
    unique_list1 = []
    for x in country:
        if x not in unique_list1:
            unique_list1.append(x)
    country = unique_list1[:]

    unique_list2 = []
    for x in lcode:
        if x not in unique_list2:
            unique_list2.append(x)

    lcode = unique_list2[:]
    #print(country)
    #print(lcode)
    if request.method == 'POST':
        new_club_data = {
                'club_id':"",
                'clubs_name': f"{request.form.get('clubs_name')}",
                'club_code': f"{request.form.get('club_code')}",
                'domestic_competition_id': f"{request.form.get('domestic_competition_id')}",
                'total_market_value': f"{request.form.get('total_market_value')}",
                'squad_size': f"{request.form.get('squad_size')}",
                'average_age': f"{request.form.get('average_age')}",
                'foreigners_number': f"{request.form.get('foreigners_number')}",  
                'foreigners_percentage': f"{request.form.get('foreigners_percentage')}",
                'national_team_players': f"{request.form.get('national_team_players')}",
                'stadium_name': f"{request.form.get('stadium_name')}",
                'stadium_seats': f"{request.form.get('stadium_seats')}",
                'net_transfer_record': f"{request.form.get('net_transfer_record')}",  
                'coach_name': f"{request.form.get('coach_name')}",
                'last_season': f"{request.form.get('last_season')}"
        }    
        print("xxx")  
        print(new_club_data)
        print("xxx")
        insert_new_club(new_club_data)
        return redirect(url_for('clubs'))
    
    player = {'clubs_name': '', 'domestic_competition_id': '', 'squad_size': '', 'foreigners_numbers': '', 'national_team_player': '', 'stadium_name': '', 'stadium_seats': '', 'net_transfer_record': '', 'last_season': '12'}
    print()

    countrycode = zip(country, lcode)
    return render_template('add_club.html', club=player, country=country, lcode=lcode, countrycode=countrycode)
  



@app.route("/player/edit/<int:player_id>", methods=['GET', 'POST'])
def edit_player(player_id):
    player_info = get_player_details(player_id)
    if not player_info:
        flash('Player not found.', 'error')
        return redirect(url_for('player'))

    if request.method == 'POST':
        updated_data = {
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'players_name': request.form.get('players_name'),
                'last_season': request.form.get('last_season'),
                'player_code': request.form.get('player_code'),  
                'country_of_birth': request.form.get('country_of_birth'),
                'city_of_birth': request.form.get('city_of_birth'),
                'country_of_citizenship': request.form.get('country_of_citizenship'),
                'date_of_birth': request.form.get('date_of_birth'),  
                'sub_position': request.form.get('sub_position'),
                'position': request.form.get('position'),
                'foot': request.form.get('foot'),
                'height_in_cm': request.form.get('height_in_cm'),  
                'highest_market_value_in_eur': request.form.get('highest_market_value_in_eur'),  
                'agent_name': request.form.get('agent_name'),
                'image_url': request.form.get('image_url'),
                'current_club_name': request.form.get('current_club_name')
        }
        
        update_player_details(player_id, **updated_data)
        return redirect(url_for('player_details', player_id=player_id))

    return render_template('edit_player.html', player=player_info)


@app.route("/player/delete/<int:player_id>")
def player_delete(player_id):
    delete_player(player_id)
    return redirect(url_for('player'))

################################# APPEARANCES ########################################
@app.route('/appearances')
def appearances():
    search_query = request.args.get('search', '')
    club_filter = request.args.get('club')
    page = request.args.get('page', 1, type=int)
    per_page = 30

    appearances_data = get_appearances_data() 

    available_competitions = get_available_competitions()
    available_clubs = get_available_clubs()

    if search_query:
        appearances_data = [appearance for appearance in appearances_data if search_query.lower() in appearance[1].lower()]
    
   
    if club_filter:
        appearances_data = [appearance for appearance in appearances_data if appearance[2] == club_filter]

    total = len(appearances_data)
    start = (page - 1) * per_page
    end = start + per_page
    players_on_page = appearances_data[start:end]

    total_pages = total // per_page + (1 if total % per_page > 0 else 0)

    return render_template('appearances.html',title='Appearances', result=players_on_page , clubs=available_clubs ,page=page, total_pages=total_pages,search_query=search_query,club_filter=club_filter)

@app.route("/appearances/<appearance_id>")
def appearance_details(appearance_id):
    appearance_info = get_appearance_details(appearance_id)

    if not appearance_info:
        return "Appearance not found", 404

    return render_template('appearance_details.html', appearance=appearance_info)


@app.route("/appearances/edit/<appearance_id>", methods=['GET', 'POST'])
def edit_appearance(appearance_id):
    appearance_info = get_appearance_details(appearance_id)
    if not appearance_info:
        flash('Appearance not found.', 'error')
        return redirect(url_for('appearances'))

    if request.method == 'POST':
        updated_data = {
            'yellow_cards': request.form.get('yellow_cards'),
            'red_cards': request.form.get('red_cards'),
            'goals': request.form.get('goals'),
            'assists': request.form.get('assists'),
            'minutes_played': request.form.get('minutes_played')}
        
        
        update_appearance_details(appearance_id, **updated_data)
        return redirect(url_for('appearance_details', appearance_id=appearance_id))

    return render_template('edit_appearance.html', appearance=appearance_info)

@app.route("/appearance/add", methods=['GET', 'POST'])
def add_appearance():
    if request.method == 'POST':
        new_appearance_data = {
            'appearance_id': request.form.get('appearance_id'), 
            'game_id': request.form.get('game_id'),
            'player_id': request.form.get('player_id'),
            'player_club_id': request.form.get('player_club_id'),
            'appearances_date': request.form.get('appearances_date'),
            'competition_id': request.form.get('competition_id'),
            'yellow_cards': request.form.get('yellow_cards'),
            'red_cards': request.form.get('red_cards'),
            'goals': request.form.get('goals'),
            'assists': request.form.get('assists'),
            'minutes_played': request.form.get('minutes_played')
        }

        insert_new_appearance(new_appearance_data)
        return redirect(url_for('appearances'))

    return render_template('add_appearance.html')

@app.route("/appearance/delete/<appearance_id>")
def appearance_delete(appearance_id):
    delete_appearance(appearance_id)
    return redirect(url_for('appearances'))
#################################################################################################################################

@app.route("/clubs")
def clubs():
    #kka
    data = club_list()
    datacopied = []
    country = []
    #convert the tuple to list
    for i in range(len(data)):
        datacopied.append(data[i])

    valxvaly = []
    valxvalz = []
    #append the clubs
    for i in range(len(datacopied)):
        valxvaly.append(datacopied[i][1])
        valxvalz.append(datacopied[i][2])
    
    unique_list = []
    # get unique countries
    for x in valxvaly:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    
    #create a dictionary
    my_dict = {key: [] for key in unique_list}
    my_dict2 = {key: [] for key in unique_list}

    for i in range(0, len(datacopied)):
        if datacopied[i][1] in my_dict:
            my_dict[datacopied[i][1]].append(datacopied[i][0])
            my_dict2[datacopied[i][1]].append(datacopied[i][2])

            
    merged_dict = {}
    for key in my_dict.keys():
        merged_dict[key] = zip(my_dict[key], my_dict2[key])
   
    return render_template('clubs.html', title='Player', country=merged_dict, clubn=[])

@app.route("/clubs_game?club_id")
@app.route("/clubs_game")
def clubs_game(club_id=3):
    club_id = request.args.get('club_id', default=3, type=int)
    club_games = clubgame_list(club_id)
    return render_template('clubs_game.html', title='Clubs Games', result=club_games)

#kaleab
@app.route("/leagues")
def leagues():
    league = request.args.get("league", default="GB1")
    season = request.args.get("season", default="2023")
    url = url_for('leagues', league=league, season=season)
    data = get_leagues(league,season)
    competition_ids = list(set([field[1] for field in data]))
    clud_ids =list(set([field[6] for field in data]))
    competition_score = []
    #print(competition_ids)
    templist = []
    #
    # print(competition_ids)
    for i in competition_ids:
        if i == league:
            clud_ids = list(set([field[6] for field in data if field[1] == i]))

            #clud_ids =list(set([field[6] for field in data] if field[1] == i))

    point = 0
    for i in clud_ids:
        club_name = ""
        points = 0 #
        scored_for = 0 #
        scored_against = 0 #
        netscore = 0
        match_played = 0 #
        win = 0#
        draw = 0#
        lose = 0 #
        for j in data:
            if i == j[5]: 
                club_name = j[9]
                if j[7] > j[8]:
                    point = 3
                    win += 1
                    
                elif j[7] == j[8]:
                    point = 1
                    draw += 1
                else:
                    point = 0
                    lose += 1
                
                match_played += 1
                scored_for += j[7]
                scored_against += j[8]
                points += point

                
            elif i == j[6]:
                club_name = j[10]
                if j[7] < j[8]:
                    point = 3
                    win += 1
                elif j[7] == j[8]:
                    point = 1
                    draw += 1
                else:
                    point = 0
                    lose += 1
                match_played += 1
                scored_for += j[8]
                scored_against += j[7]
                points += point
        netscore = scored_for - scored_against
        templist.append([club_name, match_played, win, draw, lose, scored_for, scored_against, netscore, points])
               
    clud_ids.append(point)
                    
        
    templist = (sorted(templist, key=lambda x: (x[-1], x[-2])))
    templist = templist[::-1]
    
    #competition_score.append([j[6], 3, 0, 0])
    x = getnameofleague()
    x = [item[0] for item in x]

    y = seasonofleague()
    y = [item[0] for item in y]
    y.reverse()
    print(y)
    
    return render_template('leagues.html', title='Leagues', result=templist, leaguesnamelist = x, leaguesseason = y   )

############################################ MCQ GAME ##########################################################

@app.route("/quiz_game", methods=['GET', 'POST'])
def quiz_game():
    if 'score' not in session:
        session['score'] = 0

    if request.method == 'POST':
        user_answer = request.form.get('answer')  
        if not user_answer:
            q = session.get('last_question', '')
            values = session.get('last_values', [])
            return render_template('quiz_game.html', title='Quiz Game', q=q, values=values, submitted=False, error_message="Please select an answer.")

        correct_answer = session.get('correct_answer', '')
        is_correct = user_answer == correct_answer

        if is_correct:
            session['score'] += 1
            return render_template('quiz_game.html', is_correct=True, score=session['score'], submitted=True)
        else:
            final_score = session['score']
            session['score'] = 0
            return render_template('quiz_game.html', is_correct=False, correct_answer=correct_answer, score=final_score, submitted=True, game_over=True)
    else:
        q = question_game()
        session['correct_answer'] = q[0]['country_of_citizenship']
        n = q[-1]['players_name']

        values = [session['correct_answer']]
        while len(values) < 3:
            random_country = random_value()[0]['country_of_citizenship']
            if random_country not in values:
                values.append(random_country)

        random.shuffle(values)
        session['last_question'] = n
        session['last_values'] = values

        return render_template('quiz_game.html', title='Quiz Game', q=n, values=values, submitted=False)
##############################################################################################################################################################

@app.route("/competitions", methods=['POST', 'GET'])
def competitions():
    if request.method == 'POST':
        competition = get_competition_country(request)
        return render_template('competitions.html', title='Competitions', competition=competition)
    else:
        return render_template('competitions.html', title='Competitions', competition=None)
    
@app.route('/change_competition', methods=['POST'])
def change_competition():
        if request.method == 'POST':
            print(request)
            change_tournament(request)
            return render_template('competitions.html', title='Competitions')
        else:
            return render_template('competitions.html', title='Competitions')

@app.route("/games", methods=['POST', 'GET'])
def games():

    if request.method == 'POST': #For adding new games
        all_form_data = request.form
        requests.post( url_for('games_add', _external=True), all_form_data )
        return redirect( url_for('games') ) 

    game_competitions_list = request.args.getlist('comp')
    game_season_list = request.args.getlist('game_season')
    game_rounds_list = request.args.getlist('game_rounds')
    game_clubs_list = request.args.getlist('game_clubs')
    page_get = request.args.get('page')
    page_num = 0
    try:
        page_num = int(page_get)
        if page_num < 1:
            page_num = 1
    except:
        page_num = 1

    #for filtering menu
    game_competitions = game_get_comp()
    game_season = game_get_season()
    game_rounds = game_get_round()
    game_clubs = game_get_clubs()
    #for getting list of games
    game_games = game_get_games(game_competitions_list, game_season_list, game_rounds_list, game_clubs_list, page_num)
    #page render
    return render_template('games.html', 
                            title='Games',
                            game_competitions_list = game_competitions_list,
                            game_season_list = game_season_list,
                            game_rounds_list = game_rounds_list,
                            game_clubs_list = game_clubs_list,
                            game_competitions = game_competitions,
                            game_season = game_season,
                            game_rounds = game_rounds,
                            game_clubs = game_clubs,
                            game_games = game_games,
                            page_num = page_num)

@app.route("/games_delete")
def games_delete():
    game_id = request.args.get("game_id")
    
    games_delete_game( int(game_id) )

    return redirect( request.headers.get("Referer") ) 

@app.route("/games_add", methods =['POST', 'GET'])
def games_add():
    
    game_datas = request.form
    
    games_add_game(game_datas)

    return redirect( url_for('games') ) 

@app.route("/games/edit/<int:game_id>", methods=['POST', 'GET'])
def edit_game(game_id):

    if request.method == 'POST':
        updated_game = { #This columns will be dropped when i normalize
            'competition_id': request.form.get('competition_id'),
            'season': request.form.get('season'),
            'games_round': "'" + request.form.get('games_round') + "'",
            'games_date': "'" + request.form.get('games_date') + "'",
            'home_club_id': request.form.get('home_club_id'), #from search
            'away_club_id': request.form.get('away_club_id'), #from search
            'home_club_goals': request.form.get('home_club_goals'),
            'away_club_goals': request.form.get('away_club_goals'),
            'home_club_position': request.form.get('home_club_position'),
            'away_club_position': request.form.get('away_club_position'),
            'home_club_manager_name': "'" + request.form.get('home_club_manager_name') + "'",
            'away_club_manager_name': "'" + request.form.get('away_club_manager_name') + "'",
            'stadium': "'" + request.form.get('stadium') + "'",
            'attendance': request.form.get('attendance'),
            'referee': "'" + request.form.get('referee') + "'",
            #'url': '',
            'home_club_formation': "'" + request.form.get('home_club_formation') + "'",
            'away_club_formation': "'" + request.form.get('away_club_formation') + "'",
            'home_club_name': request.form.get('home_club_name'),
            'away_club_name': request.form.get('away_club_name'),
            #'games_aggregate': ''
            'competition_type': "''" #from search
        }

        game_update_game(updated_game, game_id)
        return redirect( url_for('games_details', game_id = game_id) ) 
    else:
        game_competitions = game_get_comp()
        game_details = game_update_get_all(game_id)
        return render_template('edit_game.html',
                                game_details = game_details,
                                game_competitions = game_competitions)

@app.route("/games_details/<int:game_id>", methods=['POST', 'GET'])
def games_details(game_id):

    if request.method == 'POST': #For adding new games
        all_form_data = request.form
        requests.post( url_for('games_events_add', _external=True), all_form_data )
        return redirect( url_for('games_details', game_id = game_id) ) 

    games_details = games_details_get_game( int(game_id) )
    games_events = games_details_get_event( int(game_id) )
    home_line = get_players(game_id, games_details[0] )
    away_line = get_players(game_id, games_details[1] )

    print(home_line)

    return render_template('game_details.html',
                            games_details = games_details,
                            games_events = games_events,
                            home_line = home_line,
                            away_line = away_line)

@app.route("/game_events_delete")
def game_events_delete():
    game_event_id = request.args.get("game_event_id")
    
    games_events_delete_event( game_event_id )

    return redirect( request.headers.get("Referer") ) 

@app.route("/games_events_add", methods =['POST', 'GET'])
def games_events_add():
    
    game_datas = request.form
    print(game_datas)
    
    games_details_add_game_events(game_datas)

    return redirect( url_for('games_details', game_id = game_datas["game_id"])  ) 

@app.route("/game_events/edit/<int:game_id>/<string:event_id>", methods=['POST', 'GET'])
def edit_game_event(event_id, game_id):

    if request.method == 'POST':
        updated_game = { #This columns will be dropped when i normalize
            'minute': request.form.get('minute'),
            'game_events_type': "'" + request.form.get('game_events_type') + "'",
            'club_id': '',
            'player_id': '',
            'player_in_id': '',
            'description': "'" + request.form.get('description') + "'",
            'player_assist_id': "''"
        }

        player_names = {
            'player_name': "'" + request.form.get('player_name') + "'",
            'player_in_name': "'" + request.form.get('player_in_name') + "'",
            'club': "'" + request.form.get('clubs_name') + "'"
        }

        game_update_game_event(updated_game, player_names, event_id)
        return redirect( url_for('games_details', game_id = game_id) ) 
    else:
        event_type = [["Cards"], ["Substitutions"], ["Goals"], ["Others"]]
        event_details = event_update_get_all(event_id)
        return render_template('edit_game_event.html',
                                game_id = game_id,
                                event_type = event_type,
                                game_details = event_details)


@app.route("/transfer", methods=['POST', 'GET'])
def transfer():
    if request.method == 'POST':
        players = get_transfer_list(request)
        return render_template('transfer.html', title='Transfer', players=players)
    else:
        return render_template('transfer.html', title='Transfer', players=None)

@app.route("/player_valuation")
def player_valuation():
    return render_template('player_valuation.html', title='Player Valuation')

@app.route("/sell_player")
def sell_player():
    return render_template('sell_player.html', title='Sell Player')

@app.route("/update_market_value", methods=['POST', 'GET'])
def update_market_value():
    if request.method == 'POST':
        update_value(request)
        return render_template('update_market_value.html', title='UpdateValue')
    else:
        return render_template('update_market_value.html', title='Update Market Value')

@app.route("/create_tournament", methods=['POST', 'GET'])
def create_tournament():
    if request.method == 'POST':
        create_competition(request)
        return render_template('create_tournament.html', title='create_tournament')
    else:
        return render_template('create_tournament.html', title='create_tournament')

if __name__ == '__main__':
    app.run(debug=True, port=8000)




