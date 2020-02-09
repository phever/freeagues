import datetime

from django.db import models

# Formats, with a "Code" followed by a readable name, for the CharField.choices
FORMATS = {('LEG', 'Legacy'),
           ('MOD', 'Modern'),
           ('CEDH', 'Competitive EDH'),
           ('STD', 'Standard'),
           ('PIO', 'Pioneer')}


class Player(models.Model):
    dci = models.BigIntegerField(primary_key=True)
    first = models.CharField(max_length=50, default="Blank")
    last = models.CharField(max_length=50, default="NoName")
    nickname = models.CharField(max_length=128, default=None, null=True, blank=True)

    def __str__(self):
        return str.format("{} {} ({})", self.first, self.last, self.dci)

    def name(self):
        if self.nickname:
            return str.format("{} \"{}\" {}", self.first, self.nickname, self.last)
        else:
            return str.format("{} {}", self.first, self.last)


class Event(models.Model):
    format = models.CharField(max_length=5, choices=FORMATS)
    date = models.DateField()

    def __str__(self):
        return str.format("{} - {}", self.date.strftime("%A %B %d, %Y"), self.format)


class Round(models.Model):
    round_number = models.PositiveSmallIntegerField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return str.format("Round {} of {} on {}", self.round_number, self.event.format, self.event.date)


class Match(models.Model):
    player_1 = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, blank=True, related_name='p1')
    player_2 = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, blank=True, related_name='p2')
    p1_wins = models.PositiveSmallIntegerField(null=True)
    p2_wins = models.PositiveSmallIntegerField(null=True)
    draws = models.PositiveSmallIntegerField(null=True)
    outcome = models.PositiveSmallIntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)

    def __str__(self):
        if self.player_2:
            return str.format("{} {} vs. {} {}. {} / {} / {}", self.player_1.first, self.player_1.last,
                          self.player_2.first, self.player_2.last, self.p1_wins, self.p2_wins, self.draws)
        else:
            return str.format("{} {} got a bye", self.player_1.first, self.player_1.last)


class League(models.Model):
    format = models.CharField(max_length=5, choices=FORMATS)
    date_started = models.DateField()
    number_of_events = models.PositiveSmallIntegerField()

    def __str__(self):
        end_date = self.date_started + datetime.timedelta(weeks=self.number_of_events)
        return str.format("{format} League [{date_start} to {date_end}]",
                          format=self.convert_fmt(),
                          date_start=self.date_started.strftime("%b %d %Y"),
                          date_end=end_date.strftime("%b %d %Y"))

    def convert_fmt(self):
        if self.format == 'MOD':
            return 'Modern'
        elif self.format == 'LEG':
            return 'Legacy'
        elif self.format == 'CEDH':
            return 'Competitve EDH'
        elif self.format == 'STD':
            return 'Standard'
        elif self.format == 'PIO':
            return 'Pioneer'
        else:
            return 'ERROR'

    def convert_to_url(self):
        if self.format == 'MOD':
            return '/modern'
        elif self.format == 'LEG':
            return '/legacy'
        elif self.format == 'CEDH':
            return '/cedh'
        elif self.format == 'STD':
            return '/standard'
        elif self.format == 'PIO':
            return '/pioneer'
        else:
            return '/404'

    def print_weekday(self):
        return self.date_started.strftime("%A")


class EventResult(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date = models.DateField()
    points = models.PositiveSmallIntegerField(default=0)
    wins = models.PositiveSmallIntegerField(default=0)
    losses = models.PositiveSmallIntegerField(default=0)
    draws = models.PositiveSmallIntegerField(default=0)
    standing = models.IntegerField(default=0)
    was_here = models.BooleanField(default=True)

    def __str__(self):
        return str.format("{name} went {wins} / {losses} / {draws} on {day} in {format}",
                          name=self.player.name(),
                          format=self.league.convert_fmt(),
                          day=self.date.strftime("%b %d"),
                          wins=self.wins,
                          losses=self.losses,
                          draws=self.draws)


class CedhResult(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    date = models.DateField(default='2019-01-31')
    points = models.PositiveSmallIntegerField(default=0)
    played_both = models.BooleanField(default=True)
    standing = models.IntegerField(default=0)
    was_here = models.BooleanField(default=True)

    def __str__(self):
        return str.format("{} {} on {} got {} points.", self.player.first, self.player.last, self.date, self.points)
