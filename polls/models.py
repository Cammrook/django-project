import datetime
from django.db import models
from django.utils import timezone
from django.db.models import Q

from django.contrib import admin

# Create your models here.

class Question(models.Model):
    question_text = models.CharField(verbose_name="question text", max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self) -> str:
        return self.question_text

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self) -> bool:
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    @staticmethod
    def get_by_year(year):
        """Returns all questions published in the given year."""
        return Question.objects.filter(pub_date__year=year)

    class Meta:
        indexes = [
            models.Index(fields=['pub_date']),
        ]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.choice_text

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(votes__gte=0), name='votes_non_negative'),
        ]