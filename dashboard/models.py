from django.db import models
from django.conf import settings
from django.utils import timezone

class CovidData(models.Model):

    class Vars(models.TextChoices):
        CASES = 'C'
        ACTIVE = 'A'
        RECOVERY = 'R'
        DEATHS = 'D'
        TESTS = 'T'

    date = models.DateField()
    var = models.CharField(
        max_length=1,
        choices=Vars.choices
    )
    ec = models.IntegerField()
    fs = models.IntegerField()
    gp = models.IntegerField()
    kzn = models.IntegerField()
    lp = models.IntegerField()
    mp = models.IntegerField()
    nc = models.IntegerField()
    nw = models.IntegerField()
    wc = models.IntegerField()
    unknown = models.IntegerField()
    total = models.IntegerField()
    source = models.CharField(max_length=200)

class ReproductionNum(models.Model):
    #Date	Rt	High_80	Low_80	Infections	Adjusted_Postive
    version = models.IntegerField()
    date = models.DateField()
    state = models.CharField(max_length=20)
    rt = models.DecimalField(decimal_places=3, max_digits=5)
    high = models.IntegerField() # high confidence interval
    low = models.IntegerField() # low confidence interval
    infect = models.IntegerField(null=True) # infections
    adj = models.IntegerField(null=True) # adjusted positives