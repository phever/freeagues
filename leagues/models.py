from django.db import models


class Player(models.Model):
    dci = models.IntegerField(primary_key=True)
    first = models.CharField(max_length=50)
    last = models.CharField(max_length=50)
    nickname = models.CharField(max_length=128, default=None, null=True)

    def __str__(self):
        return str.format("{} {} ({})", self.first, self.last, self.dci)


class EventRecord(models.Model):
    data = models.FileField()
    format = models.CharField(max_length=30)
    date = models.DateField()

    def __str__(self):
        return str.format("{} - {}", self.date.strftime("%A %B %d, %Y"), self.format)

    def save(self, *args, **kwargs):
        import xml.etree.ElementTree as Et
        super(EventRecord, self).save(self, *args, **kwargs)
        tree = Et.parse(self.data)
        root = tree.getroot()
        dictionary_players = {}

        for event in root:
            participation = event.find('participation')
            for x in participation.findall('person'):
                dci = x.get('id')
                first = x.get('first')
                last = x.get('last')
                dictionary_players[int(dci)] = 0
                p, created = Player.objects.get_or_create(dci=dci, first=first, last=last)
                if created:
                    p.save()

            matches = event.find('matches')
            for round_of_magic in matches:
                round_number = round_of_magic.get('number')
                for match_of_magic in round_of_magic:
                    player = Player.objects.get(pk=match_of_magic.get('person'))
                    opp = match_of_magic.get('opponent')
                    pwins = match_of_magic.get('win')
                    draws = match_of_magic.get('draw')
                    oppwins = match_of_magic.get('loss')
                    outcome = match_of_magic.get('outcome')
                    m, created = Match.objects.get_or_create(player=player, opp=opp, pwins=pwins, draws=draws,
                                                             oppwins=oppwins, outcome=outcome,
                                                             roundNumber=round_number,
                                                             event=self)
                    if outcome is "1" or outcome is "3":
                        dictionary_players[int(player.dci)] += 1
                    elif outcome is "2":
                        pass
                    else:
                        print("ruh roh raggy")
                    if created:
                        m.save()

        for dci, dude in dictionary_players.items():
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
            event = self
            wins = dude
            s, created = StandingsRecord.objects.get_or_create(player=player, event=event, wins=wins, points=calc_points(wins))
            if created:
                s.save()


class Match(models.Model):
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    opp = models.IntegerField(null=True)
    pwins = models.SmallIntegerField(null=True)
    draws = models.SmallIntegerField(null=True)
    oppwins = models.SmallIntegerField(null=True)
    outcome = models.SmallIntegerField()
    roundNumber = models.SmallIntegerField()
    event = models.ForeignKey(EventRecord, on_delete=models.CASCADE)

    def __str__(self):
        try:
            opplastname = Player.objects.get(pk=self.opp).last
        except Player.DoesNotExist:
            opplastname = "got a bye"
        if opplastname is "got a bye":
            return str.format("{} {} - {} {}", self.player.last, opplastname, self.event.date.strftime("%a %b %d"),
                              str(self.event.format))
        else:
            return str.format("{} vs. {} - {} {}", self.player.last, opplastname, self.event.date.strftime("%a %b %d"),
                              str(self.event.format))


class StandingsRecord(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(EventRecord, on_delete=models.CASCADE)
    wins = models.SmallIntegerField(default=0)
    points = models.SmallIntegerField(default=0)

    def __str__(self):
        return str.format("{} won {} - {}", self.player.last, self.wins, self.event.date.strftime("%b %d"))
