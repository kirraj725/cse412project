from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, phone, password=None, **extra_fields):
        """Create a regular user with email instead of username."""
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=name,
            phone=phone,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, password=None, **extra_fields):
        """Create a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        
        return self.create_user(email, name, phone, password, **extra_fields)


class User(AbstractUser):
    username = None 
    first_name = None 
    last_name = None 
    
    # U_USERID
    id = models.AutoField(
        primary_key=True, 
        db_column='u_userid'
    )
    # U_EMAIL
    email = models.EmailField(
        unique=True, 
        max_length=255, 
        db_column='u_email'
    )
    # U_NAME 
    name = models.CharField(
        max_length=25, 
        db_column='u_name'
    )
    # U_PHONE 
    phone = models.CharField(
        max_length=15, 
        db_column='u_phone'
    )
    # U_PASSWORD
    password = models.CharField(
        max_length=128, 
        db_column='u_password'
    )
    # U_TOTALPOINTS
    total_points = models.IntegerField(
        default=0, 
        db_column='u_totalpoints'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.name} ({self.email})"

class Vendor(models.Model):
    # V_VENDORID
    vendor_id = models.AutoField(
        primary_key=True, 
        db_column='v_vendorid'
    )
    # V_NAME
    name = models.CharField(
        max_length=35, 
        db_column='v_name'
    )
    # V_CATEGORY
    category = models.CharField(
        max_length=15, 
        db_column='v_category'
    )

    class Meta:
        db_table = 'vendors'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'

    def __str__(self):
        return self.name


class UserTransaction(models.Model):
    # T_TRANSID
    trans_id = models.AutoField(
        primary_key=True, 
        db_column='t_transid'
    )
    # T_USERID
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        db_column='t_userid'
    )
    # T_VENDORID 
    vendor = models.ForeignKey(
        Vendor, 
        on_delete=models.CASCADE, 
        db_column='t_vendorid'
    )
    # T_TYPE
    # we use choices here to enforce data integrity in the app layer
    TRANSACTION_TYPES = [
        ('PURCHASE', 'Purchase'),
        ('REFUND', 'Refund')
    ]
    transaction_type = models.CharField(
        max_length=10, 
        choices=TRANSACTION_TYPES,
        db_column='t_type'
    )
    # T_AMOUNT (DECIMAL(15,2))
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        db_column='t_amount'
    )
    # T_LOCATION
    location = models.CharField(
        max_length=50, 
        db_column='t_location'
    )
    # T_DATE
    date = models.DateField(db_column='t_date')

    class Meta:
        db_table = 'user_transactions'
        verbose_name = 'User Transaction'
        verbose_name_plural = 'User Transactions'

    def __str__(self):
        return f"{self.user.name} - {self.vendor.name} - {self.amount}"


class Reward(models.Model):
    # R_REWARDID
    reward_id = models.AutoField(
        primary_key=True, 
        db_column='r_rewardid'
    )
    # R_USERID
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        db_column='r_userid'
    )
    # R_VENDORID
    vendor = models.ForeignKey(
        Vendor, 
        on_delete=models.CASCADE, 
        db_column='r_vendorid'
    )
    # R_BALANCE (DECIMAL(8,2))
    balance = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        db_column='r_balance'
    )
    # R_EXPIRATION
    expiration = models.DateField(
        db_column='r_expiration'
    )

    class Meta:
        db_table = 'rewards'
        verbose_name = 'Reward'
        verbose_name_plural = 'Rewards'

    def __str__(self):
        return f"{self.user.name} Credit @ {self.vendor.name}: ${self.balance}"


class Ledger(models.Model):
    # L_LEDGERID
    ledger_id = models.AutoField(
        primary_key=True, 
        db_column='l_ledgerid'
    )
    # L_USERID
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        db_column='l_userid'
    )
    # L_TRANSID
    transaction = models.ForeignKey(
        UserTransaction, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        db_column='l_transid'
    )
    # L_CHANGEAMT
    change_amount = models.IntegerField(
        db_column='l_changeamt'
    )
    # L_REASON
    reason = models.CharField(
        max_length=20, 
        db_column='l_reason'
    )
    # L_DATE
    date = models.DateField(
        db_column='l_date'
    )
    # L_EXPIRATION
    expiration_date = models.DateField(
        null=True, 
        blank=True, 
        db_column='l_expiration'
    )

    class Meta:
        db_table = 'ledger'
        verbose_name = 'Ledger Entry'
        verbose_name_plural = 'Ledger Entries'

    def __str__(self):
        return f"{self.user.name}: {self.change_amount} pts ({self.reason})"
