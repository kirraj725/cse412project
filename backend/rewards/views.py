from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from django.utils import timezone
import json
from decimal import Decimal
from datetime import timedelta, date
from .models import User, Vendor, UserTransaction, Reward, Ledger

ADMIN_EMAILS = {"alice@gmail.com"}

def is_admin(user):
    return bool(user and (user.is_staff or user.is_superuser or user.email in ADMIN_EMAILS))

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
    ) # type: ignore

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
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    user = request.user
    data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "total_points": user.total_points,
        "is_admin": is_admin(user),
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

@csrf_exempt
def api_users(request):
    if not request.user.is_authenticated or not is_admin(request.user):
        return JsonResponse({"error": "Forbidden"}, status=403)

    users = User.objects.all().order_by("name")
    data = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "total_points": u.total_points,
        }
        for u in users
    ]
    return JsonResponse({"users": data})

@csrf_exempt
def api_create_transaction(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    if not request.user.is_authenticated or not is_admin(request.user):
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_id = payload.get("user_id")
    vendor_id = payload.get("vendor_id")
    amount_str = payload.get("amount")

    if not user_id or not vendor_id or not amount_str:
        return JsonResponse({"error": "user_id, vendor_id, and amount are required"}, status=400)

    try:
        user_id = int(user_id)
        vendor_id = int(vendor_id)
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid user_id or vendor_id"}, status=400)

    try:
        amount = Decimal(str(amount_str))
    except Exception:
        return JsonResponse({"error": "Amount must be a number"}, status=400)

    # Transaction type
    transaction_type = (payload.get("transaction_type") or "PURCHASE").upper()
    if transaction_type not in ("PURCHASE", "REFUND"):
        return JsonResponse({"error": "Invalid transaction type"}, status=400)

    location = payload.get("location") or "Tempe, AZ"

    date_str = payload.get("date")
    if date_str:
        try:
            tx_date = date.fromisoformat(date_str)
        except ValueError:
            return JsonResponse({"error": "Invalid date format (expected YYYY-MM-DD)"}, status=400)
    else:
        tx_date = timezone.now().date()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    try:
        vendor = Vendor.objects.get(vendor_id=vendor_id)
    except Vendor.DoesNotExist:
        return JsonResponse({"error": "Vendor not found"}, status=404)

    tx = UserTransaction.objects.create(
        user=user,
        vendor=vendor,
        transaction_type=transaction_type,
        amount=amount,
        location=location,
        date=tx_date,
    )
    change_amount = int(amount * 100)

    if transaction_type == "REFUND" and change_amount > 0:
        change_amount = -change_amount

    if change_amount >= 0:
        reason = "Purchase Points"
        expiration_date = tx_date + timedelta(days=365)
    else:
        reason = "Refund"
        expiration_date = None

    Ledger.objects.create(
        user=user,
        transaction=tx,
        change_amount=change_amount,
        reason=reason,
        date=tx_date,
        expiration_date=expiration_date,
    )

    user.total_points = user.total_points + change_amount
    user.save()

    return JsonResponse({
        "success": True,
        "transaction": {
            "id": tx.trans_id,
            "user_id": user.id,
            "user_name": user.name,
            "vendor_id": vendor.vendor_id,
            "vendor_name": vendor.name,
            "transaction_type": tx.transaction_type,
            "amount": str(tx.amount),
            "location": tx.location,
            "date": tx.date.isoformat(),
        },
        "new_total_points": user.total_points,
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
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    vendors = Vendor.objects.all().order_by("name")
    data = [
        {
            "vendor_id": v.vendor_id,
            "name": v.name,
            "category": v.category,
        }
        for v in vendors
    ]
    return JsonResponse(data, safe=False)
   
@csrf_exempt
def api_logout(request):
    if request.method != "POST":
        return JsonResponse({"detail": "POST required"}, status=400)

    logout(request)
    return JsonResponse({"message": "Logged out"})