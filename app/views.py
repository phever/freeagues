from typing import Dict

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from .forms import *
from .models import *


class FormatsForIndex:
    format_name: str
    players: str
    prize_pool: str

    def __init__(self, format_name, prize_pool, players):
        self.format_name = format_name
        self.prize_pool = str(prize_pool)
        self.players = str(players)


class StandingsResult:
    most_recent_standing: int
    standing: int
    nickname: str
    ranking_moved: int  # no change = 0, up = 1, down = -1
    weeks_points: int
    points: int

    def __init__(self, first, last, dci, nickname):
        self.first = first
        self.last = last
        self.dci = dci
        self.nickname = nickname
        self.ranking_moved = None


def get_links():
    links = []
    old_leagues = False

    class Link:
        def __init__(self, friendly_name, url):
            self.friendly_name = friendly_name
            self.url = url

    all_leagues = League.objects.all()
    today = datetime.date.today()
    for league in all_leagues:
        date_ended = league.date_started + datetime.timedelta(days=league.number_of_events * 7)
        # currently running league
        if date_ended >= today >= league.date_started:
            links.append(Link(league.convert_fmt(), league.convert_to_url()))

        # past league
        elif date_ended < today:
            old_leagues = True

        # future league
        else:
            pass

    if old_leagues:
        links.append(Link('OLD LEAGUES', '/old-leagues'))

    return links


def get_standings(league: League):
    list_of_results = EventResult.objects.filter(league=league).order_by('-date')

    player_dict: Dict[int, StandingsResult] = {}
    for standing in list_of_results:
        try:  # result has been created, add to totals
            player_dict[standing.player.dci].points += standing.points
            old_standing = standing.standing
            if player_dict[standing.player.dci].ranking_moved is None:
                if old_standing > player_dict[standing.player.dci].standing:
                    player_dict[standing.player.dci].ranking_moved = 1
                elif old_standing < player_dict[standing.player.dci].standing:
                    player_dict[standing.player.dci].ranking_moved = -1
                elif old_standing == player_dict[standing.player.dci].standing:
                    player_dict[standing.player.dci].ranking_moved = 0

        except KeyError:  # Most recent result, create a new one
            sr = StandingsResult(first=standing.player.first,
                                 last=standing.player.last,
                                 dci=standing.player.dci,
                                 nickname=standing.player.nickname)
            sr.standing = standing.standing
            sr.most_recent_standing = standing.standing
            sr.points = standing.points
            sr.weeks_points = standing.points
            player_dict[standing.player.dci] = sr

    return sorted(player_dict.values(), key=lambda result: result.standing, reverse=False)


def get_league_badge(current_player, format):
    class FormatBadge:
        name: str
        ranking: int
        points: int

    if format == 'CEDH':
        points = 0
        my_events = CedhResult.objects.filter(player=current_player, league__format=format)
        for event in my_events:
            points += event.points
        recent_event = my_events.order_by('-date').first()
        standing = recent_event.standing
    else:
        points = 0
        my_events = EventResult.objects.filter(player=current_player, league__format=format)
        for event in my_events:
            points += event.points
        recent_event = my_events.order_by('-date').first()
        standing = recent_event.standing

    fb = FormatBadge()
    fb.name = current_player.name()
    fb.ranking = standing
    fb.points = points
    return fb


def get_sixty_card_event_cards(my_events):
    def convert_fmt(fmt):
        if fmt == 'MOD':
            return 'Modern'
        elif fmt == 'LEG':
            return 'Legacy'
        elif fmt == 'CEDH':
            return 'Competitve EDH'
        elif fmt == 'PIO':
            return 'Pioneer'
        else:
            return 'ERROR'

    class EventCard:
        format: str
        date: str
        wins = 0
        losses = 0
        draws = 0

    events = []
    for event in my_events:
        ec = EventCard()
        ec.format = convert_fmt(event.league.format)
        ec.date = event.date
        ec.points = event.points
        ec.wins = event.wins
        ec.losses = event.losses
        ec.draws = event.draws
        ec.id = event.pk
        events.append(ec)
    return events


