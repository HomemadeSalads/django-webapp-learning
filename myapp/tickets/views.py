from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from .models import Ticket, TicketMessage
from .forms import TicketForm, TicketMessageForm, TicketStatusForm


def is_staff_user(user):
    return user.is_staff


# ---------- User-facing views ----------

@login_required
def ticket_list(request):
    """Show only the logged-in user's own tickets."""
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, "tickets/ticket_list.html", {"tickets": tickets})


@login_required
def ticket_create(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            # Also log the initial description as the first thread message,
            # so the whole conversation - including the opening message -
            # lives in one place (TicketMessage).
            TicketMessage.objects.create(
                ticket=ticket, sender=request.user, body=ticket.description
            )

            _notify_admins_new_ticket(ticket)

            messages.success(request, f"Ticket #{ticket.pk} submitted.")
            return redirect("ticket-detail", pk=ticket.pk)
    else:
        form = TicketForm()

    return render(request, "tickets/ticket_form.html", {"form": form})


@login_required
def ticket_detail(request, pk):
    """
    Shows the thread for one ticket. Accessible by the ticket's owner,
    or by any staff user (so this view doubles as the admin reply page).
    """
    ticket = get_object_or_404(Ticket, pk=pk)

    # Permission check: only the owner or staff can view this ticket
    if ticket.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have access to this ticket.")

    if request.method == "POST":
        reply_form = TicketMessageForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.ticket = ticket
            reply.sender = request.user
            reply.save()

            # If a user replies to a closed ticket, reopen it automatically
            if not request.user.is_staff and ticket.status == "closed":
                ticket.status = "open"
            elif request.user.is_staff and ticket.status == "open":
                ticket.status = "in_progress"
            ticket.save()  # also bumps updated_at

            _notify_reply(ticket, reply)
            return redirect("ticket-detail", pk=ticket.pk)
    else:
        reply_form = TicketMessageForm()

    status_form = TicketStatusForm(instance=ticket) if request.user.is_staff else None

    return render(request, "tickets/ticket_detail.html", {
        "ticket": ticket,
        "thread": ticket.messages.all(),
        "reply_form": reply_form,
        "status_form": status_form,
    })


# ---------- Staff/admin views ----------

@user_passes_test(is_staff_user)
def admin_ticket_list(request):
    """All tickets, for staff to triage. Optional ?status= filter."""
    status = request.GET.get("status", "")
    tickets = Ticket.objects.all()
    if status:
        tickets = tickets.filter(status=status)

    return render(request, "tickets/admin_ticket_list.html", {
        "tickets": tickets,
        "status": status,
        "status_choices": Ticket.STATUS_CHOICES,
    })


@user_passes_test(is_staff_user)
def admin_update_status(request, pk):
    """Staff-only: change a ticket's status without posting a reply."""
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        form = TicketStatusForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, f"Ticket #{ticket.pk} marked {ticket.get_status_display()}.")
    return redirect("ticket-detail", pk=ticket.pk)


# ---------- Email helpers ----------

def _notify_admins_new_ticket(ticket):
    """Email every staff user when a new ticket comes in."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    staff_emails = list(
        User.objects.filter(is_staff=True).exclude(email="").values_list("email", flat=True)
    )
    if staff_emails:
        send_mail(
            subject=f"New support ticket #{ticket.pk}: {ticket.subject}",
            message=f"{ticket.user.username} filed a new ticket:\n\n{ticket.description}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=staff_emails,
            fail_silently=True,
        )


def _notify_reply(ticket, reply):
    """Email the other party (user <-> staff) whenever someone replies."""
    if reply.sender.is_staff:
        recipient = ticket.user.email
    else:
        # notify staff on user replies too
        from django.contrib.auth import get_user_model
        User = get_user_model()
        staff_emails = list(
            User.objects.filter(is_staff=True).exclude(email="").values_list("email", flat=True)
        )
        recipient = staff_emails[0] if staff_emails else None

    if recipient:
        send_mail(
            subject=f"New reply on ticket #{ticket.pk}: {ticket.subject}",
            message=f"{reply.sender.username} wrote:\n\n{reply.body}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient] if isinstance(recipient, str) else recipient,
            fail_silently=True,
        )