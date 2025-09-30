from django.urls import path
from BujjiAI.views import UploadCsvToVectorView, AskBujjiView, UploadPdfToVectorView


urlpatterns = [
    path('upload-csv-to-vector/', UploadCsvToVectorView.as_view()),
    path('upload-pdf-to-vector/', UploadPdfToVectorView.as_view()),
    path('ask-bujji/', AskBujjiView.as_view()),
]
