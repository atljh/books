from decimal import Decimal
from django.contrib.auth.models import User, Group
from notifications.models import Notification
from rest_framework import serializers, generics
import books.models as mod
from datetime import date

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


# class ProfileSerializer(serializers.ModelSerializer):
#     settings = serializers.HyperlinkedRelatedField(read_only=True, view_name='settings')
#     user = serializers.StringRelatedField(
#         read_only=True,
#     )
#     books = serializers.StringRelatedField(
#         many=True,
#         # view_name="books",
#         read_only=True
#     )
#
#     class Meta:
#         model = mod.Writer
#         fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = mod.Tag
        fields = ['tag_name']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = mod.Genre
        fields = ['genre_name']


class CommentsSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = mod.Comment
        exclude = ['id']


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)


class BookSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_approved = serializers.BooleanField(read_only=True)
    chapters = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='chapter'
    )

    class Meta:
        model = mod.Book
        fields = '__all__'
        depth = 1

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['fund'] = instance.fund.fund_name
        data['tags'] = [tag.tag_name for tag in instance.tags.all()]
        data['genres'] = [genre.genre_name for genre in instance.genres.all()]
        data['views'] = len(instance.views.all())
        data['likes'] = len(instance.likes.all())
        return data

    def get_field_names(self, *args, **kwargs):
        fields = super().get_field_names(*args, **kwargs)
        try:
            suffix = self.context.get('view').suffix
            if suffix == 'List':
                fields.remove('chapters')
                fields.remove('comments')
                fields.remove('subs')
        except AttributeError:
            pass
        return fields


class LikedBookSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(default=serializers.CurrentUserDefault())

    class Meta:
        model = mod.LikedBook
        # depth = 1
        fields = ['user', 'book']



class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(
        read_only=True,

    )
    photo = serializers.ImageField(max_length=None, use_url=True)

    class Meta:
        model = mod.Profile
        # fields = '__all__'
        fields = ['user', 'photo']

        # exclude = ['photo']

    # def to_representation(self, instance):
    #     books = instance.user.books.all()
    #     # if self.context.get('many'):
    #
    #     resp_data = {
    #         'user': instance.user.username,
    #         'register_date': instance.register_date,
    #         # 'photo': instance.photo,
    #     }
    #     if hasattr(self, 'many'):
    #         resp_data['books'] = BookSerializer(books, many=True).data
    #     # if instance.photo:
    #     #     resp_data['photo'] = instance.photo
    #     return resp_data


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = mod.Transaction
        # fields = "__all__"
        exclude = ['user']


class ChapterSerializer(serializers.ModelSerializer):
    # book = serializers.CharField(source='book.title', read_only=True)
    book = serializers.Field
    author = serializers.CharField(source='book.profile', read_only=True)

    class Meta:
        model = mod.Chapter
        fields = ['author', 'book', 'chapter_name', 'content', 'id', 'is_free']
        # fields = '__all__'


class BuyChapterSerializer(serializers.Serializer):
    chapter_id = serializers.IntegerField()


class BuyChaptersSerializer(serializers.Serializer):
    # chapters = serializers.ListSerializer(serializers.IntegerField())
    chapters_id = serializers.ListField(child=serializers.IntegerField(min_value=1))
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())




class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = mod.Subscription
        fields = '__all__'


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = mod.Settings
        exclude = ['user', 'id']


class BookMarkSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # book = serializers.HyperlinkedRelatedField(read_only=True, view_name='books-detail')
    book = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = mod.BookMark
        exclude = ['id']


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = mod.Message
        exclude = ['id', 'has_seen']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # customize the serialized data here
        data['receiver'] = instance.receiver.username
        data['sender'] = instance.sender.username
        return data


class AdminMessageSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    msg_type = serializers.CharField(read_only=True)

    class Meta:
        model = mod.AdminMessage
        exclude = ['id']


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ["id", "unread", "level", 'verb', 'timestamp']


class StatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = mod.Statistic
        exclude = ['id', 'user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # customize the serialized data here
        # print(len(instance.user.all_comments.all()))
        data['all_comments'] = len(instance.user.all_comments.all())
        data['all_books'] = len(instance.user.books.all())
        data['balance'] = instance.user.profile.balance
        return data


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = mod.Discount
        fields = '__all__'

    def validate(self, attrs):
        request = self.context.get('request')

        if attrs['book'] not in request.user.books.all():
            raise serializers.ValidationError("You can add discount only to your books")
        elif attrs['book'].price < attrs['price']:
            raise serializers.ValidationError("The discount price must be lower than the previous price:)")
        elif attrs['date_finish'] < date.today():
            raise serializers.ValidationError("Wrong finish date")
        elif attrs['date_start'] < date.today():
            raise serializers.ValidationError("Wrong start date")
        elif attrs['date_finish'] < attrs['date_start']:
            raise serializers.ValidationError("Wrong date")

        return attrs


class AdvSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = mod.Advertisement
        fields = '__all__'
        # exclude = ''



