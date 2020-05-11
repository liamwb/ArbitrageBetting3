"""
ArbitrageBetting3, by Liam Wood-Baker, 2020
A third version of my arbitrage betting program, this time taking into account both two and three outcome games.
"""

import json
import sys
import requests

# Keep the key for the-odds-api key secret
with open('api_key.txt') as f:
    api_key = f.read()

games = []
arbitrages = []


# General purpose functions for arbitrage calculations


# the combined market margin is the sum of the two implied probabilites.
# if it's < 1, then there is an arbitrage opportunity
def combinedMarketMargin(odds1: float, odds2: float, oddsDraw: float = 0.0) -> float:
    """Returns a combined market margin, given a set of odds."""
    if oddsDraw:
        return (1 / odds1) + (1 / odds2) + (1 / oddsDraw)
    return (1 / odds1) + (1 / odds2)


# If there is an arbitrage opportunity, then to calculate the profit for a
# given investment the following formula is used:
#
# Profit = (Investment / combined market margin) – Investment
def profit(investment: float, combined_market_margin: float) -> float:
    """Returns the profit from an arbitrage bet, given an investment and the combined market margin."""
    return (investment / combined_market_margin) - investment


# To calculate how much to stake on each side of the arbitrage bet, the following formula is used:
#
# Individual bets = (Investment x Individual implied odds) / combined market margin
def individualBet(investment: float, individual_implied_odds: float, combined_market_margins: float) -> float:
    """
    Returns the amount to bet on one outcome in an arbitrage opportunity
    """
    return (investment * individual_implied_odds) / combined_market_margins


def printGames():
    """prints all the games in a readable format"""

    for game in two_outcome_games:
        print(f'{game.team_a} vs {game.team_b} at {game.odds_a} to {game.odds_b} with {game.agency} ({game.sport}) \n')

    for game in three_outcome_games:
        print(f'{game.team_a} vs {game.team_b} at {game.odds_a} to {game.odds_b} ({game.odds_draw} to draw) '
              f'with {game.agency}  ({game.sport})\n')


def printBestArbitrages():
    print('------------Two outcome games------------ \n')
    for arbitrage_object in two_outcome_arbitrages:
        implied_odds_a = 1 / arbitrage_object.odds_a
        implied_odds_b = 1 / arbitrage_object.odds_b
        CMM = round(combinedMarketMargin(arbitrage_object.odds_a, arbitrage_object.odds_b), 2)
        bet_a = round(individualBet(100, implied_odds_a, CMM), 2)
        bet_b = round(individualBet(100, implied_odds_b, CMM), 2)
        print(
            f'For {arbitrage_object.gameID} ({arbitrage_object.sport}) \n'
            f'a combined market margin of {CMM} can be achieved by: \n'
            f'betting {bet_a}% on {arbitrage_object.team_a} with {arbitrage_object.agency_a} ({arbitrage_object.odds_a}),\n'
            f'and {bet_b}% on {arbitrage_object.team_b} with {arbitrage_object.agency_b} ({arbitrage_object.odds_b}). \n'
            f'This will yield a profit of {round(profit(100, CMM), 2)}%. \n'
        )
    print('\n------------Three outcome games------------')
    for arbitrage_object in three_outcome_arbitrages:
        implied_odds_a = 1 / arbitrage_object.odds_a
        implied_odds_b = 1 / arbitrage_object.odds_b
        implied_odds_draw = 1 / arbitrage_object.odds_draw
        CMM = round(combinedMarketMargin(arbitrage_object.odds_a, arbitrage_object.odds_b, arbitrage_object.odds_draw),
                    2)
        bet_a = round(individualBet(100, implied_odds_a, CMM), 2)
        bet_b = round(individualBet(100, implied_odds_b, CMM), 2)
        bet_draw = round(individualBet(100, implied_odds_draw, CMM), 2)
        print(
            f'For {arbitrage_object.gameID} ({arbitrage_object.sport}) \n'
            f'a combined market margin of {CMM} can be achieved by: \n'
            f'betting {bet_a}% on {arbitrage_object.team_a} with {arbitrage_object.agency_a} ({arbitrage_object.odds_a}), \n'
            f'{bet_b}% on {arbitrage_object.team_b} with {arbitrage_object.agency_b} ({arbitrage_object.odds_b}), \n'
            f'and {bet_draw}% on a draw with {arbitrage_object.agency_draw} ({arbitrage_object.agency_draw}). \n'
            f'This will yield a profit of {round(profit(100, CMM), 2)}%. \n'
        )


# Classes

