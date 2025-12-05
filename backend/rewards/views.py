from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
import json
from .models import User, Vendor, UserTransaction, Reward, Ledger


def index(request):
    """Render the main single-page frontend."""
    return render(request, "rewards/index.html")


@csrf_exempt  
def api_login(request):
    """
    POST /api/login/
    Body: { "email": "...", "password": "..." }
    Returns: { "user": { id, name, email, phone, total_points } }
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    import json
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JsonResponse({"detail": "Email and password required"}, status=400)

    # Using Django auth; assumes AUTH_USER_MODEL is rewards.User
    user = authenticate(request, email=email, password=password)

    if user is None:
        # Fallback for plain-text passwords
        try:
            user = User.objects.get(email=email, password=password)
        except User.DoesNotExist:
            user = None

    if user is None:
        return JsonResponse({"detail": "Invalid credentials"}, status=401)

    login(request, user)

    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "total_points": user.total_points,
    }
    return JsonResponse({"user": user_data})


def _require_auth(request):
    """Helper to enforce authentication for API endpoints."""
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)
    return None


@csrf_exempt
def api_register(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    if not all([name, email, phone, password]):
        return JsonResponse({"error": "All fields required"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already registered"}, status=400)

    user = User.objects.create_user(
        email=email,
        name=name,
        phone=phone,
        password=password
    )

    return JsonResponse({
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
        }
    }, status=201)

def api_account(request):
    """
    GET /api/account/
    Returns current user's basic info.
    """
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    auth_error = _require_auth(request)
    if auth_error:
        return auth_error

    user = request.user
    data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "total_points": user.total_points,
    }
    return JsonResponse(data)


def api_rewards(request):
    """
    GET /api/rewards/
    Returns:
    {
      "total_points": int,
      "ledger": [
        { "change_amount": int, "reason": str, "date": "YYYY-MM-DD", "expiration_date": "YYYY-MM-DD or null" },
        ...
      ],
      "rewards": [
        { "vendor_name": str, "balance": float, "expiration": "YYYY-MM-DD" },
        ...
      ]
    }
    """
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    auth_error = _require_auth(request)
    if auth_error:
        return auth_error

    user = request.user

    # Use the total_points field on User
    total_points = user.total_points

    # Ledger entries for this user
    ledger_qs = Ledger.objects.filter(user=user).order_by("-date", "-ledger_id")
    ledger_list = []
    for entry in ledger_qs:
        ledger_list.append({
            "change_amount": f"+{entry.change_amount}" if entry.change_amount > 0 else str(entry.change_amount),
            "reason": entry.reason,
            "date": entry.date.isoformat(),
            "expiration_date": entry.expiration_date.isoformat() if entry.expiration_date else "-",
        })

    # Rewards per vendor
    rewards_qs = Reward.objects.filter(user=user).select_related("vendor")
    rewards_list = []
    for r in rewards_qs:
        rewards_list.append({
            "vendor_name": r.vendor.name,
            "balance": float(r.balance),
            "expiration": r.expiration.isoformat(),
        })

    return JsonResponse({
        "total_points": total_points,
        "ledger": ledger_list,
        "rewards": rewards_list,
    })


def api_stores(request):
    """
    GET /api/stores/
    Returns list of spending per vendor for this user:
    [
      { "vendor_name": str, "category": str, "total_spent": float },
      ...
    ]
    """
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    auth_error = _require_auth(request)
    if auth_error:
        return auth_error

    user = request.user

    # Sum purchase amounts per vendor
    qs = (
        UserTransaction.objects
        .filter(user=user, transaction_type="PURCHASE")
        .values("vendor__name", "vendor__category")
        .annotate(total_spent=Sum("amount"))
        .order_by("-total_spent")
    )

    result = []
    for row in qs:
        result.append({
            "vendor_name": row["vendor__name"],
            "category": row["vendor__category"],
            "total_spent": float(row["total_spent"]),
        })

    return JsonResponse(result, safe=False)


@csrf_exempt
def api_exchange(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    vendor_id = data.get("vendor_id")
    credit_amount = data.get("credit_amount") 

    if not vendor_id or not credit_amount:
        return JsonResponse({"error": "Missing fields"}, status=400)

    credit_amount = int(credit_amount)

    # conversion table
    cost_map = {
        5: 40000,
        10: 75000,
        15: 110000,
        25: 180000,
        50: 350000,
    }

    if credit_amount not in cost_map:
        return JsonResponse({"error": "Invalid credit selection"}, status=400)

    cost_points = cost_map[credit_amount]

    user = request.user

    if user.total_points < cost_points:
        return JsonResponse({"error": "Not enough points"}, status=400)

    user.total_points -= cost_points
    user.save()

    vendor = Vendor.objects.get(pk=vendor_id)
    reward_obj, _ = Reward.objects.get_or_create(
        user=user,
        vendor=vendor,
        defaults={"balance": 0, "expiration": "2026-12-31"}
    )

    reward_obj.balance += credit_amount
    reward_obj.save()

    from datetime import date
    Ledger.objects.create(
        user=user,
        transaction=None,
        change_amount=-cost_points,
        reason=f"${credit_amount} Credit Redemption",
        date=date.today(),
        expiration_date=None
    )

    return JsonResponse({
        "message": f"Successfully redeemed {cost_points} points for ${credit_amount} credit at {vendor.name}.",
        "remaining_points": user.total_points,
        "credit_added": credit_amount,
        "vendor_name": vendor.name,
    })

def api_vendors(request):
    vendors = Vendor.objects.all().values("vendor_id", "name", "category")
    return JsonResponse(list(vendors), safe=False)

@csrf_exempt
def api_logout(request):
    if request.method != "POST":
        return JsonResponse({"detail": "POST required"}, status=400)

    logout(request)
    return JsonResponse({"message": "Logged out"})