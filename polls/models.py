import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
import secrets

class QuestionManager(models.Manager):
    def with_optimized_data(self):
        from django.db.models import Prefetch
        return self.select_related('owner').prefetch_related(
            Prefetch('choice_set', queryset=Choice.objects.annotate(vote_count=Count('votes')))
        ).annotate(
            total_votes=Count('choice__votes'),
            choice_count=Count('choice')
        )
    
    def published(self):
        return self.filter(pub_date__lte=timezone.now())

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    objects = QuestionManager()  # Use the custom manager
    
    def __str__(self):
        return self.question_text
    
    def was_published_recently(self):
        now = timezone.now()
        return now - timezone.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def votes_percentage(self):
        total_votes = self.question.choice_set.aggregate(models.Sum('votes'))['votes__sum']
        if total_votes > 0:
            return (self.votes / total_votes) * 100
        return 0

    def __str__(self):
        return self.choice_text

# Comment out advanced models for now - add them later
'''
class APIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=64, unique=True, default=secrets.token_hex)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    can_create_polls = models.BooleanField(default=True)
    max_polls_per_day = models.IntegerField(default=5)
    
    def __str__(self):
        return self.user.username

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['user', 'choice']]
    
    def __str__(self):
        return f"Vote for {self.choice.choice_text}"
'''

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['user', 'choice']]
        indexes = [
            models.Index(fields=['user', 'choice']),
            models.Index(fields=['ip_address', 'voted_at']),
        ]

    def __str__(self):
        return f"Vote for {self.choice.choice_text}"
    
