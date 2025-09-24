from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
import arsip
from arsip.models import Arsip


# Create your views here.

def is_admin(user):
    return user.is_staff

@login_required
def main_dashboard(request):
    queryset = Arsip.objects.all().order_by('-nota_date')
    
    paginator = Paginator(queryset, 10)
    page_num = request.GET.get('page', 1)
    arsip_page = paginator.get_page(page_num)
    
    context = {
        'arsip-list': arsip_page,
    }

    return render(request, 'arsip/main.html', context)


@login_required(login_url="/login/")
def arsip_list(request):
    queryset = Arsip.objects.all().order_by('-nota_date')

    search_name = request.GET.get('search_name')
    search_date = request.GET.get('nota_date')

    if search_name:
        queryset = queryset.filter(Q(nota_cust_name__icontains=search_name))

    if search_date:
        queryset = queryset.filter(nota_date=search_date)

    paginator = Paginator(queryset, 10)
    page_num = request.GET.get('page', 1)
    arsip_page = paginator.get_page(page_num)

    #this is to preserve filter for pagination links
    params = request.GET.copy()
    params.pop('page', None)
    querystring = params.urlencode()

    context = {
        'arsip_page': arsip_page,
        'search_name': search_name,
        'search_date': search_date,
        'querystring': querystring
    }

    return render(request, 'arsip/arsip_main.html', context)

@login_required(login_url="/login/")
def create_arsip_view(request):
    if request.method == 'POST':
        data = request.POST
        upload_date = data.get('upload_date')
        # nota_previous_id = data.get('nota_previous_id') buat baru jd no need
        nota_receipt_id = data.get('nota_receipt_id') # nomor struk / faktur
        nota_customer_name = data.get('nota_customer_name')
        nota_date = data.get('nota_date')
        nota_image = request.FILES.get('nota_image')
        nota_notes = data.get('nota_notes')
        # ganti_nota = data.get('ganti_nota') no need

        Arsip.objects.create(
            userUploader_id=request.user.id,
            nota_receipt_id=nota_receipt_id,
            nota_cust_name=nota_customer_name,
            nota_date=nota_date,
            nota_image_file=nota_image,
            nota_notes=nota_notes,
        )
    return render(request, 'arsip/create_arsip.html', { 'arsip': arsip})

def arsip_detail(request, id):
    arsip = Arsip.objects.get(id=id)
    
    logs = arsip.logs.filter(arsip=arsip).order_by('-timestamp', '-id')
    
    return render(request, 'arsip/arsip_detail.html', {'arsip': arsip, 'logs': logs})

@login_required
def request_tarik(request, id):
    arsip = get_object_or_404(Arsip, pk=id)
    # Opsional: batasi siapa yg boleh "tarik nota"
    # if not request.user.groups.filter(name='staff').exists() and request.user.role != 'staff':
    #     messages.error(request, "Anda tidak berhak melakukan aksi ini.")
    #     return redirect('arsip:arsip-detail', pk=pk)
    
    if arsip.nota_status in ['posted', 'requested']:
        messages.warning(request, f"Nota sudah berstatus {arsip.nota_status}.")
        return redirect('arsip:arsip-detail', id=id)
    
    if request.method == 'POST':
        pic = (request.POST.get('pic') or '').strip()
        # Ambil catatan dari modal (opsional)
        note = (request.POST.get('note') or '').strip()
    
    
    #ubah status ke requested
    old_status = arsip.nota_status
    arsip.nota_status = 'req_tarik_nota'
    arsip.nota_sudah_diambil = True
    arsip.save() # <--- signals akan menulis ArsipLog(action='status_change)
    
    #tambahkan catatan ke log terakhir (yang baru saja dibuat oleh signal)
    last_log = arsip.logs.filter(arsip=arsip).order_by('-timestamp', '-id').first()
    if last_log:
        extra = f"PIC: {pic}" if pic else None
        if extra:
            last_log.note = (last_log.note + " | " if last_log.note else "") + extra 
            last_log.save(update_fields=['note'])
    
    messages.success(request, 'Request tarik nota terkirim ke supervisor.')
    
    return redirect('arsip:arsip-detail', id=arsip.id)

