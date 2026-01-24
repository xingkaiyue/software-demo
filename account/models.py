from django.db import models


class UserInfo(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    token = models.CharField(max_length=64)




# Create your models here.
