from django.urls import path
from .views import *

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('main/<int:main_id>/', MainView.as_view(), name='main'),
    path('<str:course_label>/', CourseView.as_view(), name='course'),
    path('standings/<str:standings_label>/', StandingsView.as_view(), name='standings'),
    path('standings/<str:standings_label>/<int:contest_id>/', StandingsView.as_view(), name='standings'),
    path('standings_data/<str:standings_label>/', StandingsDataView.as_view(), name='standings_data'),
    path('form/<str:form_label>/', FormView.as_view(), name='form'),
    path('standings_contests/', StandingsReload.as_view(), name='standings_reload')
]
