from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = None 
    first_name = None 
    last_name = None 
    
    # U_USERID
    id = models.AutoField(
        primary_key=True, 
        db_column='U_USERID'
    )
    # U_EMAIL
    email = models.EmailField(
        unique=True, 
        max_length=255, 
        db_column='U_EMAIL'
    )
    # U_NAME 
    name = models.CharField(
        max_length=25, 
        db_column='U_NAME'
    )
    # U_PHONE 
    phone = models.CharField(
        max_length=15, 
        db_column='U_PHONE'
    )
    # U_PASSWORD
    password = models.CharField(
        max_length=128, 
        db_column='U_PASSWORD'
    )
    # U_TOTALPOINTS
    total_points = models.IntegerField(
        default=0, 
        db_column='U_TOTALPOINTS'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    class Meta:
        db_table = 'USERS'

    def __str__(self):
        return f"{self.name} ({self.email})"

class Vendor(models.Model):
    # V_VENDORID
    vendor_id = models.AutoField(
        primary_key=True, 
        db_column='V_VENDORID'
    )
    # V_NAME
    name = models.CharField(
        max_length=35, 
        db_column='V_NAME'
    )
    # V_CATEGORY
    category = models.CharField(
        max_length=15, 
        db_column='V_CATEGORY'
    )

    class Meta:
        db_table = 'VENDORS'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'

    def __str__(self):
        return self.name


class UserTransaction(models.Model):
    # T_TRANSID
    trans_id = models.AutoField(
        primary_key=True, 
        db_column='T_TRANSID'
    )
    # T_USERID
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        db_column='T_USERID'
    )
    # T_VENDORID 
    vendor = models.ForeignKey(
        Vendor, 
        on_delete=models.CASCADE, 
        db_column='T_VENDORID'
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
        db_column='T_TYPE'
    )
    # T_AMOUNT (DECIMAL(15,2))
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        db_column='T_AMOUNT'
    )
    # T_LOCATION
    location = models.CharField(
        max_length=50, 
        db_column='T_LOCATION'
    )
    # T_DATE
    date = models.DateField(db_column='T_DATE')

    class Meta:
        db_table = 'USER_TRANSACTIONS'
        verbose_name = 'User Transaction'
        verbose_name_plural = 'User Transactions'

    def __str__(self):
        return f"{self.user.name} - {self.vendor.name} - {self.amount}"


class Reward(models.Model):
    # R_REWARDID
    reward_id = models.AutoField(
        primary_key=True, 
        db_column='R_REWARDID'
    )
    # R_USERID
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        db_column='R_USERID'
    )
    # R_VENDORID
    vendor = models.ForeignKey(
        Vendor, 
        on_delete=models.CASCADE, 
        db_column='R_VENDORID'
    )
    # R_BALANCE (DECIMAL(8,2))
    balance = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        db_column='R_BALANCE'
    )
    # R_EXPIRATION
    expiration = models.DateField(
        db_column='R_EXPIRATION'
    )

    class Meta:
        db_table = 'REWARDS'
        verbose_name = 'Reward'
        verbose_name_plural = 'Rewards'

    def __str__(self):
        return f"{self.user.name} Credit @ {self.vendor.name}: ${self.balance}"


class Ledger(models.Model):
    # L_LEDGERID
    ledger_id = models.AutoField(
        primary_key=True, 
        db_column='L_LEDGERID'
    )
    # L_USERID
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        db_column='L_USERID'
    )
    # L_TRANSID
    transaction = models.ForeignKey(
        UserTransaction, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        db_column='L_TRANSID'
    )
    # L_CHANGEAMT
    change_amount = models.IntegerField(
        db_column='L_CHANGEAMT'
    )
    # L_REASON
    reason = models.CharField(
        max_length=20, 
        db_column='L_REASON'
    )
    # L_DATE
    date = models.DateField(
        db_column='L_DATE'
    )
    # L_EXPIRATION
    expiration_date = models.DateField(
        null=True, 
        blank=True, 
        db_column='L_EXPIRATION'
    )

    class Meta:
        db_table = 'LEDGER'
        verbose_name = 'Ledger Entry'
        verbose_name_plural = 'Ledger Entries'

    def __str__(self):
        return f"{self.user.name}: {self.change_amount} pts ({self.reason})"
