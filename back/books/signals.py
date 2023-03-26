from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from notifications.signals import notify

from books.models import *
from utils.choices import tr_types


@receiver(post_save, sender=User)
def new_profile(sender, instance, created, **kwargs):
    if created:
        Statistic.objects.create(user=instance)
        Settings.objects.create(user=instance)
        if instance.is_superuser:
            is_staff = True
        else:
            is_staff = False

        Profile.objects.create(is_staff=is_staff, user=instance)


@receiver(post_save, sender=Book)
def new_book(sender, instance, created, **kwargs):
    if created:
        AccessBook.objects.create(book=instance)
        Discount.objects.create(book=instance)
        Advertisement.objects.create(book=instance)


@receiver(post_save, sender=Book)
def change_status_book(sender, instance, created, **kwargs):
    if created or not kwargs['update_fields']:
        return
    if 'is_approved' in kwargs['update_fields']:
        if instance.is_approved:
            notify.send(instance, recipient=instance.user, verb=f'Книгу - {instance.title} погодженно')
        else:
            notify.send(instance, recipient=instance.user, verb=f'Книгу - {instance.title} відхиленно')


def _check_commission(profile: Profile, all_characters: int):
    if all_characters > 10000000 and profile.commission != 10:
        new_commission = 10
        profile.commission = new_commission
    elif all_characters > 5000000 and profile.commission != 12:
        new_commission = 12
        profile.commission = new_commission
    else:
        return
    profile.save()
    notify.send(profile, recipient=profile.user, verb=f'Комісію знижено! Нове значення - {new_commission}')


@receiver(pre_save, sender=Chapter)
def update_stat_when_update_chapter(sender, instance, **kwargs):
    if not instance.pk:
        return
    prev = instance.book.chapters.get(pk=instance.pk)
    stat = instance.book.user.statistic
    profile = instance.book.user.profile
    prev_char_number = len(prev.content)
    new_char_number = len(instance.content)
    stat.all_characters = stat.all_characters - prev_char_number + new_char_number
    stat.save()
    _check_commission(profile, stat.all_characters)


@receiver(post_save, sender=Chapter)
def add_chapter(sender, instance, created, **kwargs):
    if created:
        profile = instance.book.user.profile
        stat = instance.book.user.statistic
        char_number = len(instance.content)
        stat.all_characters += char_number
        stat.save()
        _check_commission(profile, stat.all_characters)


# def buy_adv(post_save, sender=Advertisement):
#     Transaction.objects.create(transaction_type=tr_types['SPEND'],
#                 amount=change_value,
#                 user=user)