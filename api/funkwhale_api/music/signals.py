import django.dispatch

""" Required args: old_status, new_status, upload """
upload_import_status_updated = django.dispatch.Signal()
