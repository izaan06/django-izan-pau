from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Event
from .forms import EventCreationForm, EventUpdateForm, EventSearchForm
from chat.forms import ChatMessageForm


# Vista de llistat d'esdeveniments
def event_list_view(request):
    form = EventSearchForm(request.GET or None)
    events = Event.objects.all()  # agafa tots els esdeveniments

    # Filtrat segons els camps del formulari
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if search:
            events = events.filter(title__icontains=search)
        if category:
            events = events.filter(category=category)
        if status:
            events = events.filter(status=status)
        if date_from:
            events = events.filter(scheduled_date__gte=date_from)
        if date_to:
            events = events.filter(scheduled_date__lte=date_to)

    # Esdeveniments destacats (filtrat en Python per evitar Djongo BooleanField error)
    all_events = Event.objects.all()
    featured_events = [e for e in all_events if e.is_featured and e.created_at is not None]
    featured_events.sort(key=lambda e: e.created_at, reverse=True)

    # Paginació dels esdeveniments principals
    paginator = Paginator(events.order_by('-created_at'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'events/event_list.html', {
        'page_obj': page_obj,
        'form': form,
        'featured_events': featured_events
    })


# Vista de detall d'un esdeveniment
def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    is_creator = request.user == event.creator  # verificar si l'usuari és el creador
    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_creator': is_creator,
        'chat_form': ChatMessageForm(),
    })


# Vista de creació d'esdeveniment (només per usuaris autenticats)
@login_required
def event_create_view(request):
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user  # assigna l'usuari com a creador
            event.save()
            messages.success(request, "Esdeveniment creat correctament!")
            return redirect(event.get_absolute_url())
    else:
        form = EventCreationForm()
    return render(request, 'events/event_form.html', {'form': form})


# Vista d'edició d'esdeveniment (només el creador pot editar)
@login_required
def event_update_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.creator:
        messages.error(request, "Només el creador pot editar aquest esdeveniment.")
        return redirect(event.get_absolute_url())

    if request.method == 'POST':
        form = EventUpdateForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Esdeveniment actualitzat correctament!")
            return redirect(event.get_absolute_url())
    else:
        form = EventUpdateForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form, 'event': event})


# Vista d'eliminació d'esdeveniment (només el creador pot eliminar)
@login_required
def event_delete_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.creator:
        messages.error(request, "Només el creador pot eliminar aquest esdeveniment.")
        return redirect(event.get_absolute_url())

    if request.method == 'POST':
        event.delete()
        messages.success(request, "Esdeveniment eliminat correctament!")
        return redirect('events:event_list')

    return render(request, 'events/event_confirm_delete.html', {'event': event})


# Vista per veure els esdeveniments propis d'un usuari
@login_required
def my_events_view(request):
    events = Event.objects.filter(creator=request.user)
    status_filter = request.GET.get('status')
    if status_filter:
        events = events.filter(status=status_filter)

    paginator = Paginator(events.order_by('-created_at'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'events/my_events.html', {'page_obj': page_obj})


# Vista per llistar esdeveniments segons categoria
def events_by_category_view(request, category):
    if category not in dict(Event.CATEGORY_CHOICES).keys():
        messages.error(request, "Categoria no vàlida.")
        return redirect('events:event_list')

    events = Event.objects.filter(category=category)
    paginator = Paginator(events.order_by('-created_at'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'events/event_list.html', {
        'page_obj': page_obj,
        'form': EventSearchForm(),  # mantenim la barra de cerca
    })