def get_cedh_event_cards(my_cedh_events):
    def convert_fmt(fmt):
        if fmt == 'MOD':
            return 'Modern'
        elif fmt == 'LEG':
            return 'Legacy'
        elif fmt == 'CEDH':
            return 'Competitive EDH'
        elif fmt == 'PIO':
            return 'Pioneer'
        else:
            return 'ERROR'

    class EventCard:
        format: str
        date: str
        points: int

    events = []
    for event in my_cedh_events:
        ec = EventCard()
        ec.format = convert_fmt(event.league.format)
        ec.date = event.date
        ec.points = event.points
        ec.played_both = event.played_both
        ec.id = event.pk
        events.append(ec)
    return events


def index_view(request):
    def get_unique_players(event_results):
        players = {}
        for event_result in event_results:
            try:
                players[event_result.player] = True
            except KeyError:
                pass

        return list(players)

    running_leagues = []
    old_leagues = []
    future_leagues = []
    all_leagues = League.objects.all()
    today = datetime.date.today()
    for league in all_leagues:
        date_ended = league.date_started + datetime.timedelta(days=league.number_of_events * 7)
        if date_ended >= today >= league.date_started:
            running_leagues.append(league)
        elif date_ended < today:
            old_leagues.append(league)
        else:
            future_leagues.append(league)

    payouts = []
    for league in running_leagues:
        if league.format == 'CEDH':
            event_results = CedhResult.objects.filter(league=league, was_here=True)
        else:
            event_results = EventResult.objects.filter(league=league, was_here=True)

        if event_results:
            f = FormatsForIndex(format_name=league.convert_fmt(), prize_pool=len(event_results),
                                players=len(get_unique_players(event_results)))
            payouts.append(f)

    context = {
        'running_leagues': running_leagues,
        'old_leagues': old_leagues,
        'future_leagues': future_leagues,
        'payouts': payouts,
        'links': get_links()
    }
    return render(request, 'leagues/index.html', context)


def modern_view(request):
    league = League.objects.filter(format='MOD').order_by('-date_started').first()
    # add if league.date + league.number_of_events to see if it's currently ongoing
    player_list = get_standings(league)

    context = {
        'league_name': 'Modern Standings',
        'player_list': player_list,
        'links': get_links()
    }
    return render(request, 'leagues/standings.html', context)


def old_modern_view(request, pk):
    league = get_object_or_404(League, pk=pk)
    player_list = get_standings(league)

    context = {
        'league_name': 'Modern Standings',
        'player_list': player_list,
        'links': get_links()
    }
    return render(request, 'leagues/standings.html', context)


def legacy_view(request):
    league = League.objects.filter(format='LEG').order_by('-date_started').first()
    # add if league.date + league.number_of_events to see if it's currently ongoing
    player_list = get_standings(league)

    context = {
        'league_name': 'Legacy Standings',
        'player_list': player_list,
        'links': get_links()
    }
    return render(request, 'leagues/standings.html', context)


def old_legacy_view(request, pk):
    league = get_object_or_404(League, pk=pk)
    player_list = get_standings(league)

    context = {
        'league_name': 'Legacy Standings',
        'player_list': player_list,
        'links': get_links()
    }
    return render(request, 'leagues/standings.html', context)


def standard_view(request):
    league = League.objects.filter(format='STD').order_by('-date_started').first()
    # add if league.date + league.number_of_events to see if it's currently ongoing
    player_list = get_standings(league)

    context = {
        'league_name': 'Standard Standings',
        'player_list': player_list,
        'links': get_links()
    }
    return render(request, 'leagues/standings.html', context)


def old_standard_view(request, pk):
    league = get_object_or_404(League, pk=pk)
    player_list = get_standings(league)

    context = {
        'league_name': 'Standard Standings',
        'player_list': player_list,
        'links': get_links()
    }
    return render(request, 'leagues/standings.html', context)


