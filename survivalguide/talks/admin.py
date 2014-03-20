from __future__ import absolute_import

from django.contrib import admin

from . import models


class TalkListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    list_filter = ('user',)


admin.site.register(models.TalkList, TalkListAdmin)
admin.site.register(models.Talk)
