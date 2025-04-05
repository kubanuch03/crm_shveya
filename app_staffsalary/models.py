from django.db import models
from app_users.models import User


class StaffSalary(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Сотрудник')
    
    def __str__(self):
        return f"{self.staff}"