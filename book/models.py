from django.db import models


class BookInfo(models.Model):
    book_code=models.CharField(max_length=100,unique=True)
    book_name=models.CharField(max_length=100)
    author=models.CharField(max_length=100)
    publisher=models.CharField(max_length=100)
    price=models.DecimalField(decimal_places=2,max_digits=10)
    stock=models.DecimalField(decimal_places=2,max_digits=10)