class Game:
    """
     A Game object contains information about a single game from a single betting agency

     teams and odds should be in the format team_1, team_2, team_3, etc.
     odds_1 is either the odds of team_2 winning, or the odds of a draw if there is no such team
    """

    def __init__(self, agency: str, teams: dict, odds: dict, sport: str):
        self.agency = agency
        self.sport = sport
        self.teams = teams
        self.odds = odds
        self.game_id = teams['team_1'] + ' vs ' + self.teams['team_2']


class Arbitrage:
    """
    an arbitrage opportunity for a single game, with odds from two or more betting agencies
    teams, odds and agencies should be in the form 'team_1', 'team_2', etc.
    """

    def __init__(self, teams: dict, odds: dict, agencies:dict, sport):
        self.teams = teams
        self.odds = odds
        self.agencies = agencies
        self.sport = sport
        self.gameID = teams['team_a'] + ' vs ' + teams['team_b']



# Function for doing things


def getOddsJson(region: str):
    """Gets all the odds available from region"""
    # Get the odds for each event in each sport for each agency. 'Sport' being set to 'upcoming' means that the odds
    # for all upcoming games will be returned
    odds_response = requests.get('https://api.the-odds-api.com/v3/odds', params={
        'api_key': api_key,
        'sport': 'upcoming',
        'region': region,  # uk | us | eu | au
        'mkt': 'h2h'  # h2h | spreads | totals
    })
    odds_json = json.loads(odds_response.text)

    if not odds_json['success']:
        print(f'There was a problem getting the odds for {region}')
        sys.exit()
    else:
        print(f'Got odds for {region} successfully')
    return odds_json


def fillGames(odds_json):
    """Fills the games arrays with the data from odds_json"""
    # put the data into the appropriate odds
    for game in odds_json['data']:
        sport = game['sport_nice']
        team_1, team_2 = game['teams']
        teams = {'team_1': team_1, 'team_2': team_2}
        for site in game['sites']:
            betting_agency = site['site_nice']  # previous version used 'site_key', but the nice one is nicer
            odds = {}
            for i, o in enumerate(site['odds']['h2h']):
                odds.update({f'team_{i+1}': o})
            games.append(Game(betting_agency, teams, odds, sport))

    # two_outcome_games and three_outcome_games are now full of games


def fillArbitrages():
    """Fills the arbitrage arrays with arbitrage opportunities given the info in the games arrays"""
    # fill the arbitrage arrays
    gameIDs = {game.gameID for game in two_outcome_games}
    for ID in gameIDs:
        # all the games with the same gameID
        relevant_games = list(filter(lambda x: x.gameID == ID, two_outcome_games))
        # the best arbitrage opportunity will come from the greatest odds for each game
        game_a = max(relevant_games, key=lambda x: x.odds_a)
        game_b = max(relevant_games, key=lambda x: x.odds_b)
        two_outcome_arbitrages.append(TwoOutcomeArbitrage(game_a.team_a, game_a.team_b, game_a.odds_a, game_b.odds_b,
                                                          game_a.agency, game_b.agency, game_a.sport))

    gameIDs = {ID.gameID for ID in three_outcome_games}
    for ID in gameIDs:
        relevant_games = list(filter(lambda x: x.gameID == ID, three_outcome_games))
        game_a = max(relevant_games, key=lambda x: x.odds_a)
        game_b = max(relevant_games, key=lambda x: x.odds_b)
        game_draw = max(relevant_games, key=lambda x: x.odds_draw)
        three_outcome_arbitrages.append(
            ThreeOutcomeArbitrage(game_a.team_a, game_a.team_b, game_a.odds_a, game_b.odds_b,
                                  game_draw.odds_draw, game_a.agency, game_b.agency,
                                  game_draw.agency, game_a.sport))


# def pickRegion():
#     regions = input('Which regions would you like odds from? (uk, us, eu, au, all) ')
#     all_regions = False
#     if 'all' in regions:
#         all_regions = True
#     if 'uk' in regions or all_regions:
#         fillGames(getOddsJson('uk'))
#     if 'us' in regions or all_regions:
#         fillGames(getOddsJson('us'))
#     if 'eu' in regions or all_regions:
#         fillGames(getOddsJson('eu'))
#     if 'au' in regions or all_regions:
#         fillGames(getOddsJson('au'))
#
#     fillArbitrages()
#
#     two_outcome_arbitrages.sort(key=lambda x: combinedMarketMargin(x.odds_a, x.odds_b))
#     three_outcome_arbitrages.sort(key=lambda x: combinedMarketMargin(x.odds_a, x.odds_b, x.odds_draw))


