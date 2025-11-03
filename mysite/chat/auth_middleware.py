from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
import urllib.parse
from django.db import close_old_connections

@database_sync_to_async
def get_user_from_token(token_key):
    # Close old database connections to prevent chaos in async code
    close_old_connections()
    try:
        access_token = AccessToken(token_key)
        user_id = access_token.payload.get('user_id')

        if user_id:
            user_id = int(user_id)
        User = get_user_model()
        return User.objects.get(id=user_id)
    except Exception as e:
        # InvalidToken or User.DoesNotExist
        print(f"Token authentication failed: {e}")
        return AnonymousUser()


class TokenAuthMiddleware:
    """
    Custom middleware to authenticate user using a 'token' query parameter in the URL.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        try:
            query_string = scope.get('query_string', b'').decode()
            query_params = urllib.parse.parse_qs(query_string)
            token = query_params.get('token', [None])[0]

            if token:
                user_obj = await get_user_from_token(token)
                scope['user'] = user_obj
                print(f"!!! Debug (Auth): User Authenticated? {user_obj.is_authenticated}(user_obj.username if user_obj.is_authenticated else 'None')!!!")
            else:
                scope['user'] = AnonymousUser()
                print("No token provided or invalid token")
        except Exception as e:
            print(f"Auth middleware error: {e}")
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)

# Combine with AuthMiddlewareStack
def TokenAuthMiddlewareStack(inner):
    return AuthMiddlewareStack(TokenAuthMiddleware(inner))