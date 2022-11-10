from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    title = models.TextField()
    content = models.TextField()
    image_path = models.URLField(max_length=1000, blank=True)
    source_name = models.TextField()
    source_link = models.URLField(max_length=1000, blank=True)

    @property
    def links(self) -> int:
        return self.libart_set.count()


class Library(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.TextField()

    @property
    def articles(self) -> int:
        return self.libart_set.count()


class LibArt(models.Model):
    library = models.ForeignKey(Library, on_delete=models.DO_NOTHING)
    article = models.ForeignKey(Article, on_delete=models.DO_NOTHING)
