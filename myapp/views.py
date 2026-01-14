import json
import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import ParkingSlot

logger = logging.getLogger(__name__)

def base(request):
    # Optional base view, e.g. homepage
    return render(request, 'base.html')

def parking_3d_view(request):
    # Render the 3D parking dashboard, passing slot data as JSON
    slots = ParkingSlot.objects.all().values(
        "id", "code", "row", "col", "is_available", "last_update"
    )
    return render(request, "dashboard/dashboard.html", {
        "parking_slots_json": json.dumps(list(slots), default=str)
    })

def parking_slots_json(request):
    # Return JSON list of all slots (for frontend fetch)
    slots = ParkingSlot.objects.all().values(
        "id", "code", "row", "col", "is_available", "last_update"
    )
    return JsonResponse(list(slots), safe=False)

@csrf_exempt
def parking_slot_update_api(request):
    # API endpoint to update a single slot from ESP POST
    if request.method != "POST":
        return JsonResponse({"detail": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    slot_code = data.get("slot_code")
    is_available = data.get("is_available")

    if slot_code is None or is_available is None:
        return JsonResponse(
            {"detail": "Fields 'slot_code' and 'is_available' are required"},
            status=400,
        )

    try:
        slot = ParkingSlot.objects.get(code=slot_code)
    except ParkingSlot.DoesNotExist:
        return JsonResponse({"detail": "Slot does not exist"}, status=404)

    slot.is_available = bool(is_available)
    slot.save(update_fields=["is_available", "last_update"])

    logger.info(f"Slot {slot.code} updated to {slot.is_available}")

    return JsonResponse({
        "detail": "updated",
        "slot_id": slot.id,
        "slot_code": slot.code,
        "is_available": slot.is_available,
        "last_update": slot.last_update.isoformat(),
    })


# ===================
from django.http import JsonResponse
from django.shortcuts import render
from .models import ParkingSlot

def parking_slots_view(request):
    # Fetch all available and occupied parking slots
    available_slots = ParkingSlot.get_available_slots()
    occupied_slots = ParkingSlot.get_occupied_slots()

    # Check if the request is an AJAX request (using 'X-Requested-With' header)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX request
        available_slots_data = [{"code": slot.code, "row": slot.row, "col": slot.col} for slot in available_slots]
        occupied_slots_data = [{"code": slot.code, "row": slot.row, "col": slot.col} for slot in occupied_slots]

        # Return the data as a JSON response
        return JsonResponse({
            'available_slots': available_slots_data,
            'occupied_slots': occupied_slots_data,
        })

    # If it's not an AJAX request, return the normal page
    context = {
        'available_slots': available_slots,
        'occupied_slots': occupied_slots,
    }
    return render(request, 'dashboard/parking_slots.html', context)
