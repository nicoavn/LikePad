from django.contrib.auth.models import User
from django.db import models
import datetime
from django.utils import timezone

# Create your models here.
from Like.Exceptions import *


class Like(models.Model):
    reported_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="likes_given")
    reported_to = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="likes")
    when = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return "Like from " + self.reported_by.first_name[0:1] + ". " + self.reported_by.last_name + " to " + \
            self.reported_to.first_name[0:1] + ". " + self.reported_to.last_name

    @classmethod
    def report(cls, reporter, report_to):
        if reporter.pk == report_to.pk:
            raise IllegalLikeException()

        now = timezone.now()
        datetime_day_start = timezone.datetime(now.year, now.month, now.day)
        datetime_day_end = timezone.datetime(now.year, now.month, now.day, 23, 59, 59)
        day_likes = Like.objects.filter(when__range=(datetime_day_start, datetime_day_end),
                                        reported_by=reporter, deleted_at__isnull=True)

        if len(day_likes) > 2:
            raise DailyVotesAlreadyGivenException()

        day_likes = day_likes.filter(reported_to=report_to)
        if day_likes:
            raise AlreadyLikedUserException()

        like = Like(reported_by=reporter, reported_to=report_to)
        like.save()

    @classmethod
    def undo_report(cls, reporter, report_to):
        if reporter.pk == report_to.pk:
            raise IllegalLikeException()

        now = timezone.now()
        datetime_day_start = timezone.datetime(now.year, now.month, now.day)
        datetime_day_end = timezone.datetime(now.year, now.month, now.day, 23, 59, 59)

        like = Like.objects.filter(reported_by=reporter, reported_to=report_to, deleted_at__isnull=True,
                                   when__range=(datetime_day_start, datetime_day_end)).first()
        if like:
            like.deleted_at = now
            like.save()

    @classmethod
    def get_day_likes(cls, user):
        now = timezone.now()
        datetime_day_start = timezone.datetime(now.year, now.month, now.day, 0, 0, 0)
        datetime_day_end = timezone.datetime(now.year, now.month, now.day, 23, 59, 59)
        day_likes = Like.objects.filter(when__range=(datetime_day_start, datetime_day_end), deleted_at__isnull=True)
        return day_likes.filter(reported_to=user)

    @classmethod
    def get_week_likes(cls, user):
        now = timezone.now()
        datetime_day_start = timezone.datetime(now.year, now.month, now.day)
        datetime_day_end = timezone.datetime(now.year, now.month, now.day, 23, 59, 59)

        idx = (datetime_day_start.weekday() + 1) % 7  # MON = 0, SUN = 6 -> SUN = 0 .. SAT = 6
        mon = datetime_day_start - datetime.timedelta(idx - 1)
        fri = datetime_day_end + datetime.timedelta(idx + 1)

        week_likes = Like.objects.filter(when__range=(mon, fri), deleted_at__isnull=True)

        return week_likes.filter(reported_to=user)