def pioneer_view(request):
    league = League.objects.filter(format='PIO').order_by('-date_started').first()
    # add if league.date + league.number_of_events to see if it's currently ongoing
    player_list = get_standings(league)

    context = {
        'league_name': 'Pioneer Standings',
        'player_list': player_list,
        'links': get_links()
    }
    return render(request, 'leagues/standings.html', context)


def old_pioneer_view(request, pk):
    league = get_object_or_404(League, pk=pk)
    player_list = get_standings(league)

    context = {
        'league_name': 'Pioneer Standings',
        'player_list': player_list,
        'links': get_links()
    }
    return render(request, 'leagues/standings.html', context)


def cedh_view(request):
    player_dict = {}
    for result in CedhResult.objects.filter(
            league=League.objects.filter(format='CEDH').order_by('-date_started').first()):
        try:
            player_dict[result.player.dci] += result.points
        except KeyError:
            player_dict[result.player.dci] = result.points

    player_list = []
    for player in player_dict.keys():
        p = Player.objects.get(dci=player)
        sr = StandingsResult(first=p.first, last=p.last, dci=player, nickname=p.nickname)
        sr.points = player_dict[player]
        player_list.append(sr)

    player_list.sort(key=lambda player: player.points, reverse=True)
    standing = 1
    previous_standing = 1
    previous_points = None
    for player in player_list:
        if player.points == previous_points:
            player.standing = previous_standing
        else:
            previous_standing = standing
            player.standing = standing
        standing += 1
        previous_points = player.points

    context = {
        'league_name': 'Competitive EDH Standings',
        'player_list': player_list,
        'links': get_links()
    }
    return render(request, 'leagues/standings.html', context)


def old_cedh_view(request, pk):
    player_dict = {}
    for result in CedhResult.objects.filter(league__pk=pk):
        try:
            player_dict[result.player.dci] += result.points
        except KeyError:
            player_dict[result.player.dci] = result.points

    player_list = []
    for player in player_dict.keys():
        p = Player.objects.get(dci=player)
        sr = StandingsResult(first=p.first, last=p.last, dci=player, nickname=p.nickname)
        sr.points = player_dict[player]
        player_list.append(sr)

    player_list.sort(key=lambda player: player.points, reverse=True)
    standing = 1
    previous_standing = 1
    previous_points = None
    for player in player_list:
        if player.points == previous_points:
            player.standing = previous_standing
        else:
            previous_standing = standing
            player.standing = standing
        standing += 1
        previous_points = player.points

    context = {
        'league_name': 'Competitive EDH Standings',
        'player_list': player_list,
        'links': get_links()
    }
    return render(request, 'leagues/standings.html', context)


def player_details_view(request, pk):
    account = Player.objects.get(dci=pk)
    events = []

    my_modern_events = EventResult.objects.filter(player=account, league__format='MOD', was_here=True).order_by(
        '-event__date')
    if my_modern_events:
        modern_fb = get_league_badge(account, 'MOD')
        events.extend(get_sixty_card_event_cards(my_modern_events))
    else:
        modern_fb = None

    my_legacy_events = EventResult.objects.filter(player=account, league__format='LEG', was_here=True).order_by(
        '-event__date')
    if my_legacy_events:
        legacy_fb = get_league_badge(account, 'LEG')
        events.extend(get_sixty_card_event_cards(my_legacy_events))
    else:
        legacy_fb = None

    my_pioneer_events = EventResult.objects.filter(player=account, league__format='PIO', was_here=True).order_by(
        '-event__date')
    if my_pioneer_events:
        pioneer_fb = get_league_badge(account, 'PIO')
        events.extend(get_sixty_card_event_cards(my_pioneer_events))
    else:
        pioneer_fb = None

    my_cedh_events = CedhResult.objects.filter(player=account, was_here=True).order_by('-date')
    if my_cedh_events:
        cedh_fb = get_league_badge(account, 'CEDH')
        events.extend(get_cedh_event_cards(my_cedh_events))
    else:
        cedh_fb = None

    context = {
        'player': account,
        'legacy_view': legacy_fb,
        'modern_view': modern_fb,
        'cedh_view': cedh_fb,
        'pioneer_view': pioneer_fb,
        'events': events,
        'links': get_links()
    }
    return render(request, 'leagues/player.html', context)


