from rest_framework import serializers
from app_productions.models import ProductionBatch, Product




class ProductionBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionBatch
        fields = ['id','batch_number', 'title', 'planned_completion_date', 'notes', 'is_completed', 'created_at']
        read_only_fields = ['created_at', ]

