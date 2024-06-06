import os

from drf_spectacular.contrib.django_oauth_toolkit import (
    DjangoOAuthToolkitScheme,
    OpenApiAuthenticationExtension,
)
from drf_spectacular.extensions import (
    OpenApiSerializerExtension,
    OpenApiSerializerFieldExtension,
)
from drf_spectacular.plumbing import (
    OpenApiTypes,
    build_basic_type,
    build_bearer_security_scheme_object,
)


class CustomRelatedFieldScheme(OpenApiSerializerFieldExtension):
    target_class = "funkwhale_api.common.serializers.RelatedField"
    match_subclasses = True

    def map_serializer_field(self, auto_schema, direction):
        if direction == "request":
            return build_basic_type(OpenApiTypes.UUID)
        elif direction == "response" and self.target.serializer:
            component = auto_schema.resolve_serializer(
                self.target.serializer, direction
            )
            return component.ref
        else:
            # happens for
            # UserViewSet: UserWriteSerializer: not sure how this works for: avatar
            # AlbumViewSet: AlbumCreateSerializer: not sure how this works for: artist
            return build_basic_type(OpenApiTypes.UUID)


class PreferenceSerializerScheme(OpenApiSerializerExtension):
    target_class = "dynamic_preferences.api.serializers.PreferenceSerializer"
    match_subclasses = True

    def map_serializer(self, auto_schema, direction):
        from dynamic_preferences.api.serializers import PreferenceSerializer

        class Fix(PreferenceSerializer):
            def get_default(self, o) -> str:
                pass

            def get_verbose_name(self, o) -> str:
                pass

            def get_identifier(self, o) -> str:
                pass

            def get_help_text(self, o) -> str:
                pass

            def get_additional_data(self, o) -> dict:
                pass

            def get_field(self, o) -> dict:
                pass

        return auto_schema._map_serializer(Fix, direction, bypass_extensions=True)


class CustomOAuthScheme(DjangoOAuthToolkitScheme):
    target_class = "funkwhale_api.common.authentication.OAuth2Authentication"

    def get_security_requirement(self, auto_schema):
        from funkwhale_api.users.oauth.permissions import (
            METHOD_SCOPE_MAPPING,
            ScopePermission,
        )

        for permission in auto_schema.view.get_permissions():
            if isinstance(permission, ScopePermission):
                scope_config = getattr(auto_schema.view, "required_scope", "noopscope")

                if isinstance(scope_config, str):
                    scope_config = {
                        "read": f"read:{scope_config}",
                        "write": f"write:{scope_config}",
                    }
                    action = METHOD_SCOPE_MAPPING[
                        auto_schema.view.request.method.lower()
                    ]
                    required_scope = scope_config[action]
                else:
                    required_scope = scope_config[auto_schema.view.action]

                return {self.name: [required_scope]}


class CustomApplicationTokenScheme(OpenApiAuthenticationExtension):
    target_class = "funkwhale_api.common.authentication.ApplicationTokenAuthentication"
    name = "ApplicationToken"

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name="Authorization",
            token_prefix="Bearer",
        )


def custom_preprocessing_hook(endpoints):
    filtered = []

    # your modifications to the list of operations that are exposed in the schema
    api_type = os.environ.get("API_TYPE", "v1")

    for path, path_regex, method, callback in endpoints:
        if path.startswith("/api/v1/providers"):
            continue

        if path.startswith("/api/v1/users/users"):
            continue

        if path.startswith("/api/v1/oauth/authorize"):
            continue

        if path.startswith(f"/api/{api_type}"):
            filtered.append((path, path_regex, method, callback))

    return filtered
