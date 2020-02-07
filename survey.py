"""Hemlock-Nash example application with iterated Prisoner's Dilemma (ipd)"""

from hemlock_nash import Game, Player, Strategy, Payoff, ipd

from hemlock import *

from random import random

PAYOFF_MATRIX = {
    ('Cooperate','Cooperate'): (3,3),
    ('Cooperate','Defect'): (0,5),
    ('Defect','Cooperate'): (5,0),
    ('Defect','Defect'): (1,1)
}
# probability of 'noise'; i.e. player will deviate from prescribed strategy
P_NOISE = .2 
ROUNDS = 10

def noisy_tft(player):
    """Tit for tat with noise"""
    action = ipd.tit_for_tat(player)
    if random() < P_NOISE:
        return 'Cooperate' if action == 'Defect' else 'Defect'
    return action    

@route('/survey')
def Start(origin=None):
    """Survey

    The survey begins with a game description page, followed by estimation 
    pages. The estimation pages ask participants to estimate the 
    probability that the Red player will Cooperate next round. 
    
    After the page is submitted, the `Submit` function records the 
    participant's prediction accuracy.
    """
    b = Branch()

    # game description page
    p = Page(b)
    Label(p, label=ipd.description(PAYOFF_MATRIX))

    # estimation pages
    game = create_game()
    [create_estimation_page(b, game, i) for i in range(ROUNDS)]

    p = Page(b, terminal=True)
    Label(p, label='<p>Thank you for completing the study!</p>')
    return b

def create_game():
    """Create IPD game with two players and a payoff matrix"""
    game = Game()
    Player(game, name='Red', strategy=noisy_tft)
    Player(game, name='Blue', strategy=noisy_tft)
    Payoff.matrix(game, PAYOFF_MATRIX)
    return game

def create_estimation_page(branch, game, round):
    """Create an estimation page"""
    p = Page(branch, cache_compile=True)
    Label(p, label=game.html_table()) # game summary table
    Range(
        p,
        var='RedCoopHat',
        label='<p>From 0% to 100%, how likely do you think Red is to Cooperate next round?</p>',
    )
    Submit.compute_accuracy(p, game=game, round=round)
    game.play()

@Submit.register
def compute_accuracy(page, game, round):
    """Play a round of the IPD

    Use embedded data to track the Red and Blue player's actions and 
    prediction accuracy using a Brier score.
    """
    estimate = page.questions[-1]
    estimate.data = red_coop_hat = float(estimate.data) / 100
    red_coop = int(game.actions['Red'][round] == 'Cooperate')
    blue_coop = int(game.actions['Blue'][round] == 'Cooperate')

    Embedded(page, var='RedCoop', data=red_coop)
    Embedded(page, var='BlueCoop', data=blue_coop)
    Embedded(page, var='Brier', data=(red_coop_hat-red_coop)**2)