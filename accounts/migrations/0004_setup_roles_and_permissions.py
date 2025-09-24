from django.db import migrations

def setup_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Ganti ini dengan daftar model yang mau kamu atur permission-nya
    target_models = [
        ('arsip', 'Arsip'),  # contoh
    ]

    # Helper ambil semua permission relevan untuk satu model
    def perms_for_model(app_label, model_name, extra_codenames=None):
        ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
        base_codes = ['view_' + model_name.lower(), 'add_' + model_name.lower(),
                      'change_' + model_name.lower(), 'delete_' + model_name.lower()]
        codenames = base_codes + (extra_codenames or [])
        found = []
        for code in codenames:
            try:
                found.append(Permission.objects.get(content_type=ct, codename=code))
            except Permission.DoesNotExist:
                # silent skip kalau belum ada (misal custom permission belum didefinisikan)
                pass
        return found

    # Kumpulkan permission untuk tiap role
    staff_perms = []
    spv_perms = []
    admin_perms = []

    for app_label, model_name in target_models:
        # Tambahkan custom permission di sini kalau kamu punya
        # Contoh: approve_arsip, mark_returned
        extras = ['posting_arsip', 'ganti_nota', 'retur_nota', 'tarik_nota', 'request_posting']  # hapus kalau tidak dipakai
        model_perms = perms_for_model(app_label, model_name, extras)

        # Mapping simple:
        # staff: view
        # supervisor: view + change (+ custom ops yang relevan)
        # admin: semua yang ada
        for p in model_perms:
            code = p.codename
            if code.startswith('view_'):
                staff_perms.append(p)
                spv_perms.append(p)
                admin_perms.append(p)
            elif code.startswith('add_') or code.startswith('change_'):
                spv_perms.append(p)
                admin_perms.append(p)
            else:
                # delete_*, custom seperti approve_arsip/mark_returned kita kasih supervisor + admin
                spv_perms.append(p)
                admin_perms.append(p)

    # Buat/isi group
    staff, _ = Group.objects.get_or_create(name='staff')
    supervisor, _ = Group.objects.get_or_create(name='supervisor')
    admin_g, _ = Group.objects.get_or_create(name='admin')

    staff.permissions.set(staff_perms)
    supervisor.permissions.set(spv_perms)
    admin_g.permissions.set(admin_perms)

class Migration(migrations.Migration):
    dependencies = [
        ('arsip', '0006_auto_20250924_1237'),  # pastikan setelah model dibuat
        ('accounts', '0003_auto_20250917_1331'), # jika accounts adalah app untuk CustomUser
        ('auth', '0012_alter_user_first_name_max_length')
    ]
    operations = [
        migrations.RunPython(setup_groups),
    ]