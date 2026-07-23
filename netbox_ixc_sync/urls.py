from django.urls import path
from netbox.views.generic import ObjectChangeLogView
from . import views
from .models import IXCConfig, SyncLog

urlpatterns = [
    # IXCConfig
    path('configs/', views.IXCConfigListView.as_view(), name='ixcconfig_list'),
    path('configs/add/', views.IXCConfigEditView.as_view(), name='ixcconfig_add'),
    path('configs/<int:pk>/', views.IXCConfigView.as_view(), name='ixcconfig'),
    path('configs/<int:pk>/edit/', views.IXCConfigEditView.as_view(), name='ixcconfig_edit'),
    path('configs/<int:pk>/delete/', views.IXCConfigDeleteView.as_view(), name='ixcconfig_delete'),
    path('configs/<int:pk>/sync/', views.IXCSyncView.as_view(), name='ixcconfig_sync'),
    path('configs/<int:pk>/changelog/', ObjectChangeLogView.as_view(),
         name='ixcconfig_changelog', kwargs={'model': IXCConfig}),

    # SyncLog
    path('logs/', views.SyncLogListView.as_view(), name='synclog_list'),
    path('logs/<int:pk>/', views.SyncLogView.as_view(), name='synclog'),
    path('logs/<int:pk>/delete/', views.SyncLogDeleteView.as_view(), name='synclog_delete'),
]