@login_required
@transaction.atomic
def request_ganti(request, id):
    arsip_lama = get_object_or_404(Arsip, pk=id)

    # Batasi status yang boleh minta ganti nota
    if arsip_lama.nota_status in ['posted', 'requested']:
        messages.warning(request, f"Nota tidak dapat diajukan ganti pada status: {arsip_lama.nota_status}.")
        return redirect('arsip:arsip-detail', id=arsip_lama.id)

    if request.method != 'POST':
        messages.error(request, 'Metode tidak valid.')
        return redirect('arsip:arsip-detail', id=arsip_lama.id)

    if request.method == 'POST':
        pic = (request.POST.get('pic') or '').strip()
        new_receipt = (request.POST.get('new_receipt_id') or '').strip()
        new_cust_name = (request.POST.get('cust_name') or '').strip()

    if not new_receipt:
        messages.error(request, 'Nomor nota baru (new_receipt_id) wajib diisi.')
        return redirect('arsip:arsip-detail', id=arsip_lama.id)

    # (Opsional) jika nota_receipt_id harus unik, validasi di sini
    if Arsip.objects.filter(nota_receipt_id=new_receipt).exists():
        messages.error(request, f"Nomor nota {new_receipt} sudah dipakai.")
        return redirect('arsip:arsip-detail', id=arsip_lama.id)

    # 1) Ubah status arsip lama -> req_ganti_nota (signals akan tulis log)
    arsip_lama.nota_status = 'req_ganti_nota'
    arsip_lama.save(update_fields=['nota_status'])

    # Tambahkan catatan PIC ke log terbaru (status_change -> req_ganti_nota)
    last_log = arsip_lama.logs.filter(
        action='status_change', new_status='req_ganti_nota'
    ).order_by('-timestamp', '-id').first()
    if last_log:
        extras = []
        if pic:
            extras.append(f"PIC: {pic}")
        extras.append(f"Ganti ke receipt: {new_receipt}")
        extra_note = " | ".join(extras)
        last_log.note = (last_log.note + " | " if last_log.note else "") + extra_note
        last_log.save(update_fields=['note'])

    # 2) Buat Arsip baru (duplikasi field penting)
    arsip_baru = Arsip.objects.create(
        userUploader=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
        nota_previous_id=arsip_lama,          # link balik ke arsip lama
        nota_receipt_id=new_receipt,          # nomor nota baru
        nota_cust_name=new_cust_name,
        nota_date=arsip_lama.nota_date,
        nota_image_file=None,                 # biasanya upload ulang; kalau mau copy, handle manual di storage
        nota_pic=pic or arsip_lama.nota_pic,  # isi PIC baru jika ada
        nota_notes=arsip_lama.nota_notes,
        nota_status='unposted',                # status awal arsip baru
        ganti_nota=True
    )
    
    messages.success(request, f"Request ganti nota terkirim. Nota baru dibuat: {arsip_baru.nota_receipt_id}.")
    return redirect('arsip:arsip-detail', id=arsip_baru.id)  # atau balik ke arsip lama kalau mau

def request_retur(request, id):
    arsip_lama = get_object_or_404(Arsip, pk=id)

    if arsip.nota_status in ['posted', 'requested']:
        messages.warning(request, f"Nota sudah berstatus {arsip.nota_status}.")
        return redirect('arsip:arsip-detail', id=id)

    if request.method != 'POST':
        messages.error(request, 'Metode tidak valid.')
        return redirect('arsip:arsip-detail', id=arsip_lama.id)

    if request.method == 'POST':
        pic = (request.POST.get('pic') or '').strip()
        new_receipt = (request.POST.get('new_receipt_id') or '').strip()
        
     #ubah status ke requested
    old_status = arsip.nota_status
    arsip.nota_status = 'req_retur_nota'
    arsip.nota_sudah_diambil = True
    arsip.save() # <--- signals akan menulis ArsipLog(action='status_change)
    
    #tambahkan catatan ke log terakhir (yang baru saja dibuat oleh signal)
    last_log = arsip.logs.filter(arsip=arsip).order_by('-timestamp', '-id').first()
    if last_log:
        extra = f"PIC: {pic}" if pic else None
        if extra:
            last_log.note = (last_log.note + " | " if last_log.note else "") + extra 
            last_log.save(update_fields=['note'])
    
    messages.success(request, 'Request retur nota terkirim ke supervisor.')
    
    return redirect('arsip:arsip-detail', id=arsip.id)
    
    
@login_required
def approve_request(request, arsip_id):
    arsip = get_object_or_404(Arsip, pk=arsip_id)
    #validasi role supervisor disini
    
    # 2) Validasi status: hanya nota yang diminta tarik/ganti yg boleh di-approve
    if arsip.nota_status not in ['requested', 'req_ganti_nota']:
        messages.warning(request, f"Nota dengan status {arsip.nota_status} tidak bisa di-approve.")
        return redirect('arsip:arsip-detail', pk=arsip.pk)

    # 3) Ubah status jadi posted (atau sesuai alurmu)
    arsip.nota_status = 'posted'
    arsip.save()   # signals akan buat ArsipLog action='status_change'

    # 4) Tambahkan pesan feedback
    messages.success(request, f"Nota {arsip.nota_receipt_id} berhasil di-approve dan diposting.")

    return redirect('arsip:arsip-detail', pk=arsip.pk)

