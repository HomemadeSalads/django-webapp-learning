from django.urls import path
from . import views

urlpatterns = [
    # User-facing
    path("", views.ticket_list, name="ticket-list"),
    path("new/", views.ticket_create, name="ticket-create"),
    path("<int:pk>/", views.ticket_detail, name="ticket-detail"),

    # Staff/admin
    path("admin/all/", views.admin_ticket_list, name="admin-ticket-list"),
    path("admin/<int:pk>/status/", views.admin_update_status, name="admin-ticket-status"),
]