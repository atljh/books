from django.db import models
# from django.contrib.auth.models import User
import utils.choices as choice
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

from decimal import Decimal, getcontext
getcontext().prec = 2


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users require an email field')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    

class Profile(models.Model):
    photo = models.ImageField(upload_to="photos/users/", null=True, blank=True)
    balance = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal(0))
    register_date = models.DateField(auto_now=True)
    commission = models.IntegerField(choices=choice.COMMISSION_CHOICE, default=15)
    bought_books = models.ManyToManyField('Book', related_name='buyers', blank=True)

    is_staff = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='profile')

    def __str__(self):
        return self.user.email

    # def save(self, *args, **kwargs):
    #     'some actions'
    #     super().save(*args, **kwargs)


class Settings(models.Model):
    font_size = models.IntegerField(default=16)
    font_color = models.CharField(default="#000000", max_length=7)
    background_color = models.CharField(default="#e5e5e5", max_length=7)

    notifications = models.BooleanField(default=True)
    site_news = models.BooleanField(default=True)
    private_messages = models.BooleanField(default=True)
    comments = models.BooleanField(default=True)
    is_adult = models.BooleanField(default=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')

    def __str__(self):
        return f"{self.user.email.capitalize()}'s settings"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receive_messages")
    message = models.TextField()
    time = models.DateTimeField(auto_now=True)
    has_seen = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} | {self.time}'

    class Meta:
        ordering = ['time']


class AdminMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages_admin")
    message = models.TextField()
    time = models.DateTimeField(auto_now=True)
    msg_type = models.CharField(default='question', choices=choice.TYPE_MSG, max_length=40)

    def __str__(self):
        return f'{self.user.email} | {self.time}'

    class Meta:
        ordering = ['time']



class Transaction(models.Model):
    transaction_type = models.CharField(max_length=40, choices=choice.TransactionType.CHOICES.value)
    time = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    user = models.ForeignKey(User, related_name="transactions", on_delete=models.CASCADE)

    class Meta:
        ordering = ['time']

    def __str__(self):
        return f'Transaction - {self.transaction_type} -> {self.amount} $'


class BookMark(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='in_bookmarks')
    book_status = models.CharField(max_length=40, choices=choice.STATUS_BOOK_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_marks')


class Statistic(models.Model):
    looked = models.IntegerField(default=0)
    income = models.DecimalField(default=0, max_digits=6, decimal_places=2)  # change
    sold = models.IntegerField(default=0)  # change
    like = models.IntegerField(default=0)
    in_marks = models.IntegerField(default=0)
    all_characters = models.IntegerField(default=0)

    user = models.OneToOneField(User, related_name="statistic", on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.email}`s stat'


class Fund(models.Model):
    fund_name = models.CharField(max_length=50)

    def __str__(self):
        return self.fund_name


class Tag(models.Model):
    tag_name = models.CharField(max_length=50)

    def __str__(self):
        return self.tag_name


class Genre(models.Model):
    genre_name = models.CharField(max_length=40)

    def __str__(self):
        return self.genre_name


def upload_to(instance, filename):
    return 'images/books/{filename}'.format(filename=filename)


class Photo(models.Model):
    file = models.ImageField(upload_to=upload_to, null=True, blank=True)
    book = models.ForeignKey('Book', related_name='photos', on_delete=models.CASCADE)


class Comment(models.Model):
    comment = models.TextField()
    user = models.ForeignKey(User, related_name='all_comments', on_delete=models.CASCADE)


class Subscription(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subs")

    class Meta:
        ordering = ['-quantity']

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    original_language = models.CharField(max_length=40, choices=choice.LANGUAGE_CHOICES)
    type_book = models.CharField(max_length=40, choices=choice.TYPE_BOOK_CHOICES)
    age_restrictions = models.BooleanField('Обмеження за вiком 18+', default=False)
    is_ready = models.BooleanField(default=False)
    fund = models.ForeignKey(Fund, on_delete=models.DO_NOTHING, related_name='books')
    created = models.DateField(auto_now=True)
    last_edit = models.DateField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True)
    genres = models.ManyToManyField(Genre, blank=True)
    main_photo = models.ImageField(upload_to=upload_to, null=True, blank=True)
    comments = models.ManyToManyField(Comment, blank=True)

    can_buy_all_book = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price_chapter = models.DecimalField(max_digits=6, decimal_places=2)
    subs = models.ManyToManyField(Subscription, blank=True)
    is_approved = models.BooleanField(default=None, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="books")

    # likes = models.ManyToManyField(User, related_name="liked_books")

    def __str__(self):
        return self.title


class LikedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='likes')


class BookView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='views')
    date = models.DateField(auto_now=True)


class Advertisement(models.Model):
    active = models.BooleanField(default=False)
    date_start = models.DateField(null=True)
    date_finish = models.DateField(null=True)
    book = models.OneToOneField(Book, related_name='adv', on_delete=models.CASCADE)

    def __str__(self):
        return self.book.title


class Discount(models.Model):
    active = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    date_start = models.DateField(null=True)
    date_finish = models.DateField(null=True)
    book = models.OneToOneField(Book, related_name='discount', on_delete=models.CASCADE)

    def __str__(self):
        return self.book.title


class AccessBook(models.Model):
    comment_book = models.CharField(max_length=40, choices=choice.ACTION_ACCESS_CHOICES, default='all')
    comment_chapter = models.CharField(max_length=40, choices=choice.ACTION_ACCESS_CHOICES, default='all')
    comment_page = models.CharField(max_length=40, choices=choice.ACTION_ACCESS_CHOICES, default='all')
    download = models.CharField(max_length=40, choices=choice.ACTION_ACCESS_CHOICES, default='all')
    estimate = models.CharField(max_length=40, choices=choice.ACTION_ACCESS_CHOICES, default='all')

    book = models.OneToOneField(Book, on_delete=models.CASCADE, primary_key=True, related_name='access')

    def __str__(self):
        return self.book.title


class UserStatusBook(models.Model):
    user = models.ForeignKey(User, related_name='reading', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='reading', on_delete=models.CASCADE)
    status = models.CharField(max_length=40, choices=choice.STATUS_BOOK_CHOICES)


class SeenBook(models.Model):
    has_seen = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='seen_books', on_delete=models.CASCADE)
    book = models.ForeignKey(User, related_name='users_seen', on_delete=models.CASCADE)


class Rating(models.Model):
    rating = models.IntegerField(choices=choice.STARS_CHOICES, default=5)
    translation = models.IntegerField(choices=choice.STARS_CHOICES, default=5)
    book = models.ForeignKey(Book, related_name='ratings', on_delete=models.CASCADE)


class Chapter(models.Model):
    chapter_name = models.CharField(max_length=50)
    content = models.TextField()
    is_free = models.BooleanField(default=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="chapters")

    users_with_access = models.ManyToManyField(User, blank=True)
    comments = models.ManyToManyField(Comment, blank=True)

    def __str__(self):
        return self.chapter_name
