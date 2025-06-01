from django.urls import path
from .views import ProductionBatchListCreateAPIView, ProductionBatchUpdateDeleteAPIView

app_name = 'product'
urlpatterns = [
    path('create_list/product_batch/', ProductionBatchListCreateAPIView.as_view(), name='create_list_pb'),
    path('update_delete/product_batch/<int:pk>/', ProductionBatchUpdateDeleteAPIView.as_view(), name='update_delete_pb'),
]