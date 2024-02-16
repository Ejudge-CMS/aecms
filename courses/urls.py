from django.urls import path
from .views import *

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('main/<int:main_id>/', MainView.as_view(), name='main'),
    path('<str:course_label>/', CourseView.as_view(), name='course'),
    path('standings/<str:standings_label>/', StandingsView.as_view(), name='standings'),
    path('standings/<str:standings_label>/<int:contest_id>/', StandingsView.as_view(), name='standings'),
    path('standings_data/<str:standings_label>/', StandingsDataView.as_view(), name='standings_data'),
    path('form/data/', FormDataView.as_view(), name='form_data'),
    path('form/export/json/<str:form_label>', FormJsonExport.as_view(), name='form_json_export'),
    path('form/export/csv/<str:form_label>', FormCSVExport.as_view(), name='form_csv_export'),
    path('form/<str:form_label>/', FormView.as_view(), name='form')
]
