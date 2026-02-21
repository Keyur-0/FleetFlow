from django import forms
from .models import WorkItem, Vehicle, Driver, MaintenanceLog, FuelLog

class TripCreateForm(forms.ModelForm):
    class Meta:
        model = WorkItem
        fields = [
            "title",
            "description",
            "origin",
            "destination",
            "vehicle",
            "driver",
            "cargo_weight",
            "estimated_fuel_cost",
            "revenue",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only show AVAILABLE vehicles
        self.fields["vehicle"].queryset = Vehicle.objects.filter(
            status=Vehicle.Status.AVAILABLE
        )

        # Only show ON_DUTY drivers
        self.fields["driver"].queryset = Driver.objects.filter(
            status=Driver.Status.ON_DUTY
        )

    def clean(self):
        cleaned_data = super().clean()

        vehicle = cleaned_data.get("vehicle")
        driver = cleaned_data.get("driver")
        cargo_weight = cleaned_data.get("cargo_weight")

        if driver and not driver.is_license_valid():
            raise forms.ValidationError("Driver license has expired.")

        if vehicle and cargo_weight:
            if cargo_weight > vehicle.max_capacity:
                raise forms.ValidationError(
                    "Cargo weight exceeds vehicle capacity."
                )

        return cleaned_data
    
class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceLog
        fields = ["vehicle", "description", "cost"]

class FuelLogForm(forms.ModelForm):
    class Meta:
        model = FuelLog
        fields = [
            "vehicle",
            "trip",
            "liters",
            "cost",
            "odometer_reading",
            "date",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }