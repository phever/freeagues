from django.db import models

# Formats, with a "Code" followed by a readable name, for the CharField.choices
FORMATS = {('LEG', 'Legacy'),
           ('MOD', 'Modern'),
           ('CEDH', 'Competitive EDH')}


class Player(models.Model):
    dci = models.IntegerField(primary_key=True)
    first = models.CharField(max_length=50)
    last = models.CharField(max_length=50)
    nickname = models.CharField(max_length=128, default=None, null=True)

    def __str__(self):
        return str.format("{} {} ({})", self.first, self.last, self.dci)

    def name(self):
        return str.format("{} {}", self.first, self.last)


class Event(models.Model):
    format = models.CharField(max_length=5, choices=FORMATS)
    date = models.DateField()

    def __str__(self):
        return str.format("{} - {}", self.date.strftime("%A %B %d, %Y"), self.format)


class Round(models.Model):
    round_number = models.PositiveSmallIntegerField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


class Match(models.Model):
    player_1 = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, blank=True, related_name='p1')
    player_2 = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, blank=True, related_name='p2')
    p1_wins = models.PositiveSmallIntegerField(null=True)
    p2_wins = models.PositiveSmallIntegerField(null=True)
    draws = models.PositiveSmallIntegerField(null=True)
    outcome = models.PositiveSmallIntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)


class League(models.Model):
    format = models.CharField(max_length=5, choices=FORMATS)
    date_started = models.DateField()
    number_of_events = models.PositiveSmallIntegerField()

    def __str__(self):
        return str.format("{format} League - {date}",
                          format=self.format,
                          date=self.date_started.strftime("%b %d %Y"))


class EventResult(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date = models.DateField()
    points = models.PositiveSmallIntegerField(default=0)


class CedhResult(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    date = models.DateField()
    points = models.PositiveSmallIntegerField()
