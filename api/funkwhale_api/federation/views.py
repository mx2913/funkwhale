from django import forms
from django.conf import settings
from django.core import paginator
from django.http import HttpResponse
from django.urls import reverse

from rest_framework import viewsets
from rest_framework import views
from rest_framework import response
from rest_framework.decorators import list_route, detail_route

from funkwhale_api.music.models import TrackFile
from funkwhale_api.music.serializers import AudioSerializer

from . import actors
from . import authentication
from . import permissions
from . import renderers
from . import serializers
from . import utils
from . import webfinger


class FederationMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not settings.FEDERATION_ENABLED:
            return HttpResponse(status=405)
        return super().dispatch(request, *args, **kwargs)


class InstanceActorViewSet(FederationMixin, viewsets.GenericViewSet):
    lookup_field = 'actor'
    lookup_value_regex = '[a-z]*'
    authentication_classes = [
        authentication.SignatureAuthentication]
    permission_classes = []
    renderer_classes = [renderers.ActivityPubRenderer]

    def get_object(self):
        try:
            return actors.SYSTEM_ACTORS[self.kwargs['actor']]
        except KeyError:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        system_actor = self.get_object()
        actor = system_actor.get_actor_instance()
        data = actor.system_conf.serialize()
        return response.Response(data, status=200)

    @detail_route(methods=['get', 'post'])
    def inbox(self, request, *args, **kwargs):
        system_actor = self.get_object()
        handler = getattr(system_actor, '{}_inbox'.format(
            request.method.lower()
        ))

        try:
            data = handler(request.data, actor=request.actor)
        except NotImplementedError:
            return response.Response(status=405)
        return response.Response(data, status=200)

    @detail_route(methods=['get', 'post'])
    def outbox(self, request, *args, **kwargs):
        system_actor = self.get_object()
        handler = getattr(system_actor, '{}_outbox'.format(
            request.method.lower()
        ))
        try:
            data = handler(request.data, actor=request.actor)
        except NotImplementedError:
            return response.Response(status=405)
        return response.Response(data, status=200)


class WellKnownViewSet(FederationMixin, viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []
    renderer_classes = [renderers.WebfingerRenderer]

    @list_route(methods=['get'])
    def webfinger(self, request, *args, **kwargs):
        try:
            resource_type, resource = webfinger.clean_resource(
                request.GET['resource'])
            cleaner = getattr(webfinger, 'clean_{}'.format(resource_type))
            result = cleaner(resource)
        except forms.ValidationError as e:
            return response.Response({
                'errors': {
                    'resource': e.message
                }
            }, status=400)
        except KeyError:
            return response.Response({
                'errors': {
                    'resource': 'This field is required',
                }
            }, status=400)

        handler = getattr(self, 'handler_{}'.format(resource_type))
        data = handler(result)

        return response.Response(data)

    def handler_acct(self, clean_result):
        username, hostname = clean_result
        actor = actors.SYSTEM_ACTORS[username].get_actor_instance()
        return serializers.ActorWebfingerSerializer(actor).data


class MusicFilesViewSet(FederationMixin, viewsets.GenericViewSet):
    authentication_classes = [
        authentication.SignatureAuthentication]
    permission_classes = [permissions.LibraryFollower]
    renderer_classes = [renderers.ActivityPubRenderer]

    def list(self, request, *args, **kwargs):
        page = request.GET.get('page')
        library = actors.SYSTEM_ACTORS['library'].get_actor_instance()
        qs = TrackFile.objects.order_by('-creation_date')
        if page is None:
            conf = {
                'id': utils.full_url(reverse('federation:music:files-list')),
                'page_size': settings.FEDERATION_COLLECTION_PAGE_SIZE,
                'items': qs,
                'item_serializer': AudioSerializer,
                'actor': library,
            }
            serializer = serializers.PaginatedCollectionSerializer(conf)
            data = serializer.data
        else:
            try:
                page_number = int(page)
            except:
                return response.Response(
                    {'page': ['Invalid page number']}, status=400)
            p = paginator.Paginator(
                qs, settings.FEDERATION_COLLECTION_PAGE_SIZE)
            try:
                page = p.page(page_number)
            except paginator.EmptyPage:
                return response.Response(status=404)
            conf = {
                'id': utils.full_url(reverse('federation:music:files-list')),
                'page': page,
                'item_serializer': AudioSerializer,
                'actor': library,
            }
            serializer = serializers.CollectionPageSerializer(conf)
            data = serializer.data

        return response.Response(data)
