"""Переменные для моделей приложения recipes."""

"""verbose_name для модели Ingredients."""
ingredient_name: str = 'Наименование ингредиента'
ingredient_measurement_unit: str = 'Единица измерения'

"""verbose_name полей для модели Tag"""
tag_color: str = 'Цвет тэга'
tag_title: str = 'Название тэга'
tag_slug: str = 'Адрес тэга'

"""verbose_name полей для модели Recipe"""
recipe_author: str = 'Автор рецепта'
recipe_name: str = 'Название рецепта'
recipe_tag: str = 'Тэг рецепта'
recipe_desc: str = 'Описание рецепта'
recipe_cooking_time: str = 'Время приготовления'
recipe_ingredients: str = 'Ингредиенты рецепта'
recipe_created: str = 'Дата публикации рецепта'
recipe_image: str = 'Фото блюда'

"""verbose_name полей промежуточной модели IngredientsForRecipe"""
ingredient_quantity = 'Количество'

"""verbose_name полей модели ShopingCart."""
cart_recipes_verbose = 'Рецепты в корзине'
cart_owner_verbose = 'Владелец корзины'
cart_comment_verbose = 'Комментарий к списку покупок'

"""verbose_name полей модели Favorite"""
favorite_author = 'Автор рецепта'
favorite_recipe = 'Избранное'

"""verbose_name Meta класса моделей"""
ingredient_singular = 'Ингредиент'
ingredient_plural = 'Ингредиенты'
cart_singular = 'Список покупок'
ingredient_for_recipe_singular = 'Ингредиент для рецепта'
ingredient_for_recipe_plural = 'Ингредиенты для рецепта'
cart_plural = 'Списки покупок'
favorite_singular = 'Избранный рецепт'
favorite_plural = 'Избранные рецепты'
recipe_singular = 'Рецепт'
recipe_plural = 'Рецепты'
tag_singular = 'Тэг'
tag_plural = 'Тэги'

"""help_text для модели Tag"""
tag_color_help = 'Введите цвет тэга в формате HEX-Кода например #49B64E'
tag_title_help = 'Введите название тэга'
tag_slug_help = 'Введите короткий адрес(не более 15 символов)'

"""help_text для модели Recipe"""
recipe_cooking_time_help = 'Введите время приготовления в минутах'
recipe_desc_help = 'Кратко опишите рецепт, либо процесс приготовления'
recipe_tag_help = 'Выберете один или несколько тэгов'
recipe_image_help = 'Добавьте фото блюда'
recipe_ingredients_help = 'Выберите ингредиенты из списка'
recipe_name_help = 'Введите название рецепта'

"""help_text для модели IngredientsForRecipe."""
qauntity_help_text = 'Введите количество ингредиента'

"""Validators"""
invalid_hex_message = (
    'Значение "%(value)s", не является HEX-значением, '
    'введите значение в формате #AAFF09'
)

regex_validate = r'^#(?:[0-9a-fA-F]{3}){1,2}$'

"""message валидаторов полей модели Recipe"""
max_value_cooking_time = 'Значение не может быть больше 400.'
min_value_cooking_time = 'Значение не может быть меньше 1.'

"""message валидаторов полей модели IngredientsForRecipe"""
min_value_amount = 'Значение не может быть меньше нуля'
max_value_amount = 'Введите значение не более 100000'
