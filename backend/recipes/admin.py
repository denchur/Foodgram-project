from django.contrib import admin

from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)


class IngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags', )
    inlines = [
        IngredientsInline,
    ]
    list_filter = ('name', 'author', 'tags')
    list_display = ('name', 'author', 'count_favorites')

    @admin.display(description='Подсчет избранных рецептов')
    def count_favorites(self, obj):
        return obj.favorites.count()


class IngredientsAdmin(admin.ModelAdmin):
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    search_fields = ('slug',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_filter = ('amount',)
    search_fields = ('ingredient',)


class CartAdmin(admin.ModelAdmin):
    list_filter = ('user', 'recipe')
    search_fields = ('user', )


class FavoriteAdmin(admin.ModelAdmin):
    list_filter = ('user', 'recipe')
    search_fields = ('user', )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
