from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cart.models import CartItem
from apps.cart.serializers import (
    CartItemCreateSerializer,
    CartItemSerializer,
    CartItemUpdateSerializer,
    CartSerializer,
)
from apps.cart.services import add_item_to_cart, clear_cart, get_cart_payload, update_cart_item_quantity


class CartView(APIView):
    @extend_schema(responses=CartSerializer)
    def get(self, request):
        payload = get_cart_payload(request.user)
        serializer = CartSerializer(payload)
        return Response(serializer.data)


class CartItemViewSet(viewsets.ModelViewSet):
    http_method_names = ["post", "patch", "delete"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return CartItem.objects.none()
        return CartItem.objects.select_related("product").filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return CartItemCreateSerializer
        if self.action == "partial_update":
            return CartItemUpdateSerializer
        return CartItemSerializer

    @extend_schema(request=CartItemCreateSerializer, responses=CartItemSerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = add_item_to_cart(user=request.user, **serializer.validated_data)
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=CartItemUpdateSerializer, responses=CartItemSerializer)
    def partial_update(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        item = update_cart_item_quantity(item=item, **serializer.validated_data)
        return Response(CartItemSerializer(item).data)

    @action(detail=False, methods=["delete"], url_path="clear")
    def clear(self, request):
        clear_cart(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
