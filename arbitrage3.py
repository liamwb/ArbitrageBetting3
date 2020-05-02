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
def combinedMarketMargin(odds1, odds2, oddsDraw=0):
    """Returns a combined market margin, given a set of odds."""
    if oddsDraw:
        return (1 / odds1) + (1 / odds2) + (1 / oddsDraw)
    return (1 / odds1) + (1 / odds2)


# If there is an arbitrage opportunity, then to calculate the profit for a
# given investment the following formula is used:
#
# Profit = (Investment / combined market margin) – Investment
def profit(investment, combinedMarketMargin):
    """Returns the profit from an arbitrage bet, given an investment and the combined market margin."""
    return (investment / combinedMarketMargin) - investment


# To calculate how much to stake on each side of the arbitrage bet, the following formula is used:
#
# Individual bets = (Investment x Individual implied odds) / combined market margin
def individualBet(investment, individualImpliedOdds, combinedMarketMargin):
    """Returns the amount to bet on one side of an arbitrage bet, given an investment, the implied odds of the side in
    question, and the combined market margin of the arbitrage opportunity."""
    return (investment * individualImpliedOdds) / combinedMarketMargin


# Classes

class Game:
    # a Game object contains information about a single game from a single betting agency
    def __init__(self, bettingAgency, teamA, teamB, oddsA, oddsB, sport, oddsDraw=0):
        self.bettingAgency = bettingAgency
        self.teamA = teamA
        self.teamB = teamB
        self.oddsA = oddsA
        self.oddsB = oddsB
        self.sport = sport
        self.oddsDraw = oddsDraw
        self.impliedOddsA = 1 / oddsA
        self.impliedOddsB = 1 / oddsB
        if oddsDraw:
            self.impliedOddsDraw = 1/oddsDraw
        self.gameID = teamA + ' vs ' + teamB


class PossibleArbitrage:
    # a PossibleArbitrage object contains information about a single game from two betting agencies (order matters)
    def __init__(self, teamA, teamB, oddsA, oddsB, agencyA, agencyB, sport, oddsDraw=0):
        self.teamA = teamA
        self.teamB = teamB
        self.oddsA = oddsA
        self.oddsB = oddsB
        self.agencyA = agencyA
        self.agencyB = agencyB
        self.sport = sport
        self.oddsDraw = oddsDraw
        self.gameID = teamA + ' vs ' + teamB
        self.CMM = combinedMarketMargin(oddsA, oddsB, oddsDraw)
