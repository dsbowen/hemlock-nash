"""Hemlock-Nash example application with iterated Prisoner's Dilemma (ipd)"""

from hemlock_nash import Game, Player, Strategy, Payoff, ipd

from hemlock import *

from math import log2
from random import random, shuffle

PAYOFF_MATRIX = {
    ('Cooperate','Cooperate'): (3,3),
    ('Cooperate','Defect'): (0,5),
    ('Defect','Cooperate'): (5,0),
    ('Defect','Defect'): (1,1)
}
# probability of 'noise'; i.e. player will deviate from prescribed strategy
P_NOISE = .2
ROUNDS = 10
SIMULATIONS = 100
SMOOTH = .005

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

    conditions = {'Conditional': (0,1)}
    conditional = random_assign(b, 'conditional', conditions)['Conditional']

    # game description page
    p = Page(b)
    Label(p, label=ipd.description(PAYOFF_MATRIX))

    # estimation pages
    game = create_game()
    for i in range(ROUNDS):
        p = Page(b, cache_compile=True)
        Compile.create_estimate_page(p, conditional, game=game)
        Submit.compute_accuracy(p, conditional, game=game)
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

@Compile.register
def create_estimate_page(page, conditional, game):
    """Create an estimation page"""
    round = game.rounds
    Label(page, label=game.html_table()) # game summary table
    Label(page, label='<p>From 0% to 100%, how likely is the following?</p>')
    if conditional:
        Range(
            page,
            var='P(C_b)_hat',
            label='<p>Blue Cooperates next round (round {}).</p>'.format(round)
        )
        Range(
            page,
            var='P(C_r|C_b)_hat',
            label='<p>Red Cooperates in two rounds (round {0}) assuming Blue Cooperates next round (round {1}).</p>'.format(round+1, round)
        )
        Range(
            page,
            var='P(C_r|D_b)_hat',
            label='<p>Red Cooperates in two rounds (round {0}) assuming Blue Defects next round (round {1}).</p>'.format(round+1, round)
        )
    else:
        Range(
            page,
            var='P(C_r)_hat',
            label='<p>Red Cooperates in two rounds (round {}).</p>'.format(round+1)
        )

@Submit.register
def compute_accuracy(page, conditional, game):
    """Play a round of the IPD

    Use embedded data to track the Red and Blue player's actions and 
    prediction accuracy using a Brier score.
    """
    ests = page.questions[-3:] if conditional else page.questions[-1:]
    [setattr(est, 'data', float(est.data)/100) for est in ests]
    if conditional:
        cr = ests[1].data * ests[0].data + ests[2].data * (1-ests[0].data)
        Embedded(page, var='P(C_r)_hat', data=cr)
    else:
        cr = ests[0].data
    true = simulate(game)
    Embedded(page, var='P(C_r)', data=true)
    Embedded(page, var='KL', data=KL(true, cr))
    game.play()

def simulate(game):
    red_coop = 0
    for i in range(SIMULATIONS):
        game.play(2)
        red_coop += int(game.actions['Red'][-1] == 'Cooperate')
        game.rewind(2)
    return red_coop / float(SIMULATIONS)

def KL(f, p):
    f, p = smooth(f), smooth(p)
    return -(f*log2(p/f) + (1-f)*log2((1-p)/(1-f)))

def smooth(p):
    return (p+SMOOTH)/(1+2*SMOOTH)