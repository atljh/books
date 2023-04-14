from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.urls import path, include, re_path
from rest_framework import routers
import books.views as v


router = routers.DefaultRouter()
# router.register(r'profile', v.ProfileAPIViewSet)
router.register(r'marks', v.BookMarkAPIViewSet, basename='marks')
router.register(r'books', v.BookAPIViewset, basename='books')
router.register(r'subscriptions', v.SubscriptionAPIVewset, basename='subscriptions')
# router.register(r'likes', v.LikedBookAPIView, basename='likes')


urlpatterns = [
    path('me/', v.show_profile),
    path('like/', v.LikedBookAPIView.as_view()),
    path('book_likes/<int:pk>', v.book_likes),
    path('statistic/', v.get_statistic),
    path('settings/', v.SettingsAPIView.as_view(), name='settings'),
    path('transactions/', v.TransactionAPIView.as_view(), name='transactions'),
    path('chapter/<int:pk>/', v.ChapterAPIView.as_view(), name='chapter'),
    path('chapter/buy/', v.BuyChapterAPIView.as_view()),
    path('chapter/add/', v.AddChapterAPiView.as_view()),


    path('tags/', v.TagAPIView.as_view()),

    path('accounts/activate/<uid>/<token>', v.ActivateUser.as_view({'get': 'activation'}), name='activation'),
    path('accounts/password/reset/confirm/<uid>/<token>', v.ResetPassword.as_view({'get': 'reset_password'}), name='reset_password'),

    path('profiles/', v.ProfileAPIViewSet.as_view({'get': 'list'})),
    path('profiles/<int:pk>', v.ProfileAPIViewSet.as_view({'get': 'retrieve'}), name='profile'),
    path('purchased/', v.PurchasedBooksAPIView.as_view({'get': 'list'})),
    path('purchased/<int:pk>', v.PurchasedBooksAPIView.as_view({'get': 'retrieve'})),
    path('comments/', v.add_comment),


    path('adv-books/', v.AdvBooksAPIVIew.as_view()),
    path('adv-add/', v.AdvADDApiView.as_view()),
    path('discount/', v.NewDiscountAPIView.as_view()),
    path('discount/<int:pk>', v.DiscountAPIView.as_view()),

    path('mail/', v.MessageAPIView.as_view()),
    path('mail/<int:pk>', v.dialog),
    path('mail-admin/', v.AdminMessageAPIView.as_view()),
    path('notifications/', v.NotificationAPIView.as_view()),
    path('notifications/<int:pk>', v.one_notification),

    path(r'auth/', include('djoser.urls')),
    re_path(r'auth/', include('djoser.urls.authtoken')),

    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

] + router.urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# router.register(r'chapters', v.ChapterViewSet)




