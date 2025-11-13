from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.db.models import Sum
from .models import Question, Choice, Vote
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Question)
def validate_question(sender, instance, **kwargs):
    """Validate question before saving"""
    if not instance.question_text.strip():
        raise ValueError("Question text cannot be empty")

@receiver(post_save, sender=Question)
def question_created(sender, instance, created, **kwargs):
    """Signal when a new question is created"""
    if created:
        logger.info(f"New question created: {instance.question_text}")
        cache.delete('latest_questions')

@receiver(post_save, sender=Choice)
def choice_added(sender, instance, created, **kwargs):
    """Signal when a new choice is added to a question"""
    if created:
        logger.info(f"New choice '{instance.choice_text}' added to question: {instance.question.question_text}")

@receiver(post_save, sender=Vote)
def vote_count_updated(sender, instance, **kwargs):
    """Update question vote statistics when a vote is cast"""
    question = instance.choice.question
    # FIXED: Use Sum instead of sum, and fix the field reference
    total = question.choice_set.aggregate(total=Sum('votes'))['total'] or 0
    # Note: This will only work if Question model has total_votes field
    # If not, either remove this line or add the field to models.py
    logger.info(f"Vote recorded - Question '{question.question_text}' now has {total} total votes")

@receiver(post_delete, sender=Question)
def question_deleted(sender, instance, **kwargs):
    """Clean up when a question is deleted"""
    logger.info(f"Question deleted: {instance.question_text}")
    cache.delete('latest_questions')