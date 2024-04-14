import django.dispatch

""" Required args: mutation """
mutation_created = django.dispatch.Signal()
""" Required args: mutation, old_is_approved, new_is_approved """
mutation_updated = django.dispatch.Signal()
