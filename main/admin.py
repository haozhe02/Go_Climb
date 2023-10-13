from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
#admin.site.register(Country)
#admin.site.register(Crags)
admin.site.register(Section)
admin.site.register(MainTopic)
admin.site.register(SubTopic)
admin.site.register(ForumPost)
admin.site.register(ContactUs)
admin.site.register(FlaggedPost)
admin.site.register(Account)
admin.site.register(ClimbingActivity)
admin.site.register(Achievement)
admin.site.register(SearchHistory)
admin.site.register(Crag)
admin.site.register(Comment)

class AccountInLine(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'Accounts'

class CustomizedUserAdmin(UserAdmin):
    inlines = (AccountInLine, )

admin.site.unregister(User)
admin.site.register(User, CustomizedUserAdmin)