def create_data_from_wer(xml_file, league):
    import xml.etree.ElementTree as Et
    tree = Et.parse(xml_file)
    root = tree.getroot()
    dictionary_wins = {}
    dictionary_losses = {}
    dictionary_draws = {}

    for event in root:
        date = event.get('startdate')
        e, e_created = Event.objects.get_or_create(format=league.format, date=datetime.date.fromisoformat(date))
        if e_created:
            e.save()
        participation = event.find('participation')
        for x in participation.findall('person'):
            dci = x.get('id')
            first = x.get('first')
            last = x.get('last')
            dictionary_wins[int(dci)] = 0
            dictionary_losses[int(dci)] = 0
            dictionary_draws[int(dci)] = 0
            p, p_created = Player.objects.get_or_create(dci=dci)
            if p_created:
                p.first = first
                p.last = last
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
                if outcome is "1" or outcome is "3":  # win or bye
                    dictionary_wins[int(player_1.dci)] += 1
                    if player_2:
                        dictionary_losses[int(player_2.dci)] += 1
                elif outcome is "2":  # draw
                    dictionary_draws[int(player_1.dci)] += 1
                    dictionary_draws[int(player_2.dci)] += 1
                else:  # 5 is a given loss/not here yet, not sure on 4
                    pass

        for dci, wins in dictionary_wins.items():
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
                    points = 99999  # if it breaks, someone gets a lot of points
                return points

            player = Player.objects.get(dci=dci)
            s, created = EventResult.objects.get_or_create(player=player,
                                                           event=e,
                                                           league=league,
                                                           points=calc_points(int(wins)),
                                                           date=date,
                                                           wins=wins,
                                                           losses=dictionary_losses.get(dci, 0),
                                                           draws=dictionary_draws.get(dci, 0))
            if created:
                s.save()


def set_most_recent_event_standings(league: League):
    results = EventResult.objects.filter(league=league)
    players_overall_standing = {}
    for result in results:
        try:
            players_overall_standing[result.player.dci] += result.points
        except KeyError:
            players_overall_standing[result.player.dci] = result.points

    sorted_players = sorted(players_overall_standing.items(), key=lambda p: p[1], reverse=True)
    standing = 1
    previous_standing = 1
    previous_points = None

    most_recent_event = Event.objects.filter(format=league.format).order_by('-date').first()

    for dci, points in sorted_players:
        if points == previous_points:
            try:
                result = EventResult.objects.get(player__dci=dci, event=most_recent_event)
                result.standing = previous_standing
                result.save()
            except ObjectDoesNotExist:
                EventResult.objects.create(league=league,
                                           player=Player.objects.get(dci=dci),
                                           date=most_recent_event.date,
                                           was_here=False,
                                           standing=previous_standing,
                                           event=most_recent_event
                                           )
        else:
            previous_standing = standing
            try:
                result = EventResult.objects.get(player__dci=dci, event=most_recent_event)
                result.standing = standing
                result.save()
            except ObjectDoesNotExist:
                EventResult.objects.create(league=league,
                                           player=Player.objects.get(dci=dci),
                                           date=most_recent_event.date,
                                           was_here=False,
                                           standing=standing,
                                           event=most_recent_event
                                           )
        standing += 1
        previous_points = points


@login_required
def uploads_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            create_data_from_wer(xml_file=form.cleaned_data['file'],
                                 league=form.cleaned_data['league'])
            set_most_recent_event_standings(league=form.cleaned_data['league'])
            return HttpResponseRedirect('/')

    upload_form = UploadForm()
    cedh_form = CedhResultForm()
    cedh_form.fields['league'].queryset = League.objects.filter(format='CEDH')

    context = {
        'upload_form': upload_form,
        'cedh_form': cedh_form,
        'player_form': PlayerForm,
        'new_league_form': NewLeagueForm,
        'links': get_links()
    }
    return render(request, 'leagues/uploads.html', context)


