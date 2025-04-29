from django.utils.translation import gettext_lazy as _

from rest_framework.views import APIView
from rest_framework import  status
from rest_framework.response import Response
from .serializers import ProductionBatchSerializer
from .models import ProductionBatch
from logger import logger



class ProductionBatchListCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = ProductionBatchSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Error serializers: {serializer.errors}")
            return Response(serializer.errors, status=400)
        try:
            serializer.save()
            logger.info(f"Production batch created: ID {serializer.instance.id if serializer.instance else 'N/A'}")
            return Response(serializer.data, status=201)
        except Exception as e:
             logger.error(f"Error saving production batch: {e}", exc_info=True)
             return Response(
                 {"detail": "An unexpected error occurred while saving the batch."}, 
                 status=500
             )

    def get(self, request,  *args, **kwargs):
        # titles = [production_batch.title for production_batch in ProductionBatch.objects.all()]
        batches = ProductionBatch.objects.all()
        serializer = ProductionBatchSerializer(batches, many=True)

        return Response(serializer.data, status=200)

class ProductionBatchUpdateDeleteAPIView(APIView):
    def _get_object(self, pk):
        try:
            return ProductionBatch.objects.get(pk=pk)
        except ProductionBatch.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error fetching ProductionBatch pk={pk}: {e}", exc_info=True)
            return None #
    
    def put(self, request, pk, *args, **kwargs):
        """
        Полное обновление (замена) данных производственной партии.
        Требует передачи всех не read-only полей.
        """
        batch = self._get_object(pk)
        if batch is None:
            logger.warning(f"PUT request for non-existent ProductionBatch pk={pk}")
            return Response({"detail": "Production batch not found."}, status=404)

        serializer = ProductionBatchSerializer(instance=batch, data=request.data)

        if not serializer.is_valid():
            logger.error(f"Validation errors on PUT for pk={pk}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save()
            logger.info(f"Production batch pk={pk} updated successfully via PUT.")
            return Response(serializer.data, status=status.HTTP_200_OK)  
        except Exception as e:
             logger.error(f"Error saving updated production batch pk={pk} via PUT: {e}", exc_info=True)
             return Response(
                 {"detail": "An unexpected error occurred while updating the batch."},
                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
             )

    def patch(self, request, pk, *args, **kwargs):
        """
        Частичное обновление данных производственной партии.
        Позволяет передавать только измененные поля.
        """
        batch = self._get_object(pk)
        if batch is None:
             logger.warning(f"PATCH request for non-existent ProductionBatch pk={pk}")
             return Response({"detail": "Production batch not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ключевое отличие от PUT: partial=True
        serializer = ProductionBatchSerializer(instance=batch, data=request.data, partial=True)

        if not serializer.is_valid():
            logger.error(f"Validation errors on PATCH for pk={pk}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save()
            logger.info(f"Production batch pk={pk} partially updated successfully via PATCH.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
             logger.error(f"Error saving partially updated production batch pk={pk} via PATCH: {e}", exc_info=True)
             return Response(
                 {"detail": "An unexpected error occurred while updating the batch."},
                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
             )

    def delete(self, request, pk, *args, **kwargs):
         """Удаление производственной партии."""
         batch = self._get_object(pk)
         if batch is None:
             logger.warning(f"DELETE request for non-existent ProductionBatch pk={pk}")
             return Response({"detail": "Production batch not found."}, status=status.HTTP_404_NOT_FOUND)

         try:
             batch_id = batch.pk  
             batch.delete()
             logger.info(f"Production batch pk={batch_id} deleted successfully.")
             return Response(status=status.HTTP_204_NO_CONTENT)
         except Exception as e:
              logger.error(f"Error deleting production batch pk={pk}: {e}", exc_info=True)
              return Response(
                  {"detail": "An unexpected error occurred while deleting the batch."},
                  status=status.HTTP_500_INTERNAL_SERVER_ERROR
              )
