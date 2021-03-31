from django.db import models
from django import forms


# Create your models here.

class Contact(models.Model):
    name=models.CharField(max_length=122)
    email=models.CharField(max_length=122)
    desc=models.TextField(max_length=122)
    date=models.DateField()

    def __str__(self):
        return self.name


class FreeboardConstructionCost(models.Model):
    address=models.CharField(max_length=100)
    street=models.CharField(max_length=200)
    floodzone=models.CharField(max_length=100)
    parish=models.CharField(max_length=100)
    no_floors=models.CharField(max_length=10)

    # class Meta:
    #        ordering = ('address',)
    
    def __str__(self):
        return self.address+" , "+self.street



class Sampledata(models.Model):
    address=models.CharField(max_length=100)
    street=models.CharField(max_length=200)
    floodzone=models.CharField(max_length=100)
    parish=models.CharField(max_length=100)
    no_floors=models.CharField(max_length=10)

    # class Meta:
    #        ordering = ('address',)
    
    def __str__(self):
        return self.address+" , "+self.street        

class Sample(models.Model):
    FID_1=models.CharField(max_length=10)
    BLDG_ID= models.CharField(max_length=10)
    HEIGHT= models.CharField(max_length=10)
    FOOTPRINT= models.CharField(max_length=30)            ##FOOTPRINT_
    address=models.CharField(max_length=100)              ##ADDRESS
    street=models.CharField(max_length=200)               ##STREET
    no_floors=models.CharField(max_length=10)             ##NO_FLOORS
    DATA_YEAR= models.CharField(max_length=10)
    SFT= models.CharField(max_length=10)
    Area_SqMet= models.CharField(max_length=30)
    FloodDepth10Year= models.CharField(max_length=10)
    FloodDepth50Year= models.CharField(max_length=10)
    FloodDepth100Year= models.CharField(max_length=10)
    FloodDepth500Year= models.CharField(max_length=10)
    ElevationUSGS2017= models.CharField(max_length=30)
    Elevation_Jefferson= models.CharField(max_length=30)
    Elevatio_2019USGS= models.CharField(max_length=30)
    parish=models.CharField(max_length=100)                   ##Name
    floodzone=models.CharField(max_length=100)                ##Zone
    Source= models.CharField(max_length=10)
    u_intercept= models.CharField(max_length=30)
    a_slope= models.CharField(max_length=30)
    

    
    def __str__(self):
        return self.address+" , "+self.street                


class dataAll(models.Model):
    FID_1=models.CharField(max_length=10)
    BLDG_ID= models.CharField(max_length=10)
    HEIGHT= models.CharField(max_length=10)
    FOOTPRINT= models.CharField(max_length=30)            ##FOOTPRINT_
    address=models.CharField(max_length=100)              ##ADDRESS
    street=models.CharField(max_length=200)               ##STREET
    no_floors=models.CharField(max_length=10)             ##NO_FLOORS
    DATA_YEAR= models.CharField(max_length=10)
    SFT= models.CharField(max_length=10)
    Area_SqMet= models.CharField(max_length=30)
    FloodDepth10Year= models.CharField(max_length=10)
    FloodDepth50Year= models.CharField(max_length=10)
    FloodDepth100Year= models.CharField(max_length=10)
    FloodDepth500Year= models.CharField(max_length=10)
    ElevationUSGS2017= models.CharField(max_length=30)
    Elevation_Jefferson= models.CharField(max_length=30)
    Elevatio_2019USGS= models.CharField(max_length=30)
    parish=models.CharField(max_length=100)                   ##Name
    floodzone=models.CharField(max_length=100)                ##Zone
    Source= models.CharField(max_length=10)
    u_intercept= models.CharField(max_length=30)
    a_slope= models.CharField(max_length=30)
    

    
    def __str__(self):
        return self.address+" , "+self.street          