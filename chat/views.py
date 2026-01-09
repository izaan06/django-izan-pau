from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import ChatMessage
from .forms import ChatMessageForm
from events.models import Event


# -----------------------------------
# Enviar missatge
# -----------------------------------
@login_required
@require_POST
def chat_send_message(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)

    if event.status != 'live':
        return JsonResponse({'success': False, 'error': 'Event no actiu'})

    form = ChatMessageForm(request.POST)
    if form.is_valid():
        msg = form.save(commit=False)
        msg.user = request.user
        msg.event = event
        msg.save()

        return JsonResponse({
            'success': True,
            'message': {
                'id': msg.id,
                'user': msg.user.username,
                'display_name': msg.get_user_display_name(),
                'message': msg.message,
                'created_at': msg.get_time_since(),
                'can_delete': msg.can_delete(request.user),
                'is_highlighted': msg.is_highlighted
            }
        })

    return JsonResponse({'success': False, 'errors': form.errors})


# -----------------------------------
# Carregar missatges
# -----------------------------------
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import ChatMessage
from events.models import Event

def chat_load_messages(request, event_pk):
    # Obtenim l'esdeveniment
    event = get_object_or_404(Event, pk=event_pk)

    # Obtenim tots els missatges de l'esdeveniment
    messages_qs = ChatMessage.objects.filter(event=event).order_by('created_at')

    # Filtrar els eliminats (soft delete) i limitar a 50
    messages_qs = [msg for msg in messages_qs if not msg.is_deleted][:50]

    # Serialitzar els missatges a JSON amb tota la informació que el JS necessita
    messages = [
        {
            'id': msg.id,
            'user_id': msg.user.id,
            'user': msg.user.username,
            'display_name': msg.get_user_display_name(),
            'message': msg.message,
            'created_at': msg.get_time_since(),  # Exemple: "fa 2 minuts"
            'can_delete': msg.can_delete(request.user),  # Mostrar botó si True
            'can_highlight': request.user.is_authenticated and request.user == msg.user,
            'is_highlighted': msg.is_highlighted
        }
        for msg in messages_qs
    ]

    return JsonResponse({'messages': messages})


# -----------------------------------
# Eliminar missatge
# -----------------------------------
@login_required
@require_POST
def chat_delete_message(request, message_pk):
    msg = get_object_or_404(ChatMessage, pk=message_pk)

    if not msg.can_delete(request.user):
        return JsonResponse({'success': False})

    msg.is_deleted = True
    msg.save()
    return JsonResponse({'success': True})


# -----------------------------------
# Destacar missatge
# -----------------------------------
@login_required
@require_POST
def chat_highlight_message(request, message_pk):
    msg = get_object_or_404(ChatMessage, pk=message_pk)

    # Solo el creador del mensaje puede destacar
    if request.user != msg.user:
        return JsonResponse({'success': False})

    msg.is_highlighted = not msg.is_highlighted
    msg.save()
    return JsonResponse({'success': True})

