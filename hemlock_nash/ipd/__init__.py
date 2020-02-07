"""Iterated Prisoner's Dilemma"""

from hemlock_nash import Payoff, Strategy

@Payoff.register
def matrix(game, payoff_matrix):
    return payoff_matrix[tuple(p.actions[-1] for p in game.players)]

@Strategy.register
def tit_for_tat(player, first_action='Cooperate'):
    other_actions = player.game.players[1-player.index].actions
    return other_actions[-1] if other_actions else first_action

IPD_DESCRIPTION = """
<p>Imagine a game with two players represented by the colors <span style="color:red;">red</span> and <span style="color:blue;">blue.</span> Each player simultaneously chooses one of the following actions: {act0} or {act1}.</p>

<p>Players win points (payoffs) based on their actions as shown in the following table.</p>

<table class="table table-bordered text-center">
    <tr>
        <td colspan="2" rowspan="2"></td>
        <th scope="col" colspan="2" style="color:blue;">Blue Player</th>
    </tr>
    <tr>
        <th scope="col" style="color:blue;">{act0}</th>
        <th scope="col" style="color:blue;">{act1}</th>
    </tr>
    <tr>
        <th class="align-middle" scope="row" rowspan="2" style="color:red;">Red<br>Player</th>
        <th scope="row" style="color:red;">{act0}</th>
        <td><span style="color:red;">{pay_red_00}</span>, <span style="color:blue;">{pay_blue_00}</span></td>
        <td><span style="color:red;">{pay_red_01}</span>, <span style="color:blue;">{pay_blue_01}</span></td>
    </tr>
    <tr>
        <th class="text-center" scope="row" style="color:red;">{act1}</th>
        <td><span style="color:red;">{pay_red_10}</span>, <span style="color:blue;">{pay_blue_10}</span></td>
        <td><span style="color:red;">{pay_red_11}</span>, <span style="color:blue;">{pay_blue_11}</span></td>
    </tr>
</table>

<p>For example, if both players choose "{act0}", the <span style="color:red;">red player</span> wins {pay_red_00} points and the <span style="color:blue;">blue player</span> wins {pay_blue_00} points.</p>

<p>Players play multiple rounds of this game in succession. After each round, players observe the actions and payoffs resulting from that round.</p>
"""

def description(payoff_matrix):
    actions = []
    for key in payoff_matrix.keys():
        actions += list(key)
    act0, act1 = list(set(actions))
    pay_red_00, pay_blue_00 = payoff_matrix[(act0, act0)]
    pay_red_01, pay_blue_01 = payoff_matrix[(act0, act1)]
    pay_red_10, pay_blue_10 = payoff_matrix[(act1, act0)]
    pay_red_11, pay_blue_11 = payoff_matrix[(act1, act1)]
    return IPD_DESCRIPTION.format(
        act0=act0, act1=act1,
        pay_red_00=pay_red_00, pay_blue_00=pay_blue_00,
        pay_red_01=pay_red_01, pay_blue_01=pay_blue_01,
        pay_red_10=pay_red_10, pay_blue_10=pay_blue_10,
        pay_red_11=pay_red_11, pay_blue_11=pay_blue_11
    )