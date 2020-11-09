from django.db import models
from datetime import date, datetime
from django.contrib.auth.models import User
from django.urls import reverse


# Post
class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # delete blogs of deleted user
    # ingredients = models.ManyToManyField(Ingredients, help_text='Input ingredients')
    body = models.TextField(max_length=1000, help_text='Recipe body')
    post_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    # Return url 
    def get_absolute_url(self):
        return reverse('recipe_detail', args=[str(self.id)])




