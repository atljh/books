from django.contrib import admin
from django.urls import reverse
from django.contrib import messages
from django.utils.safestring import mark_safe

import books.models as m


@admin.register(m.Subscription)
class WriterAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Profile)
class WriterAdmin(admin.ModelAdmin):
    search_fields = ['user__email']


@admin.register(m.User)
class BookAdmin(admin.ModelAdmin):
    search_fields = ['user__email']


@admin.register(m.Book)
class BookAdmin(admin.ModelAdmin):

    exclude = ('comments',)
    search_fields = ['title']

    def save_model(self, request, obj, form, change):
        update_fields = []

        # True if something changed in model
        # Note that change is False at the very first time
        if change:
            if form.initial['is_approved'] != form.cleaned_data['is_approved']:
                update_fields.append('is_approved')

                obj.save(update_fields=update_fields)
        return super().save_model(request, obj, form, change)


@admin.register(m.Fund)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Genre)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Tag)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Chapter)
class BookAdmin(admin.ModelAdmin):
    exclude = ('comments',)


@admin.register(m.Settings)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Transaction)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(m.BookMark)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Comment)
class BookAdmin(admin.ModelAdmin):
    pass


def respond_to_message(modeladmin, request, queryset):
    for message in queryset:
        url = reverse('admin:myapp_message_change', args=[message.id])
        response_message = f"Responding to message: {message.subject}"
        messages.success(request, mark_safe(response_message))
        messages.info(request, mark_safe(f"To respond, please visit: <a href='{url}'>{url}</a>"))


@admin.register(m.AdminMessage)
class BookAdmin(admin.ModelAdmin):
    pass
    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     message = self.get_object(request, object_id)
    #     if message:
    #         print('ok')
    #         # url = reverse('#', args=[message.id])
    #         url = '#'
    #
    #         button = mark_safe(f'<a class="button" href="{url}">Respond to message</a>')
    #         extra_context = {'button': button}
    #         extra_context['my_var'] = 'Hello, world!'
    #         return super().change_view(request, object_id, form_url, extra_context=extra_context)

    # list_display = ['sender', 'message']

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     # return qs.filter(recipient=request.user.profile.is_staff)


@admin.register(m.AccessBook)
class BookAdmin(admin.ModelAdmin):
    # exclude = ['comments']
    pass

@admin.register(m.Statistic)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Discount)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Advertisement)
class BookAdmin(admin.ModelAdmin):
    pass
