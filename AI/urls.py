from django.urls import path
from AI.views import compare_videos

from AI.views import home
urlpatterns = [
    path('compare-videos/', compare_videos, name='compare_videos'),
    path('filter-pdf/', compare_videos, name='filter_pdf'),

    path('', home, name='home'), 


]