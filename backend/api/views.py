from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.download import download_card
from api.filters import RecipeFilter
from api.pagination import MyPageNumberPagination
from api.permissions import IsSuperUserOrOwnerOrReadOnly
from api.serializers import (AddRecipeSerializer, AddToFavoriteSerializer,
                             AddToShoppingCartSerializer,
                             CreateFollowSerializer, CustomUserSerializer,
                             FollowSerializer, IngredientSerializer,
                             RecipeSerializer, TagSerializer)
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from users.models import Follow

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    pagination_class = MyPageNumberPagination

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user_id = request.user.id
        author_id = self.kwargs.get('id')
        data = {
            'user': user_id,
            'author': author_id
        }
        serializer = CreateFollowSerializer(
            data=data,
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def unfolow(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        if not Follow.objects.filter(user=user, author=author).exists():
            return Response(
                {'recipe': 'Вы не подписывались на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        get_object_or_404(
            Follow,
            user=user,
            author=author
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        subs = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )
        serializer = FollowSerializer(
            subs,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsSuperUserOrOwnerOrReadOnly,)
    pagination_class = MyPageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeSerializer
        return AddRecipeSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        cart = Cart.objects.filter(user=request.user).values(
            'recipe__ingredients_recipe__ingredient__name',
            'recipe__ingredients_recipe__ingredient__measurement_unit'
        ).annotate(total_amount=Sum('recipe__ingredients_recipe__amount'))
        shopping_list = download_card(cart)
        return HttpResponse(shopping_list, content_type='text/plain')

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        user_id = request.user.id
        recipe_id = pk
        data = {
            'user': user_id,
            'recipe': recipe_id
        }
        serializer = AddToFavoriteSerializer(
            data=data,
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def unfavorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'recipe': 'Вы не добавляли этот рецепт в изюранное'},
                status=status.HTTP_400_BAD_REQUEST
            )
        get_object_or_404(
            Favorite,
            user=user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        user_id = request.user.id
        recipe_id = pk
        data = {
            'user': user_id,
            'recipe': recipe_id
        }
        serializer = AddToShoppingCartSerializer(
            data=data,
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if not Cart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'recipe': 'Вы не добавляли этот рецепт в корзину'},
                status=status.HTTP_400_BAD_REQUEST
            )
        get_object_or_404(
            Cart,
            user=user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredintViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)
