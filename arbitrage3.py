"""
ArbitrageBetting3, by Liam Wood-Baker, 2020
A third version of my arbitrage betting program, this time taking into account both two and three outcome games.
"""

import json
import requests

# Keep the key for the-odds-api key secret
api_key = open('api_key.txt').read()

two_outcome_games = []
three_outcome_games = []
two_outcome_arbitrages = []
three_outcome_arbitrages = []


# General purpose functions for arbitrage calculations


# the combined market margin is the sum of the two implied probabilites.
# if it's < 1, then there is an arbitrage opportunity
def combinedMarketMargin(odds1: float, odds2: float, oddsDraw: float = 0) -> float:
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


# Classes

class Game:
    """
     A Game object contains information about a single game from a single betting agency
    """

    def __init__(self, agency: str, team_a: str, team_b: str, odds_a: float, odds_b: float, sport: str,
                 odds_draw: float = 0.0):
        self.bettingAgency = agency
        self.teamA = team_a
        self.teamB = team_b
        self.oddsA = odds_a
        self.oddsB = odds_b
        self.sport = sport
        self.oddsDraw = odds_draw
        self.impliedOddsA = 1 / odds_a
        self.impliedOddsB = 1 / odds_b
        if odds_draw:
            self.impliedOddsDraw = 1 / odds_draw
        self.gameID = team_a + ' vs ' + team_b


class PossibleArbitrage:
    """
    A PossibleArbitrage object contains information about a single game from two betting agencies (order matters)
    """

    def __init__(self, team_a: str, team_b: str, odds_a: float, odds_b: float, agency_a: str, agency_b: str, sport: str,
                 odds_draw: float = 0.0):
        self.teamA = team_a
        self.teamB = team_b
        self.oddsA = odds_a
        self.oddsB = odds_b
        self.agencyA = agency_a
        self.agencyB = agency_b
        self.sport = sport
        self.oddsDraw = odds_draw
        self.gameID = team_a + ' vs ' + team_b
        self.CMM = combinedMarketMargin(odds_a, odds_b, odds_draw)


# Now get the odds for each event in each sport for each agency. 'Sport' being set to 'upcoming' means that the odds
# for all upcoming games will be returned
odds_response = requests.get('https://api.the-odds-api.com/v3/odds', params={
    'api_key': api_key,
    'sport': 'upcoming',
    'region': 'au',  # uk | us | eu | au
    'mkt': 'h2h'  # h2h | spreads | totals
})
odds_json = json.loads(odds_response.text)

# put the data into the appropriate odds
for game in odds_json['data']:
    sport = game['sport_nice']
    team_a, team_b = game['teams']  # could have a third element if there's a draw possibility
    for site in game['sites']:
        betting_agency = site['site_nice']  # previous version used 'site_key', but the nice one is nicer
        if len(site['odds']['h2h']) == 2:  # if there is no draw outcome
            odds_a, odds_b = site['odds']['h2h']
            two_outcome_games.append(Game(betting_agency, team_a, team_b, odds_a, odds_b, sport))
        if len(site['odds']['h2h']) == 3:  # if there is a draw outcome
            odds_a, odds_b, odds_draw = site['odds']['h2h']
            three_outcome_games.append(Game(betting_agency, team_a, team_b, odds_a, odds_b, sport, odds_draw))
