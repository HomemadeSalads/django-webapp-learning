from django.contrib import admin
from .models import Ticket, TicketMessage


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 1
    readonly_fields = ("created_at",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "user", "status", "created_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("subject", "description", "user__username")
    inlines = [TicketMessageInline]