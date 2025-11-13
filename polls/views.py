from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch
from django.http import HttpResponseRedirect
from .models import Question, Choice, Vote  # Import models

# Remove the QuestionManager class from views.py - it belongs in models.py
# class QuestionManager(models.Manager):  # ← DELETE THIS FROM VIEWS.PY
#     def with_optimized_data(self):
#         return self.select_related('owner').prefetch_related(
#             Prefetch('choice_set', queryset=Choice.objects.annotate(vote_count=Count('votes')))
#         ).annotate(
#             total_votes=Count('choice__votes'),
#             choice_count=Count('choice')
#         )
#     
#     def published(self):
#         return self.filter(pub_date__lte=timezone.now())

class QuestionListView(ListView):
    model = Question
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'
    paginate_by = 5
    
    def get_queryset(self):
        """Return the last 10 published questions."""
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).select_related('owner').prefetch_related('choice_set').annotate(
            total_votes=Count('choice__votes')
        ).order_by('-pub_date')[:10]

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'polls/detail.html'
    
    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())

class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    template_name = 'polls/question_form.html'
    fields = ['question_text', 'pub_date']
    success_url = reverse_lazy('polls:index')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class QuestionUpdateView(LoginRequiredMixin, UpdateView):
    model = Question
    template_name = 'polls/question_form.html'
    fields = ['question_text', 'pub_date']
    
    def get_success_url(self):
        return reverse_lazy('polls:detail', kwargs={'pk': self.object.pk})

class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    model = Question
    template_name = 'polls/question_confirm_delete.html'
    success_url = reverse_lazy('polls:index')

class VoteView(UpdateView):
    model = Choice
    fields = []
    
    def post(self, request, *args, **kwargs):
        choice = self.get_object()
        choice.votes += 1
        choice.save()
        
        # Store vote in session to prevent duplicate voting
        request.session[f'voted_question_{choice.question.id}'] = True
        
        return redirect('polls:results', pk=choice.question.id)

    # Keep the original function-based views for results and vote as backup
    def results(request, pk):
        question = get_object_or_404(Question, pk=pk)
        return render(request, 'polls/results.html', {'question': question})

    def vote(request, question_id):
        question = get_object_or_404(Question, pk=question_id)
        try:
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "You didn't select a choice.",
            })
        else:
            selected_choice.votes += 1
            selected_choice.save()
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
        
