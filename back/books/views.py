from decimal import Decimal
from datetime import date, datetime
from pprint import pprint

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.views.generic import FormView
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, extend_schema_view, OpenApiParameter
from notifications.models import Notification
from rest_framework import viewsets, permissions, mixins, status
from rest_framework import generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

import books.models as mod
from back.settings import ADV_PRICE_DAY
from books.permissions import IsOwnerOrReadOnly, IsOwnerOnly, Test, BuyerReadOnly
import books.serializer as ser
from utils.change_balance import buy_book, buy_chapters
import utils.filters as f
from utils.choices import TransactionType

import requests

err = {'status': 'err', 'desc': ''}


@api_view(['GET'])
def show_profile(request):
    profile = mod.Profile.objects.get(user=request.user)
    books_data = ser.BookSerializer(request.user.books, many=True).data
    data = ser.ProfileSerializer(profile).data
    data['commission'] = profile.commission
    data['books'] = books_data
    return Response(data)


@api_view(['GET'])
def book_likes(request, pk):
    likes = mod.Book.objects.filter(pk=pk).annotate(num_likes=Count('likes')).values('num_likes')
    return Response(likes[0]['num_likes'])



class ActivateUser(UserViewSet):
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
 
        kwargs['data'] = {"uid": self.kwargs['uid'], "token": self.kwargs['token']}
 
        return serializer_class(*args, **kwargs)
 
    def activation(self, request, uid, token, *args, **kwargs):
        super().activation(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class ResetPassword(UserViewSet):
    def reset_password(self, request, *args, **kwargs):
        data = {"uid": self.kwargs['uid'], "token": self.kwargs['token']}
        return Response(status=status.HTTP_204_NO_CONTENT, data=data)




class AddChapterAPiView(generics.CreateAPIView):
    serializer_class = ser.ChapterSerializer
    queryset = mod.Chapter.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            request.user.books.get(pk=request.data.get('book'))
        except ObjectDoesNotExist:
            return self.permission_denied(request, "It's not your book!")
        return super().create(request, *args, **kwargs)
    # def get_queryset(self):
    #     return mod.Chapter.objects.filter(book__user=self.request.user)


@api_view(['GET'])
def get_statistic(request):
    stat = request.user.statistic
    return Response(ser.StatisticSerializer(stat).data)



@extend_schema(
    # request=ser.CommentsSerializer,
    parameters=[
    OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='This is id of book or chapter.'
        ),
        OpenApiParameter(
            name='type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Value must be "chapter" or "book"'
        ),
        OpenApiParameter(
            name='comment',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Text of comment (when add comment)'
        ),
    ],

    responses={200: 'OK'},
)

@api_view(['GET', 'POST'])
def add_comment(request):
    try:
        obj_type = request.GET.get('type')
        pk = request.GET.get('id')
        if obj_type == 'book':
            obj = mod.Book.objects.get(pk=pk)
        elif obj_type == 'chapter':
            obj = mod.Chapter.objects.get(pk=pk)
        else:
            raise ValueError("Wrong slug")

        if request.method == "GET":
            data = ser.CommentsSerializer(obj.comments.all(), many=True).data
            return Response(data)
        elif request.method == "POST":
            c = request.GET.get('comment')
            # new_comment = mod.Comment.objects.create(comment=request.data['comment'], user=request.user)
            new_comment = mod.Comment.objects.create(comment=c, user=request.user)
            obj.comments.add(new_comment)
            return Response(ser.CommentsSerializer(new_comment).data)

    except Exception as err:
        return Response({'status': 'err', 'desc': str(err)})



class SettingsAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ser.SettingsSerializer
    queryset = mod.Settings.objects.all()
    lookup_field = None

    def get_object(self):
        queryset = self.get_queryset()
        return queryset.get(user=self.request.user)



class NewDiscountAPIView(generics.ListCreateAPIView):
    serializer_class = ser.DiscountSerializer
    queryset = mod.Discount.objects.all()


class DiscountAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ser.DiscountSerializer
    queryset = mod.Discount.objects.all()
    permission_classes = [IsOwnerOrReadOnly]


class MessageAPIView(generics.ListCreateAPIView):
    serializer_class = ser.MessageSerializer

    def get_queryset(self):
        user = self.request.user
        return mod.Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        )


