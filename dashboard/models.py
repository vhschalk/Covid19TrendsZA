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

    Date = models.DateField()
    Var = models.CharField(max_length = 1 , choices = Vars.choices)
    EC = models.IntegerField(null=True)
    FS = models.IntegerField(null=True)
    GP = models.IntegerField(null=True)
    KZN = models.IntegerField(null=True)
    LP = models.IntegerField(null=True)
    MP = models.IntegerField(null=True)
    NC = models.IntegerField(null=True)
    NW = models.IntegerField(null=True)
    WC = models.IntegerField(null=True)
    Unknown = models.IntegerField(null=True)
    Total = models.IntegerField()
    Source = models.CharField(max_length = 200)

class ReproductionNum(models.Model):

    Date = models.DateField()
    Var = models.IntegerField()
    Province = models.CharField(max_length = 20, null=True)
    Rt = models.DecimalField(decimal_places = 3, max_digits = 5)
    High = models.DecimalField(decimal_places = 3, max_digits = 5) # high confidence interval
    Low = models.DecimalField(decimal_places = 3, max_digits = 5) # low confidence interval
    Infect = models.DecimalField(decimal_places = 3, max_digits = 10, null=True) # infections
    Adj = models.DecimalField(decimal_places = 3, max_digits = 10, null=True) # adjusted positives

class LatestUpdate(models.Model):
    
    class Vars(models.TextChoices):
        CASES = 'C'
        ACTIVE = 'A'
        RECOVERY = 'R'
        DEATHS = 'D'
        TESTS = 'T'
        RT1 = '1'
        RT2 = '2'

    Var = models.CharField(
        max_length = 1,
        choices = Vars.choices,
        primary_key = True
    )
    Date = models.DateField()
