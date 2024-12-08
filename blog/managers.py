from django.db import models


class PostQuerySet(models.QuerySet):

    def year(self, year):
        return self.filter(published_at__year=year)


class PostManager(models.Manager):

    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def year(self, year):
        return self.get_queryset().year(year)


class TagQuerySet(models.QuerySet):

    def popular(self):
        return self.annotate(posts_with_tag=models.Count('posts')).order_by('-posts_with_tag')


class TagManager(models.Manager):

    def get_queryset(self):
        return TagQuerySet(self.model, using=self._db)

    def popular(self):
        return self.get_queryset().popular()
