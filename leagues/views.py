from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from leagues.forms import UploadForm, CedhResultForm
from .models import *


class FormatsForIndex:
    format_name: str
    players: str
    prize_pool: str

    def __init__(self, format_name, prize_pool, players):
        self.format_name = str(format_name)
        self.prize_pool = str(prize_pool)
        self.players = str(players)


class StandingsResult:
    place: int

    def __init__(self, first, last, points, dci):
        self.first = first
        self.last = last
        self.points = points
        self.dci = dci

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
    def get_unique_players(event_results):
        players = {}
        for event_result in event_results:
            try:
                players[event_result.player] = True
            except KeyError:
                pass

        return list(players)
    payouts = []
    modern_event_results = EventResult.objects.filter(league__format='MOD')
    legacy_event_results = EventResult.objects.filter(league__format='LEG')
    cedh_event_results = EventResult.objects.filter(league__format='CEDH')
    if modern_event_results:
        modern = FormatsForIndex(format_name='Modern',
                             prize_pool=len(modern_event_results),
                             players=len(get_unique_players(modern_event_results)))
        payouts.append(modern)
    if legacy_event_results:
        legacy = FormatsForIndex(format_name='Legacy',
                             prize_pool=len(legacy_event_results),
                             players=len(get_unique_players(legacy_event_results)))
        payouts.append(legacy)
    if cedh_event_results:
        cedh = FormatsForIndex(format_name='Competitive EDH',
                             prize_pool=len(cedh_event_results),
                             players=len(get_unique_players(cedh_event_results)))
        payouts.append(cedh)
    context = {
        'payouts': payouts
    }
    return render(request, 'leagues/index.html', context)


def modern(request):
    player_dict = {}
    for result in EventResult.objects.filter(league__format='MOD'):
        try:
            player_dict[result.player.dci] += result.points
        except KeyError:
            player_dict[result.player.dci] = result.points

    player_list = []
    for player in player_dict.keys():
        p = Player.objects.get(dci=player)
        player_list.append(StandingsResult(first=p.first, last=p.last, points=player_dict[player], dci=player))

    player_list.sort(key=lambda player: player.points, reverse=True)
    standing = 1
    previous_standing = 1
    previous_points = None
    for player in player_list:
        if player.points == previous_points:
            player.set_place(previous_standing)
        else:
            previous_standing = standing
            player.set_place(standing)
        standing += 1
        previous_points = player.points

    context = {
        'league_name': 'Modern Standings',
        'player_list': player_list
    }
    return render(request, 'leagues/standings.html', context)


def legacy(request):
    player_dict = {}
    for result in EventResult.objects.filter(league__format='LEG'):
        try:
            player_dict[result.player.dci] += result.points
        except KeyError:
            player_dict[result.player.dci] = result.points

    player_list = []
    for player in player_dict.keys():
        p = Player.objects.get(dci=player)
        player_list.append(StandingsResult(first=p.first, last=p.last, points=player_dict[player], dci=player))

    player_list.sort(key=lambda player: player.points, reverse=True)
    standing = 1
    previous_standing = 1
    previous_points = None
    for player in player_list:
        if player.points == previous_points:
            player.set_place(previous_standing)
        else:
            previous_standing = standing
            player.set_place(standing)
        standing += 1
        previous_points = player.points

    context = {
        'league_name': 'Legacy Standings',
        'player_list': player_list
    }
    return render(request, 'leagues/standings.html', context)


def cedh(request):
    player_dict = {}
    for result in EventResult.objects.filter(league__format='CEDH'):
        try:
            player_dict[result.player.dci] += result.points
        except KeyError:
            player_dict[result.player.dci] = result.points

    player_list = []
    for player in player_dict.keys():
        p = Player.objects.get(dci=player)
        player_list.append(StandingsResult(first=p.first, last=p.last, points=player_dict[player], dci=player))

    player_list.sort(key=lambda player: player.points, reverse=True)
    standing = 1
    previous_standing = 1
    previous_points = None
    for player in player_list:
        if player.points == previous_points:
            player.set_place(previous_standing)
        else:
            previous_standing = standing
            player.set_place(standing)
        standing += 1
        previous_points = player.points

    context = {
        'league_name': 'Competitive EDH Standings',
        'player_list': player_list
    }
    return render(request, 'leagues/standings.html', context)


def user_details(request, pk):
    account = Player.objects.get(pk=pk)
    events = EventResult.objects.filter(player=account).order_by('-event__date')
    avg_wins = 0
    avg_points = 0
    legacy_wins = 0
    legacy_points = 0
    modern_wins = 0
    modern_points = 0
    for event in events:
        avg_points += event.points
        if event.event.format == "Legacy":
            legacy_points += event.points
        if event.event.format == "Modern":
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
        'avg_wins': avg_wins
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


def create_data_from_wer(xml_file, league):
    import xml.etree.ElementTree as Et
    tree = Et.parse(xml_file)
    root = tree.getroot()
    dictionary_players = {}

    for event in root:
        date = event.get('startdate')
        e, e_created = Event.objects.get_or_create(format=league.format, date=date)
        if e_created:
            e.save()
        participation = event.find('participation')
        for x in participation.findall('person'):
            dci = x.get('id')
            first = x.get('first')
            last = x.get('last')
            dictionary_players[int(dci)] = 0
            p, p_created = Player.objects.get_or_create(dci=dci, first=first, last=last)
            if p_created:
                p.save()

        matches = event.find('matches')
        for round_of_magic in matches:
            round_number = round_of_magic.get('number')
            r, r_created = Round.objects.get_or_create(round_number=round_number,
                                                     event=e)
            if r_created:
                r.save()
            for match_of_magic in round_of_magic:
                player_1 = Player.objects.get(pk=match_of_magic.get('person'))
                p2_dci = match_of_magic.get('opponent')
                if p2_dci:
                    player_2 = Player.objects.get(pk=p2_dci)
                else:
                    player_2 = None
                p1_wins = match_of_magic.get('win')
                draws = match_of_magic.get('draw')
                p2_wins = match_of_magic.get('loss')
                outcome = match_of_magic.get('outcome')
                m, m_created = Match.objects.get_or_create(player_1=player_1,
                                                           player_2=player_2,
                                                           p1_wins=p1_wins,
                                                           draws=draws,
                                                           p2_wins=p2_wins,
                                                           outcome=outcome,
                                                           round=r)
                if m_created:
                    m.save()
                if outcome is "1" or outcome is "3":
                    dictionary_players[int(player_1.dci)] += 1
                elif outcome is "2":
                    dictionary_players[int(player_2.dci)] += 1
                else:
                    print("ruh roh raggy")

        for dci, wins in dictionary_players.items():
            def calc_points(wins):
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
                return points

            player = Player.objects.get(dci=dci)
            s, created = EventResult.objects.get_or_create(player=player,
                                                           event=e,
                                                           league=league,
                                                           points=calc_points(int(wins)),
                                                           date=date)
            if created:
                s.save()


@login_required
def uploads(request):

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            create_data_from_wer(xml_file=form.cleaned_data['file'],
                                 league=form.cleaned_data['league'])
            return HttpResponseRedirect('/')

    context = {
        'upload_form': UploadForm,
        'cedh_form': CedhResultForm
    }
    return render(request, 'leagues/uploads.html', context)


@login_required
def cedh_upload(request):
    if request.method == 'POST':
        form = CedhResultForm(request.POST, request.FILES)
        if form.is_valid():
            pass

