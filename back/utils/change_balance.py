from djoser.conf import User
from datetime import date
from books.models import Profile, Book, Statistic, Transaction, Chapter
from decimal import Decimal
from django.db import transaction
from loguru import logger
from utils.choices import TYPE_TRANSACTION_CHOICES, tr_types
from notifications.signals import notify


def _make_transaction(user: User, change_value: Decimal, tr_type: str):
    return Transaction(transaction_type=tr_type,
                       amount=change_value,
                       user=user)


def _update_statistic(seller: User, last_sell):
    stat: Statistic = Statistic.objects.get_or_create(user=seller)[0]
    stat.sold += 1
    stat.income += last_sell
    stat.save()


def _update_balances(price: Decimal, seller: Profile, consumer: Profile, amount=1) -> Decimal:
    earned = price * amount / 100 * (100 - seller.commission)
    seller.balance += earned
    consumer.balance -= price * amount
    objs = [consumer, seller]
    # transaction1 = Transaction(TransactionType.SPEND, )
    Profile.objects.bulk_update(objs, ['balance'])
    return earned



@transaction.atomic
def buy_book(consumer: Profile, book: Book) -> dict:
    if book.discount.active and book.discount.date_finish > date.today():
        price = book.discount.price
    else:
        price = book.price
    if consumer.user.username == book.user.username:
        return {'status': 'err', 'desc': 'You can`t buy your own book!'}

    elif consumer.balance < price:
        return {'status': 'err', 'desc': 'Insufficient funds'}
    else:
        books = consumer.bought_books
        if book in books.all():
            return {'status': 'err', 'desc': 'You have bought this book already!'}
        books.add(book)
        seller = book.user
        earned = _update_balances(price, seller.profile, consumer)
        _update_statistic(seller, earned)

        # _save_bought_book(book, books)
        transaction1 = _make_transaction(consumer.user, price, tr_types['SPEND'])
        transaction2 = _make_transaction(seller, earned, tr_types['EARN'])
        Transaction.objects.bulk_create([transaction1, transaction2])

        notify.send(consumer,
                    recipient=seller,
                    verb=f'{consumer.user.username.capitalize()} тільки що придбав твою книгу - {book.title}')

        return {'success': True}



@transaction.atomic
def buy_chapters(consumer: Profile, chapters: list[Chapter]) -> dict:
    book = chapters[0].book
    if consumer.user.username == book.user.username:
        return {'status': 'err', 'desc': 'You can`t buy your own chapter!'}
    # if chapter.book.discount.active and chapter.book.discount.date_finish > date.today():
    #     price = book.discount.price
    # else:
    #     price = book.price

    # if consumer.balance < price:
    #     return {'status': 'err', 'desc': 'Insufficient funds'}
        # if consumer.user in chapter.users_with_access.all():
        #     return {'status': 'err', 'desc': 'You have bought this chapter already!'}

    bought_count = 0
    paid_chapters = [chapter for chapter in chapters if not chapter.is_free]
    if not paid_chapters:
        return {'info': f"Nothing to buy, all chapters is free"}
    for chapter in paid_chapters:
        if consumer.user not in chapter.users_with_access.all():
            chapter.users_with_access.add(consumer.user)
            bought_count += 1
    if bought_count == 0:
        return {'info': f"Nothing to buy, all chapters you already bought"}
    price = None
    for sub in book.subs.all():
        if sub.quantity <= bought_count:
            price = sub.price
            break

    if not price:
        price = book.price_chapter

    seller = book.user
    earned = _update_balances(price, seller.profile, consumer, amount=bought_count)
    _update_statistic(seller, earned)

    transaction1 = _make_transaction(consumer.user, price*bought_count, tr_types['SPEND'])
    transaction2 = _make_transaction(seller, earned, tr_types['EARN'])
    Transaction.objects.bulk_create([transaction1, transaction2])

    notify.send(consumer,
                recipient=seller,
                verb=f'{consumer.user.username.capitalize()} купив глав - {bought_count}\n'
                     f'Ти заробив: {earned}$')

    return {'success': f"You bought {bought_count} paid_chapters!",
            'spends': f"{round(price * bought_count, 2)}$"}
