from django.contrib.auth.models import User
import os, uuid
from django.db import models
from django.conf import settings

# Create your models here.

class Arsip(models.Model):

    class Meta:
        ordering = ['nota_date'] # TODO CHANGE THIS TOO ASCENDING LATER

    userUploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='userUploader')
    uploadDateTime = models.DateTimeField(auto_now_add=True)
    nota_previous_id = models.ForeignKey('Arsip', on_delete=models.CASCADE, null=True, blank=True, related_name='previous_id')
    nota_receipt_id = models.CharField(max_length=10, null=True, blank=True)
    nota_cust_name = models.CharField(max_length=100)
    nota_date = models.DateField(name="nota_date")
    nota_image_file = models.ImageField(upload_to="nota_image_file/", null=True, blank=True)
    nota_pic = models.CharField(max_length=30, null=True, blank=True)
    nota_notes = models.TextField(max_length=400, null=True, blank=True)
    nota_status = models.CharField(max_length=20, choices= [
        ('unposted', 'Belum Diposting'),
        ('req_tarik_nota', 'Request Posting: Tarik Nota'),
        ('req_ganti_nota', 'Request Posting: Ganti Nota'),
        ('req_retur_nota', 'Request Posting: Retur Nota'),
        ('posted', 'Sudah Diposting')
    ], default= 'unposted')
    ganti_nota = models.BooleanField(default=False)
    nota_sudah_diambil = models.BooleanField(default=False)
    nota_sudah_diambil_dateTime = models.DateTimeField(blank=True, null=True)
    nota_sudah_diambil_signer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nota_cust_name
    
    @property
    def nota_status_formatted(self):
        if self.nota_status == 'unposted': 
            return 'Belum Diposting'
        
        if self.nota_status == 'req_tarik_nota':
            return 'Request: Tarik Nota'
        
        if self.nota_status == 'req_ganti_nota':
            return 'Request: Ganti Nota'
        
        if self.nota_status == 'req_retur_nota':
            return 'Request: Retur Nota'
        
        if self.nota_status == 'posted':
            return 'Sudah Diposting'
    
    @property
    def nota_date_formatted(self):
        return self.nota_date.strftime("%d-%m-%Y")
    
    def nota_upload_to(instance, filename):
        # Get extension
        ext = filename.split('.')[-1]

        # Safe customer name
        safe_name = instance.nota_cust_name.replace(" ", "_")

        # Format date
        date_str = instance.nota_date.strftime("%Y%m%d") if instance.nota_date else "unknown"

        # Base filename
        base_filename = f"{safe_name}_{date_str}"
        
        # Short UUID (8 chars)
        short_uid = uuid.uuid4().hex[:8]

        # Build new filename
        new_filename = f"{safe_name}_{date_str}_{short_uid}.{ext}"

        return os.path.join("nota_image_file/", new_filename)

class ArsipLog(models.Model): 
    arsip = models.ForeignKey(Arsip, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('status_change', 'Ubah Status'),
            ('update', 'Diupdate'),
            ('delete', 'Hapus')
        ]
    )
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operator'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    @property
    def action_formatted(self):
        if self.action == 'status_change':
            return 'Perubahan Status'
        if 'pending':
            return 'Pending'
        if 'update':
            return 'Update'
        else:
            return '-'
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"[{self.action}] {self.arsip} {self.old_status} → {self.new_status} @ {self.timestamp}"
    
    
