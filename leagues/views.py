from django.shortcuts import render

from .models import *


class StandingsResult:
    def __init__(self, first, last, nickname, wins, place, dci):
        self.first = first
        self.last = last
        self.nickname = nickname
        self.points = 0
        self.add_points(wins)
        self.place = place
        self.dci = dci

    def add_points(self, wins):
        if wins < 2:
            points = 1
        elif wins == 2:
            points = 2
        elif wins == 3:
            points = 4
        elif wins == 4:
            points = 6
        else:
            points = 99999
        self.points += points

    def set_place(self, place):
        self.place = place


class EventRound:
    def __init__(self, round_number, player, opp, opp_name, wins, draws, losses):
        self.roundNumber = round_number
        self.player = player
        self.opp = opp
        self.opp_name = opp_name
        self.wins = wins
        self.draws = draws
        self.losses = losses

        if wins > losses:
            self.result = "Wins"
        elif wins < losses:
            self.result = "Loss"
        else:
            self.result = "Draw"


def index(request):
    modern_standings = StandingsRecord.objects.filter(event__format="Modern")
    legacy_standings = StandingsRecord.objects.filter(event__format="Legacy")
    modern_players = {}
    legacy_players = {}
    for standing in legacy_standings:
        try:
            legacy_players[standing.player.dci] = True
        except KeyError:
            pass
    for standing in modern_standings:
        try:
            modern_players[standing.player.dci] = True
        except KeyError:
            pass
    legacy_players = len(legacy_players)
    modern_players = len(modern_players)
    legacy_pool = len(legacy_standings)
    modern_pool = len(modern_standings)
    context = {
        'modern_players': modern_players,
        'legacy_players': legacy_players,
        'modpool': modern_pool,
        'legpool': legacy_pool
    }
    return render(request, 'leagues/index.html', context)


def modern(request):
    player_list = {}
    for player in StandingsRecord.objects.filter(event__format="Modern"):
        try:
            player_list[player.player.dci].add_points(player.wins)
        except KeyError:
            player_list[player.player.dci] = StandingsResult(player.player.first, player.player.last,
                                                             player.player.nickname, player.wins, 0, player.player.dci)

    player_list = sorted(player_list.values(),
                         key=lambda player: player.points, reverse=True)
    i = 0
    for player in player_list[:]:
        i += 1
        player.set_place(i)
    context = {
        'player_list': player_list
    }
    return render(request, 'leagues/modern.html', context)


def legacy(request):
    player_list = {}
    for player in StandingsRecord.objects.filter(event__format="Legacy"):
        try:
            player_list[player.player.dci].add_points(player.wins)
        except KeyError:
            player_list[player.player.dci] = StandingsResult(player.player.first, player.player.last,
                                                             player.player.nickname, player.wins, 0, player.player.dci)

    player_list = sorted(player_list.values(),
                             key=lambda player: player.points, reverse=True)
    i = 0
    for player in player_list[:]:
        i += 1
        player.set_place(i)
    context = {
        'player_list': player_list
    }
    return render(request, 'leagues/legacy.html', context)


def user_details(request, pk):
    account = Player.objects.get(pk=pk)
    events = StandingsRecord.objects.filter(player=account).order_by('-event__date')
    avg_wins = 0
    avg_points = 0
    legacy_wins = 0
    legacy_points = 0
    modern_wins = 0
    modern_points = 0
    for event in events:
        avg_wins += event.wins
        avg_points += event.points
        if event.event.format == "Legacy":
            legacy_wins += event.wins
            legacy_points += event.points
        if event.event.format == "Modern":
            modern_wins += event.wins
            modern_points += event.points
    if legacy_points > 0:
        legacy_points = legacy_points / len(events.filter(event__format="Legacy"))
    if modern_points > 0:
        modern_points = modern_points / len(events.filter(event__format="Modern"))
    avg_points = avg_points / len(events)
    context = {
        'account': account,
        'events': events,
        'avg_points': avg_points,
        'legacy_points': legacy_points,
        'modern_points': modern_points,
        'avg_wins': avg_wins,
        'legacy_wins': legacy_wins,
        'modern_wins': modern_wins,
    }
    return render(request, 'leagues/user_details.html', context)


def event_details(request, pk, event):
    def getPoints():
        events = StandingsRecord.objects.filter(player=account).order_by('-event__date')
        points = 0
        for x in events:
            if event.format == "Legacy" and x.event.format == "Legacy":
                points += x.points
            if event.format == "Modern" and x.event.format == "Modern":
                points += x.points
        return points

    rounds = {}
    account = Player.objects.get(pk=pk)
    event = EventRecord.objects.get(pk=event)
    matches = Match.objects.filter(event=event, player=account) | Match.objects.filter(event=event, opp=int(account.dci))
    matches = sorted(matches, key=lambda match: match.roundNumber)

    for match in matches:
        round_number = match.roundNumber
        player = account
        opp = match.opp
        if account.dci == opp:  # check to see if you're the opp!
            opp = match.player.dci
            wins = match.oppwins
            losses = match.pwins
        else:
            wins = match.pwins
            losses = match.oppwins
        draws = match.draws
        if opp is None:  # is it a Bye?
            opp_name = "Bye"
            wins = 1
            losses = 0
            draws = 0
        else:
            opp_name = str.format("{} {}", Player.objects.get(dci=opp).first, Player.objects.get(dci=opp).last)
        rounds[round_number] = EventRound(round_number, player, opp, opp_name, wins, draws, losses)

    context = {
        'account': account,
        'event': event,
        'rounds': rounds.values(),
        'league_points': getPoints(),
        'result': StandingsRecord.objects.get(event=event, player=account)
    }
    return render(request, 'leagues/personal_event.html', context)
