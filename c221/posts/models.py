from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
import misaka

User = get_user_model()

# Create your models here.

class Post(models.Model):
    user = models.ForeignKey(User, related_name="posts", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100, default='Title')
    created_at = models.DateTimeField(auto_now=True)
    message = models.TextField()
    message_html = models.TextField(editable = False)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.message_html = misaka.html(self.message)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("posts:single", kwargs={"username": self.user.username, "pk":self.pk})

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["user", "title"]

class Comment(models.Model):
    blogpost = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_date"]
        unique_together = ["author",]
    
    def get_absolute_url(self):
        return reverse('posts:all')

    def __str__(self):
        return self.text

    @property
    def num_of_comments(self):
        return Comment.objects.filter(blogpost=self).count()