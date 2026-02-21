from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date

from apps.workflow.models import WorkItem, Vehicle, Driver
from apps.accounts.models import User
from services.workflow_service import transition


class TestWorkflowTransitions(TestCase):

    def setUp(self):
        self.manager = User.objects.create(
            username="manager_test",
            role=User.Role.FLEET_MANAGER
        )

        self.dispatcher = User.objects.create(
            username="dispatcher_test",
            role=User.Role.DISPATCHER
        )

        self.driver_user = User.objects.create(
            username="driver_test",
            role=User.Role.DISPATCHER
        )

        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_expiry=date(2026, 12, 31)
        )

        self.vehicle = Vehicle.objects.create(
            name="Truck-01",
            license_plate="TEST123",
            vehicle_type=Vehicle.VehicleType.TRUCK,
            max_capacity=1000,
            acquisition_cost=5000000,
            odometer_current=10000,
        )

    def test_valid_dispatch(self):
        trip = WorkItem.objects.create(
            title="Trip A",
            description="Testing",
            created_by=self.manager,
            driver=self.driver,
            vehicle=self.vehicle,
            cargo_weight=500
        )

        transition(trip, WorkItem.TripStatus.DISPATCHED, self.dispatcher)
        self.assertEqual(trip.status, WorkItem.TripStatus.DISPATCHED)

    def test_vehicle_overlap(self):
        trip1 = WorkItem.objects.create(
            title="Trip 1",
            description="Test",
            created_by=self.manager,
            driver=self.driver,
            vehicle=self.vehicle,
            cargo_weight=500
        )

        transition(trip1, WorkItem.TripStatus.DISPATCHED, self.dispatcher)

        trip2 = WorkItem.objects.create(
            title="Trip 2",
            description="Test",
            created_by=self.manager,
            driver=self.driver,
            vehicle=self.vehicle,
            cargo_weight=300
        )

        with self.assertRaises(ValidationError):
            transition(trip2, WorkItem.TripStatus.DISPATCHED, self.dispatcher)