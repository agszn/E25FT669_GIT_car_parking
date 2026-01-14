from django.contrib import admin
from .models import ParkingSlot
from django.utils.html import format_html

class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('code', 'row', 'col', 'is_available', 'last_update', 'vehicle_number', 'owner_name', 'start_time', 'end_time', 'charges', 'get_occupation_status')
    list_filter = ('is_available', 'row', 'col')  # Filter by availability, row, column
    search_fields = ('code', 'vehicle_number', 'owner_name')  # Search by code, vehicle number, or owner name
    
    # Fieldsets to organize the form layout in the admin panel
    fieldsets = (
        (None, {
            'fields': ('code', 'row', 'col', 'is_available')
        }),
        ('Vehicle Info', {
            'fields': ('vehicle_number', 'owner_name', 'start_time', 'end_time', 'charges'),
            'classes': ('collapse',)  # Collapsable section for vehicle info
        }),
    )

    # Add a custom method to display occupation status in the list view
    def get_occupation_status(self, obj):
        return format_html('<span style="color: {};">{}</span>', 'green' if obj.is_available else 'red', 'Available' if obj.is_available else 'Occupied')
    get_occupation_status.short_description = 'Status'

    # Automatically calculate charges if the end time is provided
    def save_model(self, request, obj, form, change):
        if not obj.is_available and obj.start_time and obj.end_time:
            obj.calculate_charges()  # Calculate charges before saving
        super().save_model(request, obj, form, change)

# Register the admin interface
admin.site.register(ParkingSlot, ParkingSlotAdmin)
