from django.db import models


#https://www.geeksforgeeks.org/django-models/
class Member(models.Model):
   class Meta:
      db_table= 'members'
      managed = False
