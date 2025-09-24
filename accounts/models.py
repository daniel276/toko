from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('supervisor', 'Supervisor'),
    ('staff', 'Staff'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    pin_code = models.CharField(max_length=4, blank=True, null=True)

@receiver(post_save, sender=CustomUser)
def sync_role_group(sender, instance, created, **kwargs):
    """Setiap kali user dibuat/diupdate, pastikan group-nya sesuai role."""
    # pastikan group role ada (aman kalau sudah ada)
    role_group, _ = Group.objects.get_or_create(name=instance.role)

    # hapus semua group role yang lain
    for gname in ('admin', 'supervisor', 'staff'):
        if gname != instance.role:
            try:
                g = Group.objects.get(name=gname)
                instance.groups.remove(g)
            except Group.DoesNotExist:
                pass

    # pastikan group sesuai role terpasang
    instance.groups.add(role_group)
