from distutils.command.install_egg_info import safe_name
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Arsip, ArsipLog
from .utils.current_user import get_current_user

@receiver(pre_save, sender=Arsip)
def arsip_capture_old_status(sender, instance: Arsip, **kwargs):
    """
    Simpan old_status di instance sementara sebelum disave,
    supaya di post_save kita bisa bandingkan.
    """
    if instance.pk:
        try:
            old = Arsip.objects.get(pk=instance.pk)
            instance._old_status = old.nota_status
        except Arsip.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None
        
@receiver(post_save, sender=Arsip)
def arsip_log_create_or_change(sender, instance: Arsip, created, **kwargs):
    user = get_current_user()
    
    if created:
        ArsipLog.objects.create(
            arsip = instance,
            action = 'create',
            old_status = None,
            new_status = instance.nota_status,
            operator = user
        )
        return  

    old_status = getattr(instance, '_old_status', None)
    new_status = instance.nota_status
    
    #kalau status berubah -> tulis log status_change
    if old_status != new_status:
        ArsipLog.objects.create(
            arsip = instance,
            action = 'status_change',
            old_status = old_status,
            new_status = new_status,
            operator = user
        )
    else:
        # Non-status update (opsional): kalau mau log semua update lain
        # ArsipLog.objects.create(
        #     arsip=instance, action='update', actor=user, note='Arsip updated without status change'
        # )
        pass
    
@receiver(post_delete, sender=Arsip) # i think this will not be used in application
def arsip_log_delete(sender, instance: Arsip, **kwargs):
    user = get_current_user
    ArsipLog.objects.create(
        arsip = instance, # ini akan gagal kalau CASCADE? Tidak, instance masih ada di memori tapi FK sudah terhapus.
        action = 'delete',
        old_status =getattr(instance, 'status', None),
        new_status = None,
        operator = user
    )