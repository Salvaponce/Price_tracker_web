from django.contrib import admin

from Price_tracker_app.models import Report, Product, Feedback

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject','date',)
    search_fields = ('name', 'email',)
    date_hierarchy = 'date'

# Register your models here.
admin.site.register(Report)
admin.site.register(Product)
admin.site.register(Feedback, FeedbackAdmin)