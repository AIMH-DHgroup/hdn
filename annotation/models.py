"""

| **Project**: HDN
| **Package**: Backend
| **Title**: Models in Django
| **File**: models.py
| **Path**: annotation/
| **Type**: python
| **Started**: 2020-04-26
| **Author(s)**: Nicolo' Pratelli & Daniele Metilli
| **State**: in use

Version history.

:2020-04-26 Nicolo' Pratelli & Daniele Metilli:
    * First version

:2020-05-07 Daniele Metilli:
    * Added Author, Source and Area Models

:2020-06-16 Nicolo' Pratelli:
    * Added Commentary model

This file is part of software developed by the Digital Libraries group
of AIMH Laboratory, Institute of Information Science and Technologies
(ISTI-CNR), Pisa, Italy, for the IMAGO and HDN projects.
Further information at: https://hdn.dantenetwork.it
Copyright (C) 2020 ISTI-CNR, Nicolo' Pratelli & Daniele Metilli

This is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation; either version 3.0 of the License,
or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.db import models

class Annotation(models.Model):
    """This class is the model of a Annotation record.
    """
    id = models.BigIntegerField(unique=True, primary_key=True)
    data = JSONField()

    # Fix plural name in admin
    class Meta:
        ordering = ['id']

class Author(models.Model):
    """This class is the model of a Author record.
    """
    data = JSONField()

    # Fix plural name in admin
    class Meta:
        ordering = ['data__name']

class Source(models.Model):
    """This class is the model of a Source record.
    """
    data = JSONField()

    # Fix plural name in admin
    class Meta:
        ordering = ['data__title']

class Area(models.Model):
    """This class is the model of a Area record.
    """
    data = JSONField()

    # Fix plural name in admin
    class Meta:
        ordering = ['data__name']

class Commentary(models.Model):
    """This class is the model of a Commentary record.
    """
    data = JSONField()
    
    # Fix plural name in admin
    class Meta:
        verbose_name_plural = 'Commentaries'
        ordering = ['data__name']

class Owner(models.Model):
    """This class is the model of a Commentary record.
    """
    
    commentary = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class Place(models.Model):
    """This class is the model of a Place record.
    """
    data = JSONField()
    
    # Fix plural name in admin
    class Meta:
        verbose_name_plural = 'Places'
        ordering = ['data__name']

class Character(models.Model):
    """This class is the model of a Character record.
    """
    data = JSONField()
    
    # Fix plural name in admin
    class Meta:
        verbose_name_plural = 'Characters'
        ordering = ['data__name']