def cedh_refresh_standings(league, date):
    cedh_results = CedhResult.objects.filter(league=league)
    players_overall_standing = {}
    for result in cedh_results:
        try:
            players_overall_standing[result.player.dci] += result.points
        except KeyError:
            players_overall_standing[result.player.dci] = result.points

    sorted_players = sorted(players_overall_standing.items(), key=lambda p: p[1], reverse=True)
    standing = 1
    previous_standing = 1
    previous_points = None

    for dci, points in sorted_players:
        if points == previous_points:
            try:
                result = CedhResult.objects.get(player__dci=dci, date=date)
                result.standing = previous_standing
                result.save()
            except ObjectDoesNotExist:
                CedhResult.objects.create(league=league,
                                          player=Player.objects.get(dci=dci),
                                          date=date,
                                          was_here=False,
                                          standing=previous_standing
                                          )
        else:
            previous_standing = standing
            try:
                result = CedhResult.objects.get(player__dci=dci, date=date)
                result.standing = standing
                result.save()
            except ObjectDoesNotExist:
                CedhResult.objects.create(league=league,
                                          player=Player.objects.get(dci=dci),
                                          date=date,
                                          was_here=False,
                                          standing=previous_standing
                                          )
        standing += 1
        previous_points = points


@login_required
def cedh_upload_view(request):
    if request.method == 'POST':
        form = CedhResultForm(request.POST, request.FILES)
        if form.is_valid():
            league = form.cleaned_data['league']
            player = form.cleaned_data['player']
            date = form.cleaned_data['date']
            points = form.cleaned_data['points']
            p, created = CedhResult.objects.get_or_create(league=league,
                                                          player=player,
                                                          date=date,
                                                          points=points)
            if created:
                p.save()
                cedh_refresh_standings(league=league, date=date)
                return HttpResponseRedirect('/uploads')

    return HttpResponseRedirect('/')


@login_required
def player_upload_view(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST, request.FILES)
        if form.is_valid():
            dci = form.cleaned_data['dci']
            first = form.cleaned_data['first']
            last = form.cleaned_data['last']
            nickname = form.cleaned_data['nickname']
            p, created = Player.objects.get_or_create(dci=dci,
                                                      first=first,
                                                      last=last,
                                                      nickname=nickname)
            if created:
                p.save()
                return HttpResponseRedirect('/uploads')

    return HttpResponseRedirect('/')


@login_required
def new_league_upload_view(request):
    if request.method == 'POST':
        form = NewLeagueForm(request.POST)
        if form.is_valid():
            form.save(commit=True)

    return HttpResponseRedirect('/')


def sixty_personal_event_view(request, pk, event):
    player = get_object_or_404(Player, dci=pk)
    event_result = get_object_or_404(EventResult, pk=event)
    matches = []
    for round_of_magic in Round.objects.filter(event=event_result.event):
        try:
            match = Match.objects.get(player_1=pk, round=round_of_magic)
            matches.append(match)
        except ObjectDoesNotExist:
            try:
                match = Match.objects.get(player_2=pk, round=round_of_magic)
                matches.append(match)
            except ObjectDoesNotExist:
                pass
    context = {
        'event': event_result,
        'player': player,
        'matches': matches,
        'links': get_links()
    }
    return render(request, 'leagues/personal_event.html', context)


def full_event_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    context = {
        'event': event,
        'links': get_links()
    }
    return render(request, 'leagues/event.html', context)


def old_league_view(request):
    old_leagues = []
    all_leagues = League.objects.filter()
    today = datetime.date.today()
    for league in all_leagues:
        date_ended = league.date_started + datetime.timedelta(days=league.number_of_events * 7)
        if date_ended < today:
            old_leagues.append(league)

    context = {
        'old_leagues': old_leagues,
        'links': get_links()
    }
    return render(request, 'leagues/old_events.html', context)
