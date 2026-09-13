from django import forms
from .models import Ticket, TicketMessage


class TicketForm(forms.ModelForm):
    """Used by a user to file a new ticket."""
    class Meta:
        model = Ticket
        fields = ["subject", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Describe the problem..."}),
        }


class TicketMessageForm(forms.ModelForm):
    """Used by either the user or staff to reply within a ticket thread."""
    class Meta:
        model = TicketMessage
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3, "placeholder": "Write a reply..."}),
        }
        labels = {"body": ""}


class TicketStatusForm(forms.ModelForm):
    """Staff-only: change a ticket's status."""
    class Meta:
        model = Ticket
        fields = ["status"]