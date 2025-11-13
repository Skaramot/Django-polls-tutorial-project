from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.QuestionListView.as_view(), name='index'),
    path('<int:pk>/', views.QuestionDetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.QuestionDetailView.as_view(template_name='polls/results.html'), name='results'),
    path('<int:pk>/vote/', views.VoteView.as_view(), name='vote'),
    path('create/', views.QuestionCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.QuestionUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='delete'),
]