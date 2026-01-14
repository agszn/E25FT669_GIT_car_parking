from django.db import models
from datetime import timedelta

class ParkingSlot(models.Model):
    code = models.CharField(max_length=20, unique=True)  # e.g. "A1", "B2"
    row = models.IntegerField()
    col = models.IntegerField()
    is_available = models.BooleanField(default=True)
    last_update = models.DateTimeField(auto_now=True)

    # Additional fields for occupied slots
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.code} - {'Free' if self.is_available else 'Occupied'}"

    @classmethod
    def get_available_slots(cls):
        """Fetches all available parking slots."""
        return cls.objects.filter(is_available=True)

    @classmethod
    def get_occupied_slots(cls):
        """Fetches all occupied parking slots."""
        return cls.objects.filter(is_available=False)

    def calculate_charges(self):
        """Calculates parking charges if the slot is occupied."""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            # Assuming the rate is 100 INR per hour
            rate_per_hour = 100
            hours = duration.total_seconds() / 3600  # Convert to hours
            self.charges = round(hours * rate_per_hour, 2)
            self.save(update_fields=["charges"])

    def update_slot(self, is_available, vehicle_number=None, owner_name=None, start_time=None, end_time=None):
        """Updates slot availability and details if occupied."""
        self.is_available = is_available
        if not is_available:  # If slot is occupied
            self.vehicle_number = vehicle_number
            self.owner_name = owner_name
            self.start_time = start_time
            self.end_time = end_time
            if self.end_time:  # Calculate charges when the slot is marked as occupied
                self.calculate_charges()
        else:
            # Clear vehicle-related details if slot is made available
            self.vehicle_number = None
            self.owner_name = None
            self.start_time = None
            self.end_time = None
            self.charges = 0.0

        self.save(update_fields=["is_available", "vehicle_number", "owner_name", "start_time", "end_time", "charges", "last_update"])
