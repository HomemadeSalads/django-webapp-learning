from django.conf import settings
from django.db import models
from django.urls import reverse


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("closed", "Closed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]  # most recently active tickets first

    def __str__(self):
        return f"#{self.pk} {self.subject} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse("ticket-detail", kwargs={"pk": self.pk})


class TicketMessage(models.Model):
    """
    One message in a ticket's conversation thread — either from the
    ticket owner or from a staff member replying.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]  # oldest first, like a chat thread

    def __str__(self):
        return f"Message on #{self.ticket_id} by {self.sender}"

    @property
    def is_staff_reply(self):
        return self.sender.is_staff