# from django.contrib.auth.models import User
# from django.db.models.signals import post_save, pre_save
# from django.dispatch import receiver
# from notifications.signals import notify
#
# from books.models import Profile, Book,
#
#
# @receiver(post_save, sender=Book)
# def change_status_book(sender, instance, created, **kwargs):
#     if created:
#         return
#     if 'is_approved' in kwargs['update_fields']:
#         if instance.is_approved:
#             notify.send(instance, recipient=instance.user, verb=f'Книгу - {instance.title} погодженно')
#         else:
#             notify.send(instance, recipient=instance.user, verb=f'Книгу - {instance.title} відхиленно')
#
#
