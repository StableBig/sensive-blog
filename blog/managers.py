from django.db import models


class PostQuerySet(models.QuerySet):

    def year(self, year):
        return self.filter(published_at__year=year)


class PostManager(models.Manager):

    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def year(self, year):
        return self.get_queryset().year(year)
