"""Hemlock extension for games"""

from hemlock import Settings
from hemlock.app import db
from hemlock.database import Base
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy_function import FunctionMixin
from sqlalchemy_mutable import MutableListType

import os

DIR = os.path.dirname(os.path.realpath(__file__))

def read_file(filename):
    return open(os.path.join(DIR, filename)).read()


class Game(Base, db.Model):
    """Game model

    A `Game` contains a list of `Player`s and a `Payoff` function. The game 
    is played for a number of `rounds`. Each round, players choose an 
    `action` as the output of their `Strategy` function. The payoff 
    function then returns a list of payoffs, where payoffs are ordered by 
    player index.

    Games display players' actions, stage payoffs, and cumulative payoffs 
    with the `html_table` method.
    """
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    rounds = db.Column(db.Integer)

    players = db.relationship(
        'Player',
        backref='game',
        order_by='Player.index',
        collection_class=ordering_list('index')
    )
    
    payoff_function = db.relationship(
        'Payoff',
        backref='game',
        uselist=False
    )
    
    @property
    def actions(self):
        return {p.name: p.actions for p in self.players}

    @property
    def payoffs(self):
        return {p.name: p.payoffs for p in self.players}

    @property
    def cum_payoffs(self):
        return {p.name: p.cum_payoffs for p in self.players}

    @Base.init('Game')
    def __init__(self, *args, **kwargs):
        self.rounds = 0
        super().__init__()
        return kwargs

    def play(self, rounds=1):
        [self._play() for i in range(rounds)]

    def _play(self):
        actions = [p.strategy() for p in self.players]
        [p.actions.append(a) for p, a in zip(self.players, actions)]
        payoffs = self.payoff_function()
        for p in self.players:
            payoff = payoffs[p.index]
            p.payoffs.append(payoff)
            cum_payoff = p.cum_payoffs[-1] if p.cum_payoffs else 0
            p.cum_payoffs.append(cum_payoff + payoff)
        self.rounds += 1

    def rewind(self, rounds=1):
        [p.rewind(rounds) for p in self.players]
        self.rounds -= rounds
    
    def html_table(self, rounds=None):
        self._table_rounds = rounds or self.rounds
        game_table = read_file('game_table.html')
        return game_table.format(game=self)

    @property
    def _players(self):
        player_col = read_file('player_col.html')
        return ''.join([player_col.format(name=p.name) for p in self.players])
    
    @property
    def _stats_header(self):
        stats_header = read_file('stats_header.html')
        return ''.join([stats_header for i in self.players])

    @property
    def _stats(self):
        round_stats = read_file('round_stats.html')
        stats = ''
        for i in range(self._table_rounds):
            self._round = i
            stats += round_stats.format(game=self)
        return stats

    @property
    def _player_stats(self):
        player_stats = read_file('player_stats.html')
        return ''.join([
            player_stats.format(
                action=p.actions[self._round],
                payoff=p.payoffs[self._round],
                cum_payoff=p.cum_payoffs[self._round]
            ) 
            for p in self.players
        ])


class Player(Base, db.Model):
    """Player model

    Players relate to a `Strategy` function, which is called each round by 
    the `Game` to output an `action`.
    """
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    strategy = db.relationship(
        'Strategy', 
        backref='player',
        uselist=False
    )

    index = db.Column(db.Integer)
    name = db.Column(db.String)
    actions = db.Column(MutableListType)
    payoffs = db.Column(MutableListType)
    cum_payoffs = db.Column(MutableListType)    

    @Base.init('Player')
    def __init__(self, game=None, *args, **kwargs):
        self.actions, self.payoffs, self.cum_payoffs = [], [], []
        super().__init__()
        return {'game': game, **kwargs}

    def rewind(self, rounds=1):
        del self.actions[-rounds:]
        del self.payoffs[-rounds:]
        del self.cum_payoffs[-rounds:]


class Strategy(FunctionMixin, Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))

    @property
    def parent(self):
        return self.player

    @parent.setter
    def parent(self, player):
        self.player = player

    @Base.init('Strategy')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Payoff(FunctionMixin, Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    @property
    def parent(self):
        return self.game

    @parent.setter
    def parent(self, game):
        self.game = game

    @Base.init('Payoff')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)