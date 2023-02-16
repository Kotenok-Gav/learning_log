from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404


from .models import Topic, Entry
from .forms import TopicForm, EntryForm


def index(request):
    "Домашняя страница приложения Learning Log"
    return render(request, "learning_logs/index.html")



@login_required
def topics(request):
    "Выводит все темы."

    # выдается запрос к базе данных на получение объектов Topic, отсортированных по атрибуту date_added.
    # Полученный итоговый набор сохраняется в topics
#    topics = Topic.objects.order_by("date_added")

    """приказывает Django извлечь из базы данных только 
    те объекты Topic, у которых атрибут owner соответствует текущему пользователю. """
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')


    """Контекст представляет собой словарь, в котором ключами являются имена, используемые в шаблоне для обращения к данным, 
    а значениями — данные, которые должны передаваться шаблону. В данном случае существует всего одна пара
     «ключ-значение», которая содержит набор тем, отображаемых на странице. """
    context = {'topics': topics}
    return render(request, "learning_logs/topics.html", context)
    #                1                  2                   3
    # 1 исходный объект запроса
    # 2 шаблон используемый для построения страницы
    # 3 контекст который будет передаваться шаблону, context - словарь в котором:
    #   ключами являются имена используемые в шаблоне для обращения к данным
    #   значениями - данные, которые передаются шаблону



@login_required
def topic(request, topic_id):
    "Выводит одну тему и все ее записи."

    #функция get() используется для получения темы
    topic = Topic.objects.get(id = topic_id)


    # Проверка того, что тема принадлежит текущему пользователю.
    if topic.owner != request.user:
        raise Http404


    """В entries загружаются записи, связанные с данной темой, и они упорядочиваются по значению date_added: знак
     «минус» перед date_added сортирует результаты в обратном порядке, то есть самые последние записи будут находиться 
    на первых местах"""
    entries = topic.entry_set.order_by('-date_added')

    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """Определяет новую тему."""
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма.
        form = TopicForm()
    else:
        # Отправлены данные POST; обработать данные.
        form = TopicForm(data=request.POST)  # request.POST - тут хранятся данные введенные пользователем
        if form.is_valid():        #проверка на корректность ввода данных
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
#            form.save()              #сохранение введенных данных в БД
            return redirect('learning_logs:topics')

    # Вывести пустую или недействительную форму.
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)



@login_required
def new_entry(request, topic_id):
    """Добавляет новую запись по конкретной теме."""

    topic = Topic.objects.get(id=topic_id)
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма.
        form = EntryForm()
    else:
        # Отправлены данные POST; обработать данные.
        form = EntryForm(data=request.POST)   # request.POST - тут хранятся данные введенные пользователем
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    # Вывести пустую или недействительную форму.
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)



@login_required
def edit_entry(request, entry_id):
    """Редактирует существующую запись."""
    entry = Entry.objects.get(id=entry_id)   #получаем объект записи, который пользователь хочет изменить,
    topic = entry.topic                     #  и тему, связанную с этой записью

    #совпадает ли владелец темы с текущим пользователем
    if topic.owner != request.user:
        raise Http404


    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи.
        form = EntryForm(instance=entry)   #аргумент приказывает Django создать форму, заранее заполненную информацией из существующего объекта записи
    else:
        # Отправка данных POST; обработать данные.
        form = EntryForm(instance=entry, data=request.POST)   # создать экземпляр формы на основании информации существующего объекта записи, обновленный данными из request.POST
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)