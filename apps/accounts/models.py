from django.contrib.auth.models import AbstractUser
from django.db import models

"""
Custom User model for FleetFlow.

Extends Django's AbstractUser to implement
Role-Based Access Control (RBAC).

Defines system roles:
- Fleet Manager
- Dispatcher
- Safety Officer
- Financial Analyst

All permission and navigation logic depends on this model.
"""


class User(AbstractUser):

    class Role(models.TextChoices):
        FLEET_MANAGER = "FLEET_MANAGER", "Fleet Manager"
        DISPATCHER = "DISPATCHER", "Dispatcher"
        SAFETY_OFFICER = "SAFETY_OFFICER", "Safety Officer"
        FINANCIAL_ANALYST = "FINANCIAL_ANALYST", "Financial Analyst"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.FLEET_MANAGER,
        db_index=True,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
        
    @property
    def is_manager(self):
        return self.role == self.Role.FLEET_MANAGER

    @property
    def is_dispatcher(self):
        return self.role == self.Role.DISPATCHER

    @property
    def is_safety_officer(self):
        return self.role == self.Role.SAFETY_OFFICER

    @property
    def is_financial_analyst(self):
        return self.role == self.Role.FINANCIAL_ANALYST