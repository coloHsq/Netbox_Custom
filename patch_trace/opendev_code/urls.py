from django.urls import path
from . import views

app_name = 'opendev'

urlpatterns = [

    path(r'patchpanels/', views.PatchPanelListView.as_view(), name='patchPanels'),
    path(r'patchpanels/<int:pk>/', views.PatchPanelTrace.as_view(), name='patchPanelTrace'),
]
