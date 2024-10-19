from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from django_jalali.db import models as jmodels
from django.contrib.auth.validators import UnicodeUsernameValidator
from .managers import OperatorManager, PersonalManager


# Local Imports

# Models


class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'department'

    def __str__(self) -> str:
        return self.name


class Operator(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        "username",
        max_length=150,
        unique=True,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[username_validator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    name = models.CharField(max_length=50)
    family = models.CharField(max_length=50)
    NID = models.CharField(max_length=10)
    PID = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=11)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    job = models.CharField(max_length=50)
    expire = jmodels.jDateField()

    is_staff = models.BooleanField(default=False)
    date_joined = jmodels.jDateTimeField(auto_now_add=True)

    is_deleted = models.BooleanField(default=False)

    objects = OperatorManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('name', 'family', 'NID', 'PID', 'phone', 'job', 'expire', )

    class Meta:
        db_table = 'operator_reg'

    def __str__(self) -> str:
        return self.name
    

class OperatorLog(models.Model):
    STATE_CHOICES = (
        ('exit', 'Exit'),
        ('entry', 'Entry')
    )

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT)
    
    date_in = jmodels.jDateField()
    time_in = models.TimeField()

    date_out = jmodels.jDateField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES)

    class Meta:
        db_table = 'operator_log'

    def __str__(self) -> str:
        return self.operator.family


class Communication(models.Model):
    cam_enable = models.BooleanField(max_length=1, default=0)
    finger_enable = models.BooleanField(max_length=1, default=0)
    rfid_enable = models.BooleanField(max_length=1, default=0)
    total_enable = models.BooleanField(max_length=1, default=0)
    cam_active = models.BooleanField(max_length=1, default=0)
    get_image = models.BooleanField(max_length=1, default=0)
    finger_active = models.BooleanField(max_length=1, default=0)
    get_finger = models.BooleanField(max_length=1, default=0)
    register = models.BooleanField(max_length=1, default=0)
    PID = models.CharField(max_length=10, blank=True, null=True)
    port = models.CharField(max_length=6, blank=True, null=True, default='8002')
    permit = models.BooleanField(max_length=1, default=0)
    open_door = models.BooleanField(max_length=1, default=0)
    alarm1 = models.BooleanField(max_length=1, default=0)
    alarm2 = models.BooleanField(max_length=1, default=0)
    register_end = models.BooleanField(max_length=1, default=0)
    delete_req = models.BooleanField(max_length=1, default=0)


    class Meta:
        db_table = 'communication'

    def __str__(self) -> str:
        return self.PID or "Communication"


class Personal(models.Model):
    name = models.CharField(max_length=50)
    family = models.CharField(max_length=50)
    PID = models.CharField(max_length=20, unique=True)
    shift = models.JSONField(max_length=150)
    position = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    type = models.CharField(max_length=50)

    permit = models.JSONField(max_length=200)

    permit_date_start = jmodels.jDateField()
    permit_date_stop = jmodels.jDateField()

    permit_time_start = models.TimeField()
    permit_time_stop = models.TimeField()

    phone = models.CharField(max_length=11)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT)

    parent_id = models.CharField(max_length=20, default=None, blank=True, null=True)
    certify = models.BooleanField(max_length=1, default=0)

    first_editor = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True, related_name='persoanl_first_editor')
    second_editor = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True, related_name='persoanl_second_editor')

    date_joined = jmodels.jDateTimeField(auto_now_add=True)

    is_deleted = models.BooleanField(default=False)

    objects = PersonalManager()

    class Meta:
        db_table = 'personal_reg'

    def __str__(self) -> str:
        return self.name
    

class PersonalLog(models.Model):
    STATE_CHOICES = (
        ('exit', 'Exit'),
        ('entry', 'Entry')
    )

    personal = models.ForeignKey(Personal, on_delete=models.PROTECT)

    date_in = jmodels.jDateField(default="1400-01-01")
    time_in = models.TimeField(blank=True, null=True)
    date_out = jmodels.jDateField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)

    state = models.CharField(max_length=20, choices=STATE_CHOICES)

    class Meta:
        db_table = 'personal_log'

    def __str__(self) -> str:
        return self.personal.family
    
class Log(models.Model):
    PID = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    check_req = models.BooleanField(max_length=1, default=0)
    check_ok = models.BooleanField(max_length=1, default=0)
    check_nok = models.BooleanField(max_length=1, default=0)
    access_control = models.BooleanField(max_length=1, default=0) 

class DoorOpenLog(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.PROTECT)
    dt = jmodels.jDateTimeField()

    def __str__(self) -> str:
        return self.operator.name