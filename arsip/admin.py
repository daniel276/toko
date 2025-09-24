from django.contrib import admin

from arsip.models import Arsip, ArsipLog

# Register your models here.
admin.site.register(Arsip)

class ArsipAdmin(admin.ModelAdmin):
    list_display = ('nota_receipt_id', 'nota_cust_name', 'nota_date', 'status')
    search_fields = ('nota_receipt_id', 'nota_cust_name')
    list_filter = ('status', 'nota_date')

@admin.register(ArsipLog)
class ArsipLogAdmin(admin.ModelAdmin):
    list_display = ('arsip', 'action', 'old_status', 'new_status', 'operator', 'timestamp')
    list_filter  = ('action', 'old_status', 'new_status', 'timestamp')
    search_fields = ('arsip__nota_receipt_id', 'arsip__nota_cust_name', 'operator__username')
