from django.db import models


class PostQuerySet(models.QuerySet):

    def popular(self):
        return self.annotate(likes_count=models.Count('likes')).order_by('-likes_count')

    def fetch_with_comments_count(self):
        """ Получить количество комментариев для каждого поста """
        from .models import Post  # late import, чтобы избежать циклического импорта
        post_ids = list(self.values_list('id', flat=True))
        posts_with_comments = Post.objects.filter(id__in=post_ids).annotate(comments_count=models.Count('comments'))
        comments_count_dict = dict(posts_with_comments.values_list('id', 'comments_count'))
        for post in self:
            post.comments_count = comments_count_dict.get(post.id, 0)
        return self


class PostManager(models.Manager):

    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def popular(self):
        return self.get_queryset().popular()

    def fetch_with_comments_count(self):
        return self.get_queryset().fetch_with_comments_count()


class TagQuerySet(models.QuerySet):

    def popular(self):
        return self.annotate(posts_with_tag=models.Count('posts')).order_by('-posts_with_tag')


class TagManager(models.Manager):

    def get_queryset(self):
        return TagQuerySet(self.model, using=self._db)

    def popular(self):
        return self.get_queryset().popular()
