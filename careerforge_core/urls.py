"""
URL configuration for careerforge_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import home
from resumes.views import upload_resume
from django.conf import settings
from django.conf.urls.static import static
from jobs.views import job_matches
from resumes.views import resume_result
from interviews.views import start_interview, take_interview, submit_interview, interview_results
from interviews.views import tts_speak

from interviews.views import (
    start_interview, take_interview, submit_interview, interview_results,
    start_voice_interview, voice_interview, voice_answer, finish_voice_interview,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', home, name='home'),
    path('resumes/upload/', upload_resume, name='upload_resume'),
    path('jobs/matches/', job_matches, name='job_matches'),
    path('resumes/upload/', upload_resume, name='upload_resume'),
    path('resumes/<int:resume_id>/result/', resume_result, name='resume_result'),
    path('interviews/start/<int:job_id>/', start_interview, name='start_interview'),
    path('interviews/<int:session_id>/take/', take_interview, name='take_interview'),
    path('interviews/<int:session_id>/submit/', submit_interview, name='submit_interview'),
    path('interviews/<int:session_id>/results/', interview_results, name='interview_results'),
    path('interviews/start-voice/<int:job_id>/', start_voice_interview, name='start_voice_interview'),
    path('interviews/<int:session_id>/voice/', voice_interview, name='voice_interview'),
    path('interviews/<int:session_id>/voice/answer/', voice_answer, name='voice_answer'),
    path('interviews/<int:session_id>/voice/finish/', finish_voice_interview, name='finish_voice_interview'),
    path('interviews/tts/', tts_speak, name='tts_speak'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