class AdminMessageAPIView(generics.ListCreateAPIView):
    serializer_class = ser.AdminMessageSerializer

    def get_queryset(self):
        user = self.request.user
        return mod.AdminMessage.objects.filter(user=user)



class TransactionAPIView(generics.ListAPIView):
    serializer_class = ser.TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return self.request.user.transactions.all()


class ProfileAPIViewSet(mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    queryset = mod.Profile.objects.all()
    serializer_class = ser.ProfileSerializer

    def get_serializer_class(self):
        s = ser.ProfileSerializer
        if 'pk' in self.kwargs:
            s.many = True
        return s


class SubscriptionAPIVewset(viewsets.ModelViewSet):
    serializer_class = ser.SubscriptionSerializer

    def get_queryset(self):
        return self.request.user.subs.all()


class ChapterAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = mod.Chapter.objects.all()
    serializer_class = ser.ChapterSerializer
    permission_classes = [BuyerReadOnly | IsOwnerOnly | permissions.IsAdminUser]
    # permission_classes = [BuyerReadOnly]
    # permission_classes = [permissions.AllowAny]


# class FinishedBooksAPIView(generics.ListCreateAPIView):
#     serializer_class = ser.BookSerializer
#
#     def get_queryset(self):
#         return self.request.user.bought_books.finished_books.all()
#
#     def create(self, request, pk, *args, **kwargs):
#         try:
#             book = self.request.user.bought_books.bought_books.get(pk=pk)
#             self.request.user.bought_books.bought_books
#         except:
#             return Response({"err": "Wrong book number"})


# class FavoriteBooksAPIView(mixins.ListModelMixin,
#                            mixins.CreateModelMixin,
#                            mixins.DestroyModelMixin,
#                            viewsets.GenericViewSet):
#     serializer_class = ser.BookSerializer
#
#     def get_queryset(self):
#         return self.request.user.bought_books.all()
#
#     def create(self, request, pk, *args, **kwargs):
#         book = mod.Book.objects.get(pk=pk)
#         request.user.bought_books.favorite_books.add(book)
#         return Response({'status': 'Added to favorite'})
#
#     def delete(self, request, pk, *args, **kwargs):
#         book = mod.Book.objects.get(pk=pk)
#         request.user.bought_books.favorite_books.remove(book)
#         return Response({'status': 'Removed from favorite'})


class BookAPIViewset(viewsets.ModelViewSet):
    queryset = mod.Book.objects.filter(is_approved=True)
    serializer_class = ser.BookSerializer
    permission_classes = [IsOwnerOrReadOnly | permissions.IsAdminUser]
    basename = 'books'

    def retrieve(self, request, *args, **kwargs):
        book = self.get_object()
        mod.BookView.objects.create(user=request.user, book=book)
        return super().retrieve(request, *args, **kwargs)

    # def retrieve(self, request, *args, **kwargs):
    #     book = self.get_object()
    #     ser_data = ser.BookSerializer(book, context={'request': request}).data
    #     return Response(ser_data)
        # if request.user == book.user:
        #     return Response(ser_data)
        # free_only = book.chapters.filter(is_free=True)
        # ser_data['chapters'] = [
        #     request.build_absolute_uri(
        #         reverse('chapter', args=[chp.pk]))
        #     for chp in free_only]
        # return Response(ser_data)

    @action(detail=True, methods=['get'])
    def buy_book(self, request, pk=None):
        try:
            consumer = mod.Profile.objects.get(user=request.user)
        except TypeError:
            resp = {'status': "err", "desc": "You are not authenticated. Please login."}
            return Response(resp)

        book = self.get_object()
        response = buy_book(consumer, book)
        return Response(response)


    @action(detail=True, methods=['get'])
    def author(self, request, pk=None):
        try:
            author = mod.User.objects.get(pk=pk)
        except TypeError:
            resp = {'status': "err", "desc": "You are not authenticated. Please login."}
            return Response(resp)
        ser_data = ser.BookSerializer(author.books.filter(is_approved=True), many=True).data
        return Response(ser_data)

    # @action(detail=True, methods=['post'])


class BuyChapterAPIView(generics.GenericAPIView):
    serializer_class = ser.BuyChaptersSerializer
    queryset = mod.Chapter.objects.all()

    def post(self, request):
        chapters = self.queryset.filter(pk__in=request.data['chapters_id'])

        response = buy_chapters(request.user.profile, chapters)
        return Response(response)


class LikeBook(generics.GenericAPIView):
    pass


class AdvBooksAPIVIew(generics.ListAPIView):
    queryset = mod.Book.objects.filter(
        Q(adv__active=True) | Q(adv__date_finish__gte=date.today())
    )
    serializer_class = ser.BookSerializer


class AdvADDApiView(generics.ListCreateAPIView):
    serializer_class = ser.AdvSerializer
    queryset = mod.Advertisement.objects.all()
    permission_classes = [IsOwnerOnly]

    def create(self, request, *args, **kwargs):
        data = self.request.data
        start = datetime.strptime(data['date_start'], '%Y-%m-%d')
        finish = datetime.strptime(data['date_finish'], '%Y-%m-%d')
        try:
            if finish < datetime.today():
                raise Exception("Wrong finish date")
            elif start < datetime.today():
                raise Exception("Wrong start date")

            elif finish < start:
                raise Exception("Wrong date")

            days = finish - start
            profile = request.user.profile
            adv_cost = (days.days + 1) * ADV_PRICE_DAY
            profile.balance -= adv_cost
            if profile.balance < 0:
                raise Exception("Insufficient funds")

        except Exception as err:
            return Response({"status": "err", "desc": str(err)})

        with transaction.atomic():
            profile.save()
            mod.Transaction.objects.create(
                transaction_type=TransactionType.BUY_ADV.value,
                amount=Decimal(adv_cost),
                user=request.user
            )
            return super().create(request, *args, **kwargs)


# def add_adv(request, pk):
#     try:
#         book = mod.Book.objects.get(pk=pk)
#         if book.user != request.user:
#             raise Exception("It must be your book. You can't advertise others' books")
#
#
#
#     except Exception as err:
#         return Response({'status': 'err', 'desc': str(err)})


class BookMarkAPIViewSet(viewsets.ModelViewSet):
    serializer_class = ser.BookMarkSerializer

    def get_queryset(self):
        return self.request.user.book_marks.all()


class PurchasedBooksAPIView(mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    serializer_class = ser.BookSerializer

    def get_queryset(self):
        return self.request.user.profile.bought_books.all()


class LikedBookAPIView(generics.ListAPIView):
    serializer_class = ser.LikedBookSerializer

    def get_queryset(self):
        return self.request.user.liked.all()

    def post(self, request, *args, **kwargs):
        book = mod.Book.objects.get(pk=request.data['book'])
        try:
            queryset = self.request.user.liked.get(book=book)
            queryset.delete()
            return Response({'status': 'ok', 'desc': 'like removed'})
        except ObjectDoesNotExist:
            mod.LikedBook.objects.create(user=request.user, book=book)
            return Response({'status': 'ok', 'desc': 'like added'})



class TagAPIView(generics.ListAPIView):
    queryset = mod.Tag.objects.all()
    serializer_class = ser.TagSerializer


class BuyChapterAPICreate(APIView):
    serializer_class = ser.ChapterSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return mod.Chapter.objects.filter(book__pk=pk)

    def post(self, request):
        pass



class RegisterUser(generics.CreateAPIView):
    model = User
    permission_classes = [permissions.AllowAny]
    serializer_class = ser.RegisterUserSerializer


class NotificationAPIView(generics.ListAPIView):
    # queryset = Notification.objects.all()
    model = Notification
    serializer_class = ser.NotificationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['unread']

    def get_queryset(self):
        return self.request.user.notifications.all()


@api_view(['GET'])
def one_notification(request, pk):
    try:
        notification = request.user.notifications.get(pk=pk)
        notification.unread = False
        notification.save()
        data = ser.NotificationSerializer(notification).data
        return Response(data)
    except Exception as err:
        return Response({"status": "err", "desc": str(err)})


@api_view(['GET'])
def dialog(request, pk):
    try:
        user = request.user
        dialog =  mod.Message.objects.filter(
            Q(sender=user) & Q(recipient=pk)
        )
        data = ser.MessageSerializer(dialog, many=True).data
        return Response(data)
    except Exception as err:
        return Response({"status": "err", "desc": str(err)})


def pay(request):
    token = 'AVpGjBnJTCZd5QK6FqNsW4G43ZHUT_wMaiCJS0xSk3w53cPntp8pg1TwR582Ywpaie1mqlGQKj-04JOh'
    return render(request, "payment.html", {'token': token})
