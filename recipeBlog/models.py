from django.db import models
from datetime import date
from django.contrib.auth.models import User


# Post
class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # delete blogs of deleted user
    # ingredients = models.ManyToManyField(Ingredients, help_text='Input ingredients')
    body = models.TextField()

    def __str__(self):
        return self.title + ' by ' + self.author




