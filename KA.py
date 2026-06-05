import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import ImageTk, Image, ImageDraw, ImageFont
from pathlib import Path
import requests
from io import BytesIO
import hashlib
import colorsys
import os
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple
from urllib.parse import urlparse
import threading
import re

# ==================== КОНСТАНТЫ ====================

# Создаем директории для изображений
IMAGE_DIR = Path("ingredient_images")
IMAGE_DIR.mkdir(exist_ok=True)

LOCAL_ICONS_DIR = Path("local_icons")
LOCAL_ICONS_DIR.mkdir(exist_ok=True)

RECIPE_IMAGES_DIR = Path("recipe_images")
RECIPE_IMAGES_DIR.mkdir(exist_ok=True)

# ПОЛНЫЙ СПИСОК ПРОДУКТОВ с указанием категории
ALL_INGREDIENTS_WITH_CATEGORIES = [
    # Овощи
    ('Картошка', 'Овощи'),
    ('Морковь', 'Овощи'),
    ('Свёкла', 'Овощи'),
    ('Капуста', 'Овощи'),
    ('Помидоры', 'Овощи'),
    ('Огурцы', 'Овощи'),
    ('Кабачки', 'Овочи'),
    ('Баклажаны', 'Овощи'),
    ('Чеснок', 'Овощи'),
    ('Лук репчатый', 'Овощи'),
    ('Зелень', 'Овощи'),
    ('Перец болгарский', 'Овощи'),
    ('Редис', 'Овощи'),
    ('Сельдерей', 'Овощи'),
    ('Шпинат', 'Овощи'),
    ('Салат листовой', 'Овощи'),
    ('Баклажан', 'Овощи'),
    
    # Мясо
    ('Говядина', 'Мясо'),
    ('Свинина', 'Мясо'),
    ('Курица', 'Мясо'),
    ('Индейка', 'Мясо'),
    ('Утка', 'Мясо'),
    ('Баранина', 'Мясо'),
    ('Кролик', 'Мясо'),
    
    # Рыба и морепродукты
    ('Лосось', 'Рыба'),
    ('Треска', 'Рыба'),
    ('Минтай', 'Рыба'),
    ('Скумбрия', 'Рыба'),
    ('Креветки', 'Рыба'),
    ('Кальмары', 'Рыба'),
    ('Мидии', 'Рыба'),
    
    # Молочные продукты
    ('Молоко', 'Молочные'),
    ('Кефир', 'Молочные'),
    ('Творог', 'Молочные'),
    ('Сметана', 'Молочные'),
    ('Масло сливочное', 'Молочные'),
    ('Сыр', 'Молочные'),
    
    # Хлеб и выпечка
    ('Хлеб', 'Хлеб и выпечка'),
    ('Багет', 'Хлеб и выпечка'),
    ('Булочки', 'Хлеб и выпечка'),
    
    # Грибы
    ('Шампиньоны', 'Грибы'),
    ('Вешенки', 'Грибы'),
    ('Белые грибы', 'Грибы'),
    ('Опята', 'Грибы'),
    ('Лисички', 'Грибы'),
    
    # Крупы и макароны
    ('Рис', 'Крупы'),
    ('Гречка', 'Крупы'),
    ('Овсянка', 'Крупы'),
    ('Манка', 'Крупы'),
    ('Пшеничная крупа', 'Крупы'),
    ('Вермишель', 'Крупы'),
    ('Рожки', 'Крупы'),
    ('Спагетти', 'Крупы'),
    
    # Масла и соусы
    ('Подсолнечное масло', 'Масла и соусы'),
    ('Оливковое масло', 'Масла и соусы'),
    ('Кокосовое масло', 'Масла и соусы'),
    ('Горчица', 'Масла и соусы'),
    ('Майонез', 'Масла и соусы'),
    ('Томатная паста', 'Масла и соусы'),
    ('Соевый соус', 'Масла и соусы'),
    ('Лимонный сок', 'Масла и соусы'),
    ('Вино', 'Масла и соусы'),
    
    # Специи
    ('Кориандр', 'Специи'),
    ('Тимьян', 'Специи'),
    ('Розмарин', 'Специи'),
    ('Мускатный орех', 'Специи'),
    ('Гвоздика', 'Специи'),
    ('Карри', 'Специи'),
    ('Хмели-сунели', 'Специи'),
    
    # Напитки
    ('Вода', 'Напитки'),
    ('Чай', 'Напитки'),
    ('Кофе', 'Напитки'),
    ('Компоты', 'Напитки'),
    ('Лимонад', 'Напитки'),
    ('Квас', 'Напитки'),
    
    # Сладости
    ('Мед', 'Сладости'),
    ('Шоколад', 'Сладости'),
    ('Джемы и варенья', 'Сладости'),
    ('Конфеты', 'Сладости'),
    ('Печенье', 'Сладости'),
    ('Торты', 'Сладости'),
    
    # Фрукты и ягоды
    ('Яблоки', 'Фрукты'),
    ('Груши', 'Фрукты'),
    ('Апельсины', 'Фрукты'),
    ('Лимоны', 'Фрукты'),
    ('Мандарины', 'Фрукты'),
    ('Виноград', 'Фрукты'),
    ('Персики', 'Фрукты'),
    ('Абрикосы', 'Фрукты'),
    ('Вишня', 'Фрукты'),
    ('Клубника', 'Фрукты'),
    ('Малина', 'Фрукты'),
    ('Черешня', 'Фрукты'),
    ('Арбуз', 'Фрукты'),
    ('Дыня', 'Фрукты'),
    ('Киви', 'Фрукты'),
    ('Ананас', 'Фрукты'),
    ('Авокадо', 'Фрукты'),
    
    # Яйца и бобовые
    ('Яйца', 'Яйца и бобовые'),
    ('Горошек', 'Яйца и бобовые'),
    ('Фасоль', 'Яйца и бобовые'),
]

# Создаем словари для быстрого доступа
ALL_INGREDIENTS = [item[0] for item in ALL_INGREDIENTS_WITH_CATEGORIES]
INGREDIENT_CATEGORY_MAP = {item[0]: item[1] for item in ALL_INGREDIENTS_WITH_CATEGORIES}

# ЛОКАЛЬНЫЕ ИКОНКИ ДЛЯ ПРОДУКТОВ (эмодзи)
LOCAL_INGREDIENT_ICONS = {
    # Овощи
    'Картошка': '🥔',
    'Морковь': '🥕',
    'Свёкла': '🍠',
    'Капуста': '🥬',
    'Помидоры': '🍅',
    'Огурцы': '🥒',
    'Кабачки': '🥒',
    'Баклажаны': '🍆',
    'Баклажан': '🍆',
    'Чеснок': '🧄',
    'Лук репчатый': '🧅',
    'Зелень': '🌿',
    'Перец болгарский': '🫑',
    'Редис': '🌶️',
    'Сельдерей': '🥬',
    'Шпинат': '🥬',
    'Салат листовой': '🥬',
    
    # Мясо
    'Говядина': '🥩',
    'Свинина': '🐖',
    'Курица': '🍗',
    'Индейка': '🦃',
    'Утка': '🦆',
    'Баранина': '🐑',
    'Кролик': '🐇',
    
    # Рыба и морепродукты
    'Лосось': '🐟',
    'Треска': '🐟',
    'Минтай': '🐟',
    'Скумбрия': '🐟',
    'Креветки': '🦐',
    'Кальмары': '🦑',
    'Мидии': '🐚',
    
    # Молочные продукты
    'Молоко': '🥛',
    'Кефир': '🥛',
    'Творог': '🧀',
    'Сметана': '🥛',
    'Масло сливочное': '🧈',
    'Сыр': '🧀',
    
    # Хлеб и выпечка
    'Хлеб': '🍞',
    'Багет': '🥖',
    'Булочки': '🥐',
    
    # Грибы
    'Шампиньоны': '🍄',
    'Вешенки': '🍄',
    'Белые грибы': '🍄',
    'Опята': '🍄',
    'Лисички': '🍄',
    
    # Крупы и макароны
    'Рис': '🍚',
    'Гречка': '🌾',
    'Овсянка': '🥣',
    'Манка': '🌾',
    'Пшеничная крупа': '🌾',
    'Вермишель': '🍝',
    'Рожки': '🍝',
    'Спагетти': '🍝',
    
    # Масла и соусы
    'Подсолнечное масло': '🫒',
    'Оливковое масло': '🫒',
    'Кокосовое масло': '🥥',
    'Горчица': '🫙',
    'Майонез': '🫙',
    'Томатная паста': '🍅',
    'Соевый соус': '🫙',
    'Лимонный сок': '🍋',
    'Вино': '🍷',
    
    # Специи
    'Кориандр': '🌿',
    'Тимьян': '🌿',
    'Розмарин': '🌿',
    'Мускатный орех': '🌰',
    'Гвоздика': '🌿',
    'Карри': '🌶️',
    'Хмели-сунели': '🌿',
    
    # Напитки
    'Вода': '💧',
    'Чай': '🍵',
    'Кофе': '☕',
    'Компоты': '🧃',
    'Лимонад': '🥤',
    'Квас': '🧃',
    
    # Сладости
    'Мед': '🍯',
    'Шоколад': '🍫',
    'Джемы и варенья': '🍓',
    'Конфеты': '🍬',
    'Печенье': '🍪',
    'Торты': '🍰',
    
    # Фрукты и ягоды
    'Яблоки': '🍎',
    'Груши': '🍐',
    'Апельсины': '🍊',
    'Лимоны': '🍋',
    'Мандарины': '🍊',
    'Виноград': '🍇',
    'Персики': '🍑',
    'Абрикосы': '🍑',
    'Вишня': '🍒',
    'Клубника': '🍓',
    'Малина': '🫐',
    'Черешня': '🍒',
    'Арбуз': '🍉',
    'Дыня': '🍈',
    'Киви': '🥝',
    'Ананас': '🍍',
    'Авокадо': '🥑',
    
    # Яйца и бобовые
    'Яйца': '🥚',
    'Горошек': '🫛',
    'Фасоль': '🫘',
}

# Цветовая схема
COLORS = {
    'primary': '#2E7D32',
    'primary_light': '#4CAF50',
    'secondary': '#1976D2',
    'secondary_light': '#2196F3',
    'accent': '#FF9800',
    'background': '#F5F5F5',
    'surface': '#FFFFFF',
    'text_primary': '#212121',
    'text_secondary': '#757575',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#F44336',
    'card_bg': '#FFFFFF',
    'hover_bg': '#E8F5E9',
    'selected_bg': '#C8E6C9',
    'unselected_bg': '#F5F5F5',
    'border': '#E0E0E0'
}

# Все рецепты с полными ингредиентами и инструкциями
recipes_data = [
    ('Борщ', 'Картошка, Капуста, Свёкла, Морковь, Лук репчатый, Говядина, Сметана, Чеснок, Томатная паста, Соль, Перец, Лавровый лист', 
     '1. Говядину промыть, залить холодной водой и варить 1.5 часа, снимая пену\n2. Свёклу, морковь и лук нарезать соломкой и пассеровать\n3. Капусту нашинковать, картошку нарезать кубиками\n4. В бульон добавить картошку, через 10 минут капусту\n5. За 15 минут до готовности добавить пассерованные овощи\n6. Добавить томатную пасту, соль, перец, лавровый лист\n7. Варить до готовности овощей, подавать со сметаной', 
     'Супы', 120, 'Средняя', 4.8, 'https://img.freepik.com/free-photo/traditional-russian-borscht-soup-with-sour-cream_123827-21862.jpg', None),
    
    ('Щи из свежей капусты', 'Капуста, Картошка, Морковь, Лук репчатый, Говядина, Томатная паста, Сметана, Соль, Перец, Зелень', 
     '1. Мясо варить 1.5 часа до готовности\n2. Капусту нашинковать, картошку нарезать кубиками\n3. Лук и морковь пассеровать с томатной пастой\n4. В бульон добавить картошку, через 10 минут капусту\n5. Добавить пассерованные овощи, варить до готовности\n6. Посолить, поперчить, добавить зелень', 
     'Супы', 100, 'Средняя', 4.6, 'https://img.freepik.com/free-photo/russian-cabbage-soup-schi-with-sour-cream_123827-21863.jpg', None),
    
    ('Солянка', 'Говядина, Колбаса, Сосиски, Соленые огурцы, Каперсы, Лук репчатый, Томатная паста, Оливки, Лимон, Сметана', 
     '1. Говядину отварить, бульон процедить\n2. Мясо, колбасу и сосиски нарезать кубиками\n3. Лук обжарить, добавить томатную пасту\n4. Соленые огурцы нарезать, добавить к луку\n5. Все компоненты соединить в бульоне, довести до кипения\n6. Добавить каперсы, оливки, варить 10 минут\n7. Подавать с лимоном и сметаной', 
     'Супы', 90, 'Средняя', 4.7, None, None),
    
    ('Салат оливье', 'Картошка, Яйца, Огурцы, Морковь, Горошек, Колбаса, Майонез, Соль, Зелень', 
     '1. Картошку, морковь и яйца отварить до готовности\n2. Все ингредиенты нарезать мелкими кубиками\n3. Добавить зеленый горошек\n4. Заправить майонезом, посолить\n5. Тщательно перемешать\n6. Украсить зеленью перед подачи', 
     'Салаты', 60, 'Легкая', 4.9, 'https://img.freepik.com/free-photo/russian-salad-olivier_123827-21865.jpg', None),
    
    ('Греческий салат', 'Помидоры, Огурцы, Перец болгарский, Сыр фета, Оливки, Лук красный, Оливковое масло, Лимонный сок, Орегано, Соль', 
     '1. Овощи нарезать крупными кусками\n2. Сыр фета нарезать кубиками\n3. Лук нарезать полукольцами\n4. Смешать все ингредиенты в большой миске\n5. Приготовить заправку: оливковое масло + лимонный сок + орегано\n6. Полить салат заправкой, аккуратно перемешать', 
     'Салаты', 20, 'Легкая', 4.8, None, None),
    
    ('Салат Цезарь', 'Курица, Салат листовой, Сухарики, Сыр пармезан, Яйца, Чеснок, Оливковое масло, Горчица, Лимонный сок, Вустерширский соус', 
     '1. Куриное филе обжарить до готовности\n2. Салат промыть, обсушить, порвать руками\n3. Приготовить соус: яичный желток + чеснок + горчица + лимонный сок + вустерширский соус + оливковое масло\n4. Салат полить соусом, перемешать\n5. Добавить курицу, сухарики, тертый пармезан', 
     'Салаты', 30, 'Средняя', 4.7, None, None),
    
    ('Плов', 'Рис, Говядина, Морковь, Лук репчатый, Чеснок, Растительное масло, Зира, Барбарис, Соль, Перец', 
     '1. Мясо нарезать кубиками, обжарить до румяной корочки\n2. Лук нарезать полукольцами, морковь соломкой\n3. Добавить овощи к мясу, обжарить 10 минут\n4. Добавить специи, соль, перец\n5. Рис промыть, выложить сверху\n6. Залить водой, чтобы покрывала рис на 2 см\n7. Тушить на медленном огне 40 минут', 
     'Основные блюда', 90, 'Сложная', 4.9, 'https://img.freepik.com/free-photo/uzbek-pilaf-with-meat-and-vegetables_123827-21867.jpg', None),
    
    ('Бефстроганов', 'Говядина, Сметана, Грибы, Лук репчатый, Томатная паста, Мука, Масло сливочное, Соль, Перец', 
     '1. Говядину нарезать тонкими полосками\n2. Обжарить на сильном огне до румяной корочки\n3. Лук нарезать полукольцами, грибы пластинками\n4. Обжарить лук и грибы отдельно\n5. Соединить мясо с овощами\n6. Добавить томатную пасту, сметану, тушить 20 минут\n7. Заправить мукой, разведенной в воде', 
     'Основные блюда', 60, 'Средняя', 4.7, None, None),
    
    ('Омлет', 'Яйца, Молоко, Сыр, Масло сливочное, Соль, Перец, Зелень', 
     '1. Яйца взбить с молоком, солью и перцем\n2. Сыр натереть на терке\n3. На сковороде растопить масло\n4. Вылить яичную смесь\n5. Когда омлет схватится, посыпать сыром\n6. Накрыть крышкой, готовить 3 минуты', 
     'Завтраки', 15, 'Легкая', 4.7, 'https://img.freepik.com/free-photo/fluffy-omelette-with-cheese-and-herbs_123827-21868.jpg', None),
    
    ('Сырники', 'Творог, Яйца, Мука, Сахар, Ванилин, Растительное масло, Сметана', 
     '1. Творог протереть через сито\n2. Добавить яйца, сахар, ванилин\n3. Добавить мука, замесить тесто\n4. Сформировать сырники\n5. Обжарить на растительном масле с двух сторон\n6. Подавать со сметаной', 
     'Завтраки', 30, 'Легкая', 4.8, None, None),
    
    ('Шарлотка яблочная', 'Яблоки, Яйца, Сахар, Мука, Корица, Ванилин, Сливочное масло', 
     '1. Яблоки очистить, нарезать дольками\n2. Яйца взбить с сахаром до пышной пены\n3. Добавить мука, корицу, ванилин\n4. Аккуратно перемешать\n5. Форму смазать маслом\n6. Выложить яблоки, залить тестом\n7. Выпекать 40 минут при 180°C', 
     'Десерты', 60, 'Легкая', 4.9, 'https://img.freepik.com/free-photo/apple-charlotte-cake_123827-21869.jpg', None),
    
    # НОВЫЕ РЕЦЕПТЫ:
    # Супы
    ('Куриный суп с лапшой', 'Курица, Картошка, Морковь, Лук репчатый, Вермишель, Зелень, Соль, Перец, Лавровый лист', 
     '1. Курицу залить водой, довести до кипения, снять пену\n2. Добавить целую луковицу и морковь, варить 40 минут\n3. Курицу вынуть, бульон процедить\n4. Картошку нарезать кубиками, добавить в бульон\n5. Через 10 минут добавить вермишель\n6. Курицу нарезать кусочками, вернуть в суп\n7. Добавить соль, перец, лавровый лист, варить 5 минут\n8. Подавать с зеленью', 
     'Супы', 60, 'Легкая', 4.5, None, None),
    
    ('Грибной суп-пюре', 'Шампиньоны, Картошка, Лук репчатый, Сливки, Масло сливочное, Чеснок, Соль, Перец, Зелень', 
     '1. Грибы нарезать пластинками, лук и чеснок мелко\n2. Обжарить лук и чеснок на сливочном масле\n3. Добавить грибы, обжарить 10 минут\n4. Картошку нарезать кубиками, залить водой\n5. Варить 15 минут, затем добавить грибную смесь\n6. Варить ещё 10 минут, добавить сливки\n7. Погружным блендером превратить в пюре\n8. Посолить, поперчить, подавать с зеленью', 
     'Супы', 45, 'Средняя', 4.6, None, None),
    
    ('Томатный суп', 'Помидоры, Лук репчатый, Чеснок, Базилик, Сливки, Соль, Перец, Оливковое масло', 
     '1. Помидоры обдать кипятком, снять кожуру\n2. Лук и чеснок обжарить на оливковом масле\n3. Добавить нарезанные помидоры, тушить 15 минут\n4. Добавить базилик, соль, перец\n5. Залить водой, варить 20 минут\n6. Пюрировать блендером, добавить сливки\n7. Прогреть 5 минут, не доводя до кипения', 
     'Супы', 40, 'Легкая', 4.4, None, None),
    
    ('Уха', 'Рыба (треска), Картошка, Морковь, Лук репчатый, Лавровый лист, Перец, Зелень, Соль', 
     '1. Рыбу почистить, нарезать кусками\n2. Залить холодной водой, довести до кипения\n3. Снять пену, добавить целую луковицу и морковь\n4. Варить 20 минут, затем рыбу вынуть\n5. Картошку нарезать, добавить в бульон\n6. Варить 15 минут, добавить лавровый лист, перец\n7. Рыбу без костей вернуть в суп\n8. Посолить, варить 5 минут, подавать с зеленью', 
     'Супы', 50, 'Средняя', 4.7, None, None),
    
    # Салаты
    ('Винегрет', 'Свёкла, Картошка, Морковь, Соленые огурцы, Горошек, Лук репчатый, Растительное масло, Соль', 
     '1. Свёклу, картошку и морковь отварить до готовности\n2. Овощи очистить, нарезать мелкими кубиками\n3. Соленые огурцы и лук нарезать\n4. Все ингредиенты смешать в миске\n5. Добавить зеленый горошек\n6. Заправить растительным маслом, посолить\n7. Тщательно перемешать', 
     'Салаты', 45, 'Легкая', 4.5, None, None),
    
    ('Салат с тунцом', 'Тунец консервированный, Яйца, Помидоры, Огурцы, Лук красный, Майонез, Соль, Перец, Листья салата', 
     '1. Яйца отварить, нарезать кубиками\n2. Помидоры и огурцы нарезать\n3. Лук нарезать полукольцами\n4. Тунец размять вилкой\n5. Все ингредиенты смешать в миске\n6. Добавить майонез, соль, перец\n7. Выложить на листья салата', 
     'Салаты', 20, 'Легкая', 4.6, None, None),
    
    ('Капрезе', 'Помидоры, Сыр моцарелла, Базилик, Оливковое масло, Бальзамический уксус, Соль, Перец', 
     '1. Помидоры нарезать кружочками\n2. Моцареллу нарезать кружочками\n3. На тарелку выложить поочередно помидоры, моцареллу и листья базилика\n4. Сбрызнуть оливковым маслом и бальзамическим уксусом\n5. Посолить, поперчить\n6. Подавать сразу', 
     'Салаты', 15, 'Легкая', 4.8, None, None),
    
    # Основные блюда
    ('Котлеты по-киевски', 'Курица, Масло сливочное, Чеснок, Зелень, Яйца, Мука, Сухари панировочные, Растительное масло, Соль, Перец', 
     '1. Куриное филе отбить\n2. Масло смешать с чесноком и зеленью, сформировать брусок\n3. Завернуть масло в куриное филе\n4. Обвалять в муке, затем в яйце, затем в сухарях\n5. Обжарить в разогретом масле 7-8 минут\n6. Выложить на бумажное полотенце\n7. Подавать с картофельным пюре', 
     'Основные блюда', 40, 'Средняя', 4.8, None, None),
    
    ('Жаркое в горшочках', 'Свинина, Картошка, Морковь, Лук репчатый, Грибы, Сметана, Чеснок, Соль, Перец, Зелень', 
     '1. Мясо нарезать кубиками, обжарить\n2. Лук и морковь обжарить отдельно\n3. Картошку нарезать кубиками\n4. Грибы нарезать пластинками\n5. В горшочки выложить слоями: мясо, лук с морковью, картошку, грибы\n6. Залить сметаной, смешанной с водой\n7. Добавить чеснок, соль, перец\n8. Тушить в духовке 1 час при 180°C', 
     'Основные блюда', 90, 'Средняя', 4.7, None, None),
    
    ('Лазанья', 'Фарш говяжий, Листы для лазаньи, Помидоры, Лук репчатый, Чеснок, Сыр, Молоко, Мука, Масло сливочное, Соль, Перец', 
     '1. Лук и чеснок обжарить, добавить фарш\n2. Добавить нарезанные помидоры, тушить 20 минут\n3. Приготовить бешамель: растопить масло, добавить муку, затем молоко\n4. В форму выложить слоями: соус, листы лазаньи, мясной соус, бешамель\n5. Последний слой посыпать сыром\n6. Выпекать 40 минут при 180°C', 
     'Основные блюда', 80, 'Сложная', 4.9, None, None),
    
    ('Рыба в кляре', 'Рыба (минтай), Яйца, Мука, Пиво, Растительное масло, Лимон, Соль, Перец', 
     '1. Рыбу нарезать порционными кусками\n2. Приготовить кляр: смешать яйца, мука, пиво до консистенции сметаны\n3. Рыбу посолить, поперчить\n4. Каждый кусок обмакнуть в кляр\n5. Обжарить в разогретом масле до золотистой корочки\n6. Выложить на бумажное полотенце\n7. Подавать с дольками лимона', 
     'Основные блюда', 30, 'Легкая', 4.5, None, None),
    
    ('Плов с курицей', 'Рис, Курица, Морковь, Лук репчатый, Чеснок, Растительное масло, Зира, Соль, Перец', 
     '1. Курицу нарезать кусочками, обжарить\n2. Лук нарезать полукольцами, морковь соломкой\n3. Обжарить овощи в отдельной сковороде\n4. В казане смешать курицу и овощи\n5. Добавить промытый рис, залить водой на 2 см выше\n6. Добавить целые зубчики чеснока, зиру, соль, перец\n7. Тушить на медленном огне 30 минут', 
     'Основные блюда', 60, 'Средняя', 4.6, None, None),
    
    # Завтраки
    ('Блинчики', 'Молоко, Яйца, Мука, Сахар, Соль, Растительное масло', 
     '1. Яйца взбить с сахаром и солью\n2. Добавить молоко, перемешать\n3. Постепенно добавлять мука, постоянно помешивая\n4. Тесто должно быть как жидкая сметана\n5. Дать тесту постоять 20 минут\n6. На разогретой сковороде печь блинчики с двух сторон\n7. Подавать с вареньем, сметаной или медом', 
     'Завтраки', 40, 'Легкая', 4.7, None, None),
    
    ('Овсяная каша', 'Овсянка, Молоко, Вода, Сахар, Соль, Масло сливочное, Фрукты', 
     '1. В кастрюлю влить молоко и воду (пополам)\n2. Добавить овсянку, довести до кипения\n3. Убавить огонь, варить 10-15 минут\n4. Добавить сахар, соль по вкусу\n5. Снять с огня, добавить масло\n6. Дать постоять 5 минут под крышкой\n7. Подавать с фрукты или ягодами', 
     'Завтраки', 20, 'Легкая', 4.4, None, None),
    
    ('Яичница с помидорами', 'Яйца, Помидоры, Лук репчатый, Растительное масло, Соль, Перец, Зелень', 
     '1. Помидоры нарезать кубиками, лук полукольцами\n2. Обжарить лук до прозрачности\n3. Добавить помидоры, тушить 5 минут\n4. Яйца взбить вилкой, посолить, поперчить\n5. Вылить яйца к овощам\n6. Жарить на среднем огне 5-7 минут\n7. Посыпать зеленью', 
     'Завтраки', 15, 'Легкая', 4.5, None, None),
    
    # Десерты
    ('Тирамису', 'Сыр маскарпоне, Яйца, Сахар, Кофе, Песочное печенье, Какао', 
     '1. Яичные желтки взбить с сахаром до белой пены\n2. Добавить маскарпоне, аккуратно перемешать\n3. Кофе сварить, остудить\n4. Печенье быстро обмакнуть в кофе\n5. В форму выложить слой печенья, затем слой крема\n6. Повторить слои\n7. Посыпать какао, убрать в холодильник на 4 часа', 
     'Десерты', 60, 'Средняя', 4.9, None, None),
    
    ('Шоколадный торт', 'Мука, Сахар, Какао, Яйца, Масло сливочное, Сметана, Сода, Уксус, Соль', 
     '1. Яйца взбить с сахаром до пышности\n2. Добавить растопленное масло, сметану\n3. Мука смешать с какао, содой, солью\n4. Постепенно добавлять сухие ингредиенты к жидким\n5. Добавить уксус, быстро перемешать\n6. Вылить в форму, выпекать 40 минут при 180°C\n7. Остудить, разрезать на коржи, промазать кремом', 
     'Десерты', 90, 'Средняя', 4.8, None, None),
    
    ('Печенье овсяное', 'Овсянка, Мука, Сахар, Масло сливочное, Яйца, Сода, Изюм, Корица', 
     '1. Масло растереть с сахаром\n2. Добавить яйцо, перемешать\n3. Овсянку измельчить в блендере\n4. Смешать овсянку, мука, соду, корицу\n5. Соединить сухие и жидкие ингредиенты\n6. Добавить изюм\n7. Сформировать печенье, выпекать 20 минут при 180°C', 
     'Десерты', 45, 'Легкая', 4.6, None, None),
    
    ('Мороженое ванильное', 'Сливки, Молоко, Сахар, Желтки, Ванилин', 
     '1. Желтки взбить с сахаром до белой пены\n2. Молоко нагреть, но не кипятить\n3. Тонкой струйкой влить молоко в желтки\n4. Вернуть смесь на огонь, нагревать до загустения\n5. Остудить, добавить ванилин\n6. Сливки взбить до мягких пиков\n7. Смешать с яичной смесью\n8. Заморозить в мороженице или вручную каждые 30 минут перемешивать', 
     'Десерты', 120, 'Средняя', 4.7, None, None),
    
    # Напитки
    ('Мохито', 'Лайм, Мята, Сахар, Ром, Содовая, Лёд', 
     '1. Лайм нарезать дольками, положить в стакан\n2. Добавить листья мяты, сахар\n3. Аккуратно подавить пестиком\n4. Наполнить стакан льдом\n5. Добавить ром\n6. Долить содовой\n7. Аккуратно перемешать', 
     'Напитки', 10, 'Легкая', 4.8, None, None),
    
    ('Глинтвейн', 'Вино красное, Апельсин, Лимон, Гвоздика, Корица, Мускатный орех, Мед', 
     '1. Вино налить в кастрюлю, нагревать на медленном огне\n2. Апельсин и лимон нарезать дольками\n3. Добавить фрукты и специи в вино\n4. Нагревать, не доводя до кипения\n5. Добавить мед по вкусу\n6. Настоять 10 минут под крышкой\n7. Процедить, подавать горячим', 
     'Напитки', 25, 'Легкая', 4.7, None, None),
    
    ('Смузи ягодный', 'Клубника, Малина, Банан, Йогурт, Мед, Лёд', 
     '1. Ягоды и банан помыть, очистить\n2. Положить все ингредиенты в блендер\n3. Добавить йогурт, мед, лед\n4. Взбить до однородной массы\n5. Перелить в стакан\n6. Украсить ягодой', 
     'Напитки', 10, 'Легкая', 4.5, None, None)
]

# Категории продуктов для фильтрации
CATEGORIES = sorted(list(set([item[1] for item in ALL_INGREDIENTS_WITH_CATEGORIES])))
INGREDIENT_CATEGORIES = {cat: [] for cat in CATEGORIES}
INGREDIENT_CATEGORIES['Все продукты'] = ALL_INGREDIENTS

for product, category in ALL_INGREDIENTS_WITH_CATEGORIES:
    INGREDIENT_CATEGORIES[category].append(product)


# ==================== КЛАССЫ ====================
@dataclass
class Recipe:
    """Модель рецепта"""
    id: int
    name: str
    ingredients: str
    instructions: str
    category: str
    prep_time: int
    difficulty: str
    rating: float
    image_url: Optional[str]
    image_data: Optional[bytes]
    match_percentage: float = 0.0
    matches: int = 0
    total_ingredients: int = 0
    selected_count: int = 0


class ImageManager:
    """Менеджер для работы с изображениями"""
    
    def __init__(self):
        self.cache = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.ingredient_icons = {}
        self.recipe_images = {}
        self.placeholder_icons = {}
    
    def create_ingredient_icon(self, name, bg_color=None, size=60, is_selected=False):
        """Создание иконки для ингредиента"""
        try:
            if name in LOCAL_INGREDIENT_ICONS:
                icon = LOCAL_INGREDIENT_ICONS[name]
                
                # Создаем изображение с эмодзи
                img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
                draw = ImageDraw.Draw(img)
                
                # Цвет фона
                if is_selected:
                    bg_color = COLORS['selected_bg']
                elif not bg_color:
                    # Генерируем цвет на основе хеша названия
                    hash_obj = hashlib.md5(name.encode())
                    hash_int = int(hash_obj.hexdigest(), 16)
                    hue = hash_int % 360
                    r, g, b = colorsys.hls_to_rgb(hue/360, 0.7, 0.8)
                    bg_color = (int(r*255), int(g*255), int(b*255))
                
                # Рисуем круглый фон
                margin = 5
                draw.ellipse([margin, margin, size-margin, size-margin], fill=bg_color)
                
                try:
                    # Используем эмодзи
                    from PIL import ImageFont
                    try:
                        font = ImageFont.truetype("seguiemj.ttf", size-20)
                    except:
                        font = ImageFont.load_default()
                    
                    bbox = draw.textbbox((0, 0), icon, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    x = (size - text_width) // 2
                    y = (size - text_height) // 2
                    
                    draw.text((x, y), icon, font=font, fill="white", 
                              stroke_width=1, stroke_fill=(0, 0, 0, 128))
                    
                except Exception as e:
                    print(f"Ошибка при создании эмодзи для {name}: {e}")
                    # Если не удалось нарисовать эмодзи, рисуем первую букву
                    first_letter = name[0].upper() if name else "?"
                    font_size = size // 3
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                    
                    bbox = draw.textbbox((0, 0), first_letter, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    x = (size - text_width) // 2
                    y = (size - text_height) // 2
                    draw.text((x, y), first_letter, font=font, fill="white")
                
                return ImageTk.PhotoImage(img)
            
            # Если нет эмодзи, создаем цветной круг с первой буквой
            if not bg_color:
                hash_obj = hashlib.md5(name.encode())
                hash_int = int(hash_obj.hexdigest(), 16)
                hue = hash_int % 360
                r, g, b = colorsys.hls_to_rgb(hue/360, 0.7, 0.8)
                bg_color = (int(r*255), int(g*255), int(b*255))
            
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Рисуем круглый фон
            margin = 5
            draw.ellipse([margin, margin, size-margin, size-margin], fill=bg_color)
            
            # Добавляем текст с первой буквой
            try:
                from PIL import ImageFont
                font = ImageFont.truetype("arial.ttf", size//2)
            except:
                font = ImageFont.load_default()
            
            text = name[0].upper()
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            draw.text((x, y), text, font=font, fill='white')
            
            return ImageTk.PhotoImage(img)
            
        except Exception as e:
            print(f"Ошибка создания иконки для {name}: {e}")
            # Возвращаем пустое изображение
            img = Image.new('RGB', (size, size), 'gray')
            return ImageTk.PhotoImage(img)
    
    def get_or_create_ingredient_icon(self, product_name, is_selected=False):
        """Получает или создает иконку продукта"""
        cache_key = f"{product_name}_{is_selected}"
        if cache_key not in self.ingredient_icons:
            icon = self.create_ingredient_icon(product_name, is_selected=is_selected)
            self.ingredient_icons[cache_key] = icon
        return self.ingredient_icons[cache_key]
    
    def load_recipe_image(self, recipe_id, image_url=None, image_data=None):
        """Загружает изображение рецепта"""
        try:
            # Проверяем кэш
            cache_key = f"{recipe_id}_{image_url}"
            if cache_key in self.recipe_images:
                return self.recipe_images[cache_key]
            
            # Пробуем загрузить из локального файла
            local_path = RECIPE_IMAGES_DIR / f"recipe_{recipe_id}.jpg"
            if local_path.exists():
                img = Image.open(local_path)
                img = img.resize((200, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.recipe_images[cache_key] = photo
                return photo
            
            # Если есть данные изображения в базе
            if image_data:
                try:
                    img_data = BytesIO(image_data)
                    img = Image.open(img_data)
                    img = img.resize((200, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.recipe_images[cache_key] = photo
                    return photo
                except:
                    pass
            
            # Если есть URL, загружаем из интернета
            if image_url and image_url.startswith('http'):
                try:
                    response = requests.get(image_url, timeout=5)
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        img = img.resize((200, 150), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.recipe_images[cache_key] = photo
                        
                        # Сохраняем локально
                        img.save(local_path, 'JPEG', quality=85)
                        
                        return photo
                except:
                    pass
            
            # Создаем заглушку если изображение не найдено
            return self.create_recipe_placeholder(recipe_id)
            
        except Exception as e:
            print(f"Ошибка при загрузке изображения для рецепта {recipe_id}: {e}")
            return self.create_recipe_placeholder(recipe_id)
    
    def create_recipe_placeholder(self, recipe_id):
        """Создает заглушку для рецепта без изображения"""
        if recipe_id in self.placeholder_icons:
            return self.placeholder_icons[recipe_id]
        
        # Создаем изображение с иконкой камеры
        img = Image.new('RGB', (200, 150), color=COLORS['unselected_bg'])
        draw = ImageDraw.Draw(img)
        
        # Рисуем значок камеры
        try:
            from PIL import ImageFont
            
            # Рисуем круг
            center_x, center_y = 100, 75
            radius = 40
            draw.ellipse([center_x-radius, center_y-radius, center_x+radius, center_y+radius], 
                        fill=COLORS['text_secondary'], outline=COLORS['border'], width=2)
            
            # Рисуем значок камеры
            draw.rectangle([center_x-20, center_y-15, center_x+20, center_y+15], 
                          fill=COLORS['surface'], outline=COLORS['border'], width=2)
            draw.ellipse([center_x-10, center_y-5, center_x+10, center_y+5], 
                        fill=COLORS['primary'])
            
            # Текст
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            draw.text((center_x-40, center_y+30), "Добавить фото", 
                     fill=COLORS['text_secondary'], font=font)
            
        except Exception as e:
            print(f"Ошибка при создании заглушки: {e}")
        
        photo = ImageTk.PhotoImage(img)
        self.placeholder_icons[recipe_id] = photo
        return photo
    
    def load_image_from_url(self, url, callback=None):
        """Асинхронная загрузка изображения по URL"""
        if url in self.cache:
            if callback:
                callback(self.cache[url])
            return self.cache[url]
        
        def load():
            try:
                response = requests.get(url, timeout=10)
                img_data = Image.open(BytesIO(response.content))
                photo = ImageTk.PhotoImage(img_data)
                self.cache[url] = photo
                if callback:
                    callback(photo)
                return photo
            except Exception as e:
                print(f"Ошибка загрузки изображения {url}: {e}")
                return None
        
        return self.executor.submit(load)
    
    def create_placeholder_image(self, text="Нет\nизображения", size=(300, 200)):
        """Создание заглушки для отсутствующего изображения"""
        img = Image.new('RGB', size, (240, 240, 240))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        lines = text.split('\n')
        line_height = 25
        total_height = len(lines) * line_height
        y = (size[1] - total_height) // 2
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (size[0] - text_width) // 2
            draw.text((x, y), line, font=font, fill=(150, 150, 150))
            y += line_height
        
        return ImageTk.PhotoImage(img)


class DatabaseManager:
    """Менеджер базы данных"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Подключение к базе данных"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        return self
    
    def init_database(self, recipes_data: List[Tuple]):
        """Инициализация базы данных"""
        self.cursor.execute('DROP TABLE IF EXISTS Recipes')
        
        self.cursor.execute('''
        CREATE TABLE Recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT,
            category TEXT,
            prep_time INTEGER,
            difficulty TEXT,
            rating REAL DEFAULT 0.0,
            image_url TEXT,
            image_data BLOB
        )
        ''')
        
        # Создаем индекс для быстрого поиска
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON Recipes(name)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON Recipes(category)')
        
        for recipe in recipes_data:
            self.cursor.execute('''INSERT INTO Recipes 
                               (name, ingredients, instructions, category, prep_time, difficulty, rating, image_url, image_data) 
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', recipe)
        
        self.conn.commit()
        print(f"Загружено {len(recipes_data)} рецептов в базу данных")
        return self
    
    def search_recipes_by_ingredients(self, selected_ingredients: Set[str]) -> List[Recipe]:
        """Поиск рецептов по ингредиентам"""
        if not selected_ingredients:
            return []
        
        self.cursor.execute('SELECT * FROM Recipes')
        all_recipes = self.cursor.fetchall()
        
        results = []
        selected_lower = {ing.strip().lower() for ing in selected_ingredients}
        
        for row in all_recipes:
            recipe = self._row_to_recipe(row)
            ingredient_list = [ing.strip().lower() for ing in recipe.ingredients.split(',')]
            
            matches = 0
            for selected in selected_lower:
                for recipe_ing in ingredient_list:
                    if selected in recipe_ing or recipe_ing in selected:
                        matches += 1
                        break
            
            if matches > 0:
                recipe.matches = matches
                recipe.match_percentage = (matches / len(selected_lower)) * 100
                recipe.total_ingredients = len(ingredient_list)
                recipe.selected_count = len(selected_lower)
                results.append(recipe)
        
        results.sort(key=lambda x: (x.match_percentage, x.matches), reverse=True)
        return results
    
    def search_recipes_by_text(self, search_text: str, search_in_ingredients: bool = True) -> List[Recipe]:
        """Поиск рецептов по тексту (названию и/или ингредиентам)"""
        if not search_text or len(search_text.strip()) < 2:
            return []
        
        search_terms = search_text.lower().strip().split()
        
        self.cursor.execute('SELECT * FROM Recipes')
        all_recipes = self.cursor.fetchall()
        
        results = []
        
        for row in all_recipes:
            recipe = self._row_to_recipe(row)
            score = 0
            
            # Поиск в названии
            recipe_name_lower = recipe.name.lower()
            for term in search_terms:
                if term in recipe_name_lower:
                    score += 3  # Больший вес для совпадений в названии
            
            # Поиск в ингредиентах (если включено)
            if search_in_ingredients:
                ingredients_lower = recipe.ingredients.lower()
                for term in search_terms:
                    if term in ingredients_lower:
                        score += 1
            
            # Поиск в категории
            category_lower = recipe.category.lower()
            for term in search_terms:
                if term in category_lower:
                    score += 2
            
            if score > 0:
                recipe.match_percentage = min(score * 10, 100)  # Преобразуем score в процент
                results.append(recipe)
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x.match_percentage, reverse=True)
        return results
    
    def search_recipes_by_category(self, category: str) -> List[Recipe]:
        """Поиск рецептов по категории"""
        if not category:
            return []
        
        self.cursor.execute('SELECT * FROM Recipes WHERE category = ?', (category,))
        rows = self.cursor.fetchall()
        
        return [self._row_to_recipe(row) for row in rows]
    
    def update_recipe_image_url(self, recipe_id: int, image_url: Optional[str] = None):
        """Обновление URL изображения рецепта"""
        self.cursor.execute(
            'UPDATE Recipes SET image_url = ? WHERE id = ?', 
            (image_url, recipe_id)
        )
        self.conn.commit()
    
    def _row_to_recipe(self, row: Tuple) -> Recipe:
        """Преобразование строки в объект Recipe"""
        return Recipe(
            id=row[0],
            name=row[1],
            ingredients=row[2],
            instructions=row[3],
            category=row[4],
            prep_time=row[5],
            difficulty=row[6],
            rating=row[7],
            image_url=row[8],
            image_data=row[9]
        )


# ==================== ГЛАВНОЕ ПРИЛОЖЕНИЕ С ПОИСКОМ ====================
class KitchenAssistant:
    """Главный класс приложения с функцией поиска"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🍳 Кухонный помощник - Рецепты с изображениями")
        self.root.configure(bg=COLORS['background'])
        
        # Менеджеры
        self.db_manager = DatabaseManager('database.db').connect()
        self.image_manager = ImageManager()
        
        # Данные
        self.selected_ingredients = set()
        self.current_popup = None
        self.search_mode = "ingredients"  # ingredients, text, category
        
        # UI переменные
        self.category_var = tk.StringVar(value="Все продукты")
        self.search_var = tk.StringVar()
        self.search_category_var = tk.StringVar(value="Все категории")
        self.status_bar = None
        self.label_all_count = None
        self.label_selected_count = None
        self.all_products_frame = None
        self.selected_products_frame = None
        self.recipe_canvas_frame = None
        
        # Инициализация
        self.init_database()
        self.setup_interface()
        self.load_initial_data()
    
    def init_database(self):
        """Инициализирует базу данных"""
        self.db_manager.init_database(recipes_data)
    
    def load_initial_data(self):
        """Загружает начальные данные"""
        # Загрузка категорий
        self.recipe_categories = self.get_recipe_categories()
    
    def setup_interface(self):
        """Настройка интерфейса с поиском"""
        # Главный контейнер
        main_container = tk.Frame(self.root, bg=COLORS['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Заголовок
        header_frame = tk.Frame(main_container, bg=COLORS['background'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame, text="🍳 Кухонный помощник", 
                font=('Segoe UI', 28, 'bold'), bg=COLORS['background'], 
                fg=COLORS['primary']).pack(side=tk.LEFT)
        
        tk.Label(header_frame, text="Рецепты с изображениями", 
                font=('Segoe UI', 12), bg=COLORS['background'], 
                fg=COLORS['text_secondary']).pack(side=tk.LEFT, padx=10, pady=10)
        
        # ========== ПАНЕЛЬ ПОИСКА ==========
        search_frame = tk.Frame(main_container, bg=COLORS['background'])
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Тип поиска
        search_type_frame = tk.Frame(search_frame, bg=COLORS['background'])
        search_type_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(search_type_frame, text="Поиск:", 
                font=('Segoe UI', 11), bg=COLORS['background']).pack(side=tk.LEFT, padx=(0, 10))
        
        # Переключатели поиска
        self.search_mode_var = tk.StringVar(value="ingredients")
        
        rb_ingredients = tk.Radiobutton(
            search_type_frame, text="По ингредиентам", variable=self.search_mode_var, 
            value="ingredients", command=self.on_search_mode_changed,
            bg=COLORS['background'], font=('Segoe UI', 10)
        )
        rb_ingredients.pack(side=tk.LEFT, padx=5)
        
        rb_text = tk.Radiobutton(
            search_type_frame, text="По названию", variable=self.search_mode_var, 
            value="text", command=self.on_search_mode_changed,
            bg=COLORS['background'], font=('Segoe UI', 10)
        )
        rb_text.pack(side=tk.LEFT, padx=5)
        
        rb_category = tk.Radiobutton(
            search_type_frame, text="По категории", variable=self.search_mode_var, 
            value="category", command=self.on_search_mode_changed,
            bg=COLORS['background'], font=('Segoe UI', 10)
        )
        rb_category.pack(side=tk.LEFT, padx=5)
        
        # Поле поиска (для текстового поиска)
        self.search_entry_frame = tk.Frame(search_frame, bg=COLORS['background'])
        self.search_entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(self.search_entry_frame, text="Название:", 
                font=('Segoe UI', 11), bg=COLORS['background']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_entry = tk.Entry(
            self.search_entry_frame, 
            textvariable=self.search_var,
            font=('Segoe UI', 11),
            bg=COLORS['surface'],
            relief=tk.SOLID,
            width=30
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        self.search_entry.bind('<KeyRelease>', lambda e: self.on_search_text_changed())
        
        # Кнопка поиска
        search_btn = tk.Button(
            search_frame, 
            text="🔍 Найти", 
            command=self.perform_search,
            bg=COLORS['primary'], 
            fg='white', 
            font=('Segoe UI', 11),
            padx=20, 
            pady=5, 
            relief=tk.FLAT
        )
        search_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Кнопка сброса
        reset_btn = tk.Button(
            search_frame, 
            text="🗑 Сброс", 
            command=self.reset_search,
            bg=COLORS['text_secondary'], 
            fg='white', 
            font=('Segoe UI', 11),
            padx=15, 
            pady=5, 
            relief=tk.FLAT
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Выбор категории (для поиска по категории)
        self.category_search_frame = tk.Frame(search_frame, bg=COLORS['background'])
        
        tk.Label(self.category_search_frame, text="Категория:", 
                font=('Segoe UI', 11), bg=COLORS['background']).pack(side=tk.LEFT, padx=(0, 10))
        
        # Получаем уникальные категории рецептов
        recipe_categories = self.get_recipe_categories()
        self.search_category_menu = ttk.Combobox(
            self.category_search_frame, 
            textvariable=self.search_category_var,
            values=["Все категории"] + recipe_categories,
            state="readonly", 
            width=20
        )
        self.search_category_menu.pack(side=tk.LEFT)
        self.search_category_menu.bind('<<ComboboxSelected>>', lambda e: self.search_by_category())
        
        # Скрываем изначально неактивные фреймы
        self.category_search_frame.pack_forget()
        
        # Основное содержимое
        content_frame = tk.Frame(main_container, bg=COLORS['background'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель - продукты (только для поиска по ингредиентам)
        self.left_panel = tk.Frame(content_frame, bg=COLORS['background'])
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.setup_products_panel()
        
        # Правая панель - выбранные продукты и рецепты
        right_panel = tk.Frame(content_frame, bg=COLORS['background'])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.setup_recipes_panel(right_panel)
        
        # Статус бар внизу
        status_frame = tk.Frame(main_container, bg=COLORS['surface'], height=30, relief=tk.SUNKEN, bd=1)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        status_frame.pack_propagate(False)
        
        self.status_bar = tk.Label(
            status_frame, 
            text="✅ Готов к поиску рецептов. Выберите режим поиска.", 
            font=('Segoe UI', 10), 
            bg=COLORS['surface'], 
            fg=COLORS['text_secondary'], 
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, padx=10)
        
        # Инициализируем отображение
        self.update_products_display()
        self.clear_recipes()
    
    def setup_products_panel(self):
        """Настройка панели продуктов"""
        # Заголовок с фильтром
        products_header = tk.Frame(self.left_panel, bg=COLORS['background'])
        products_header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(products_header, text="🛒 Все продукты", 
                font=('Segoe UI', 16, 'bold'), bg=COLORS['background']).pack(side=tk.LEFT)
        
        self.label_all_count = tk.Label(
            products_header, text="Всего: 0", 
            font=('Segoe UI', 11), bg=COLORS['background'],
            fg=COLORS['text_secondary']
        )
        self.label_all_count.pack(side=tk.RIGHT, padx=10)
        
        # Фильтр по категориям продуктов
        filter_frame = tk.Frame(self.left_panel, bg=COLORS['background'])
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(filter_frame, text="Фильтр:", 
                font=('Segoe UI', 11), bg=COLORS['background']).pack(side=tk.LEFT, padx=(0, 10))
        
        category_menu = ttk.Combobox(
            filter_frame, 
            textvariable=self.category_var,
            values=list(INGREDIENT_CATEGORIES.keys()),
            state="readonly", 
            width=20
        )
        category_menu.pack(side=tk.LEFT)
        category_menu.bind('<<ComboboxSelected>>', lambda e: self.filter_by_category())
        
        # Фрейм для всех продуктов
        self.all_products_frame = tk.Frame(self.left_panel, bg=COLORS['background'])
        self.all_products_frame.pack(fill=tk.BOTH, expand=True)
    
    def setup_recipes_panel(self, parent):
        """Настройка панели рецептов"""
        # Верхняя часть - выбранные продукты
        self.selected_header = tk.Frame(parent, bg=COLORS['background'])
        self.selected_header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(self.selected_header, text="✅ Выбранные продукты", 
                font=('Segoe UI', 16, 'bold'), bg=COLORS['background']).pack(side=tk.LEFT)
        
        self.label_selected_count = tk.Label(
            self.selected_header, 
            text="Выбрано: 0", 
            font=('Segoe UI', 11), 
            bg=COLORS['background'],
            fg=COLORS['text_secondary']
        )
        self.label_selected_count.pack(side=tk.RIGHT, padx=10)
        
        # Контейнер для выбранных продуктов
        selected_container = tk.Frame(parent, bg=COLORS['background'], height=150)
        selected_container.pack(fill=tk.X, pady=(0, 15))
        selected_container.pack_propagate(False)
        
        # Canvas для горизонтальной прокрутки
        canvas = tk.Canvas(selected_container, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(selected_container, orient="horizontal", command=canvas.xview)
        
        self.selected_products_frame = tk.Frame(canvas, bg=COLORS['background'])
        canvas.create_window((0, 0), window=self.selected_products_frame, anchor="nw")
        
        self.selected_products_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.configure(xscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Кнопки управления
        buttons_frame = tk.Frame(parent, bg=COLORS['background'])
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(
            buttons_frame, 
            text="🔍 Найти рецепты", 
            command=self.show_recipes,
            bg=COLORS['primary'], 
            fg='white', 
            font=('Segoe UI', 11, 'bold'),
            padx=20, 
            pady=8, 
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            buttons_frame, 
            text="🗑 Очистить выбор", 
            command=self.clear_selection,
            bg=COLORS['error'], 
            fg='white', 
            font=('Segoe UI', 11),
            padx=20, 
            pady=8, 
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=2)
        
        # Canvas для рецептов
        recipes_container = tk.Frame(parent, bg=COLORS['background'])
        recipes_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas для вертикальной прокрутки
        recipe_canvas = tk.Canvas(recipes_container, bg=COLORS['background'], highlightthickness=0)
        recipe_scrollbar = ttk.Scrollbar(recipes_container, orient="vertical", command=recipe_canvas.yview)
        
        self.recipe_canvas_frame = tk.Frame(recipe_canvas, bg=COLORS['background'])
        recipe_canvas.create_window((0, 0), window=self.recipe_canvas_frame, anchor="nw")
        
        self.recipe_canvas_frame.bind(
            "<Configure>",
            lambda e: recipe_canvas.configure(scrollregion=recipe_canvas.bbox("all"))
        )
        recipe_canvas.configure(yscrollcommand=recipe_scrollbar.set)
        
        recipe_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        recipe_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def on_search_mode_changed(self):
        """Обработка изменения режима поиска"""
        mode = self.search_mode_var.get()
        
        # Скрываем/показываем элементы в зависимости от режима
        if mode == "ingredients":
            # Показываем панель продуктов, скрываем другие
            self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            self.selected_header.pack(fill=tk.X, pady=(0, 10))
            self.search_entry_frame.pack_forget()
            self.category_search_frame.pack_forget()
            self.status_bar.config(text="✅ Режим поиска по ингредиентам. Выберите продукты.")
            
        elif mode == "text":
            # Скрываем панель продуктов, показываем поле поиска
            self.left_panel.pack_forget()
            self.selected_header.pack_forget()
            self.search_entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.category_search_frame.pack_forget()
            self.status_bar.config(text="✅ Режим поиска по тексту. Введите название рецепта.")
            self.search_entry.focus()
            
        elif mode == "category":
            # Скрываем панель продуктов, показываем выбор категории
            self.left_panel.pack_forget()
            self.selected_header.pack_forget()
            self.search_entry_frame.pack_forget()
            self.category_search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.status_bar.config(text="✅ Режим поиска по категории. Выберите категорию рецептов.")
        
        # Очищаем результаты
        self.clear_recipes()
    
    def on_search_text_changed(self):
        """Обработка изменения текста поиска (поиск при вводе)"""
        if self.search_mode_var.get() == "text":
            # Задержка для избежания слишком частых поисков
            if hasattr(self, '_search_timer'):
                self.root.after_cancel(self._search_timer)
            
            self._search_timer = self.root.after(500, self.perform_search)  # Поиск через 500 мс
    
    def perform_search(self):
        """Выполнение поиска в зависимости от режима"""
        mode = self.search_mode_var.get()
        
        if mode == "ingredients":
            self.show_recipes()
        elif mode == "text":
            self.search_by_text()
        elif mode == "category":
            self.search_by_category()
    
    def search_by_text(self):
        """Поиск рецептов по тексту"""
        search_text = self.search_var.get().strip()
        
        if len(search_text) < 2:
            self.clear_recipes()
            tk.Label(
                self.recipe_canvas_frame, 
                text="🔍 Введите не менее 2 символов для поиска",
                font=('Segoe UI', 14), 
                fg=COLORS['text_secondary'], 
                bg=COLORS['background'],
                justify=tk.CENTER
            ).pack(expand=True, pady=100)
            return
        
        # Показываем индикатор загрузки
        for widget in self.recipe_canvas_frame.winfo_children():
            widget.destroy()
        
        loading_label = tk.Label(
            self.recipe_canvas_frame, 
            text=f"🔍 Ищем рецепты по запросу: '{search_text}'...",
            font=('Segoe UI', 14), 
            fg=COLORS['text_secondary'], 
            bg=COLORS['background'],
            justify=tk.CENTER
        )
        loading_label.pack(expand=True, pady=100)
        self.root.update()
        
        # Выполняем поиск
        results = self.db_manager.search_recipes_by_text(search_text)
        
        # Очищаем и показываем результаты
        for widget in self.recipe_canvas_frame.winfo_children():
            widget.destroy()
        
        if not results:
            tk.Label(
                self.recipe_canvas_frame, 
                text=f"😔 По запросу '{search_text}' ничего не найдено\nПопробуйте другой запрос",
                font=('Segoe UI', 14), 
                fg=COLORS['text_secondary'], 
                bg=COLORS['background'],
                justify=tk.CENTER
            ).pack(expand=True, pady=100)
            self.update_status(f"❌ По запросу '{search_text}' ничего не найдено")
            return
        
        # Заголовок с результатами
        header_frame = tk.Frame(self.recipe_canvas_frame, bg=COLORS['background'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            header_frame, 
            text=f"🔍 Найдено рецептов: {len(results)} по запросу '{search_text}'", 
            font=('Segoe UI', 14, 'bold'), 
            bg=COLORS['background']
        ).pack()
        
        # Показываем рецепты
        for recipe in results[:15]:  # Ограничиваем 15 результатами
            self.create_recipe_card(recipe)
        
        self.update_status(f"✅ Найдено {len(results)} рецептов по запросу '{search_text}'")
    
    def search_by_category(self):
        """Поиск рецептов по категории"""
        category = self.search_category_var.get()
        
        if category == "Все категории":
            self.clear_recipes()
            tk.Label(
                self.recipe_canvas_frame, 
                text="📁 Выберите категорию рецептов",
                font=('Segoe UI', 14), 
                fg=COLORS['text_secondary'], 
                bg=COLORS['background'],
                justify=tk.CENTER
            ).pack(expand=True, pady=100)
            return
        
        # Показываем индикатор загрузки
        for widget in self.recipe_canvas_frame.winfo_children():
            widget.destroy()
        
        loading_label = tk.Label(
            self.recipe_canvas_frame, 
            text=f"📁 Загружаем рецепты категории: '{category}'...",
            font=('Segoe UI', 14), 
            fg=COLORS['text_secondary'], 
            bg=COLORS['background'],
            justify=tk.CENTER
        )
        loading_label.pack(expand=True, pady=100)
        self.root.update()
        
        # Выполняем поиск
        results = self.db_manager.search_recipes_by_category(category)
        
        # Очищаем и показываем результаты
        for widget in self.recipe_canvas_frame.winfo_children():
            widget.destroy()
        
        if not results:
            tk.Label(
                self.recipe_canvas_frame, 
                text=f"😔 В категории '{category}' пока нет рецептов",
                font=('Segoe UI', 14), 
                fg=COLORS['text_secondary'], 
                bg=COLORS['background'],
                justify=tk.CENTER
            ).pack(expand=True, pady=100)
            self.update_status(f"❌ В категории '{category}' нет рецептов")
            return
        
        # Заголовок с результатами
        header_frame = tk.Frame(self.recipe_canvas_frame, bg=COLORS['background'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            header_frame, 
            text=f"📁 Рецепты категории '{category}': {len(results)}", 
            font=('Segoe UI', 14, 'bold'), 
            bg=COLORS['background']
        ).pack()
        
        # Показываем рецепты
        for recipe in results:
            self.create_recipe_card(recipe)
        
        self.update_status(f"✅ Найдено {len(results)} рецептов в категории '{category}'")
    
    def reset_search(self):
        """Сброс поиска"""
        self.search_var.set("")
        self.search_category_var.set("Все категории")
        self.selected_ingredients.clear()
        
        # Очищаем выбранные продукты
        for widget in self.selected_products_frame.winfo_children():
            widget.destroy()
        
        # Возвращаемся к режиму поиска по ингредиентам
        self.search_mode_var.set("ingredients")
        self.on_search_mode_changed()
        
        # Обновляем отображение
        self.update_counters()
        self.update_products_display(self.category_var.get())
        self.clear_recipes()
        
        self.update_status("✅ Поиск сброшен. Выберите продукты для поиска рецептов.")
    
    def get_recipe_categories(self):
        """Получение списка уникальных категорий рецептов"""
        self.db_manager.cursor.execute('SELECT DISTINCT category FROM Recipes ORDER BY category')
        categories = [row[0] for row in self.db_manager.cursor.fetchall()]
        return categories
    
    def create_ingredient_icon(self, parent, product_name, is_selected=False):
        """Создает иконку продукта"""
        # Получаем иконку
        icon_image = self.image_manager.get_or_create_ingredient_icon(product_name, is_selected)
        
        # Создаем фрейм для иконки
        icon_frame = tk.Frame(parent, bg=COLORS['background'], padx=5, pady=5)
        
        # Фрейм для изображения с обводкой
        img_frame = tk.Frame(icon_frame, 
                             bg=COLORS['selected_bg'] if is_selected else COLORS['surface'],
                             highlightbackground=COLORS['primary'] if is_selected else COLORS['border'],
                             highlightthickness=2,
                             relief=tk.SOLID,
                             width=70,
                             height=70)
        img_frame.pack_propagate(False)
        img_frame.pack()
        
        # Изображение
        img_label = tk.Label(img_frame, image=icon_image, bg=img_frame['bg'])
        img_label.image = icon_image  # Сохраняем ссылку
        img_label.pack(expand=True)
        
        # Название продукта
        name_label = tk.Label(icon_frame, text=product_name, 
                             font=('Segoe UI', 9),
                             bg=COLORS['background'],
                             fg=COLORS['text_primary'],
                             wraplength=70,
                             justify=tk.CENTER)
        name_label.pack(pady=(5, 0))
        
        # Обработчики событий
        def on_click(event):
            if is_selected:
                # Удаляем из выбранных
                self.selected_ingredients.discard(product_name)
                # Удаляем иконку
                icon_frame.destroy()
                # Обновляем счетчики
                self.update_counters()
                # Обновляем отображение продуктов в текущей категории
                self.update_products_display(self.category_var.get())
                # Если есть выбранные продукты, обновляем рецепты
                if self.selected_ingredients:
                    self.show_recipes()
                else:
                    self.clear_recipes()
            else:
                # Добавляем в выбранные
                self.selected_ingredients.add(product_name)
                # Создаем иконку в правой панели
                self.create_selected_icon(product_name)
                # Обновляем счетчики
                self.update_counters()
                # Удаляем продукт из отображения в текущей категории
                self.update_products_display(self.category_var.get())
                # Показываем рецепты
                self.show_recipes()
        
        def on_enter(e):
            if not is_selected:
                img_frame.config(bg=COLORS['hover_bg'])
                img_label.config(bg=COLORS['hover_bg'])
        
        def on_leave(e):
            if not is_selected:
                img_frame.config(bg=COLORS['surface'])
                img_label.config(bg=COLORS['surface'])
        
        # Привязываем события
        icon_frame.bind('<Button-1>', on_click)
        img_frame.bind('<Button-1>', on_click)
        img_label.bind('<Button-1>', on_click)
        name_label.bind('<Button-1>', on_click)
        
        icon_frame.bind('<Enter>', on_enter)
        icon_frame.bind('<Leave>', on_leave)
        img_frame.bind('<Enter>', on_enter)
        img_frame.bind('<Leave>', on_leave)
        
        return icon_frame
    
    def create_selected_icon(self, product_name):
        """Создает иконку выбранного продукта в правой панели"""
        # Создаем новую иконку с selected=True
        icon_image = self.image_manager.get_or_create_ingredient_icon(product_name, is_selected=True)
        
        # Создаем фрейм для иконки
        icon_frame = tk.Frame(self.selected_products_frame, bg=COLORS['background'], padx=5, pady=5)
        icon_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Фрейм для изображения с обводкой
        img_frame = tk.Frame(icon_frame, 
                             bg=COLORS['selected_bg'],
                             highlightbackground=COLORS['primary'],
                             highlightthickness=2,
                             relief=tk.SOLID,
                             width=70,
                             height=70)
        img_frame.pack_propagate(False)
        img_frame.pack()
        
        # Изображение
        img_label = tk.Label(img_frame, image=icon_image, bg=img_frame['bg'])
        img_label.image = icon_image  # Сохраняем ссылку
        img_label.pack(expand=True)
        
        # Название продукта
        name_label = tk.Label(icon_frame, text=product_name, 
                             font=('Segoe UI', 9),
                             bg=COLORS['background'],
                             fg=COLORS['text_primary'],
                             wraplength=70,
                             justify=tk.CENTER)
        name_label.pack(pady=(5, 0))
        
        # Обработчик удаления
        def on_click(event):
            self.selected_ingredients.discard(product_name)
            icon_frame.destroy()
            self.update_counters()
            # Обновляем отображение продуктов в текущей категории
            self.update_products_display(self.category_var.get())
            if self.selected_ingredients:
                self.show_recipes()
            else:
                self.clear_recipes()
        
        def on_enter(e):
            img_frame.config(bg=COLORS['hover_bg'])
            img_label.config(bg=COLORS['hover_bg'])
        
        def on_leave(e):
            img_frame.config(bg=COLORS['selected_bg'])
            img_label.config(bg=COLORS['selected_bg'])
        
        # Привязываем события
        icon_frame.bind('<Button-1>', on_click)
        img_frame.bind('<Button-1>', on_click)
        img_label.bind('<Button-1>', on_click)
        name_label.bind('<Button-1>', on_click)
        
        icon_frame.bind('<Enter>', on_enter)
        icon_frame.bind('<Leave>', on_leave)
    
    def update_products_display(self, category_filter="Все продукты"):
        """Обновляет отображение продуктов по категориям"""
        # Очищаем фреймы
        for widget in self.all_products_frame.winfo_children():
            widget.destroy()
        
        # Получаем продукты для отображения
        if category_filter == "Все продукты":
            products_to_show = [p for p in ALL_INGREDIENTS if p not in self.selected_ingredients]
        else:
            products_to_show = [p for p in INGREDIENT_CATEGORIES[category_filter] 
                              if p not in self.selected_ingredients]
        
        # Сортируем по алфавиту
        products_to_show.sort()
        
        # Если нет продуктов для отображения
        if not products_to_show:
            no_products_label = tk.Label(
                self.all_products_frame, 
                text="Все продукты из этой категории уже выбраны!\n\nВыберите другую категорию или удалите некоторые продукты из выбранных.",
                font=('Segoe UI', 12),
                fg=COLORS['text_secondary'],
                bg=COLORS['background'],
                justify=tk.CENTER
            )
            no_products_label.pack(expand=True, pady=50)
            return
        
        # Создаем сетку для продуктов
        rows_frame = tk.Frame(self.all_products_frame, bg=COLORS['background'])
        rows_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем Canvas для прокрутки
        canvas = tk.Canvas(rows_frame, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(rows_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['background'])
        
        # Привязываем события для прокрутки
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Создаем иконки в сетке 6x?
        row_frame = None
        col = 0
        
        for i, product in enumerate(products_to_show):
            if col % 6 == 0:
                row_frame = tk.Frame(scrollable_frame, bg=COLORS['background'])
                row_frame.pack(fill=tk.X, pady=5)
                col = 0
            
            icon = self.create_ingredient_icon(row_frame, product, is_selected=False)
            icon.pack(side=tk.LEFT, padx=5)
            col += 1
        
        # Обновляем счетчики
        self.update_counters()
    
    def update_counters(self):
        """Обновляет счетчики продуктов"""
        all_count = len(ALL_INGREDIENTS)
        selected_count = len(self.selected_ingredients)
        
        if self.label_all_count:
            self.label_all_count.config(text=f"Всего: {all_count}")
        if self.label_selected_count:
            self.label_selected_count.config(text=f"Выбрано: {selected_count}")
    
    def filter_by_category(self):
        """Фильтрует продукты по выбранной категории"""
        category = self.category_var.get()
        self.update_products_display(category)
    
    def show_recipes(self):
        """Показывает найденные рецепты"""
        # Очищаем старые результаты
        for widget in self.recipe_canvas_frame.winfo_children():
            widget.destroy()
        
        if not self.selected_ingredients:
            tk.Label(self.recipe_canvas_frame, text="👨‍🍳 Выберите продукты из списка слева\nчтобы найти подходящие рецепты",
                    font=('Segoe UI', 14), fg=COLORS['text_secondary'], bg=COLORS['background'],
                    justify=tk.CENTER).pack(expand=True, pady=100)
            return
        
        # Ищем рецепты
        results = self.db_manager.search_recipes_by_ingredients(self.selected_ingredients)
        
        if not results:
            tk.Label(self.recipe_canvas_frame, text="😔 Рецепты не найдены\nПопробуйте выбрать другие продукты",
                    font=('Segoe UI', 14), fg=COLORS['text_secondary'], bg=COLORS['background'],
                    justify=tk.CENTER).pack(expand=True, pady=100)
            return
        
        # Заголовок
        header_frame = tk.Frame(self.recipe_canvas_frame, bg=COLORS['background'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame, text=f"🍽 Найдено рецептов: {len(results)}", 
                font=('Segoe UI', 14, 'bold'), bg=COLORS['background']).pack()
        
        # Создаем карточки рецептов
        for recipe in results[:10]:  # Показываем первые 10 рецептов
            self.create_recipe_card(recipe)
    
    def create_recipe_card(self, recipe):
        """Создает карточку рецепта"""
        card_frame = tk.Frame(
            self.recipe_canvas_frame, 
            bg=COLORS['card_bg'],
            relief=tk.RAISED,
            bd=1,
            highlightbackground=COLORS['border'],
            highlightthickness=1
        )
        card_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Внутренний контейнер
        inner_frame = tk.Frame(card_frame, bg=COLORS['card_bg'], padx=15, pady=15)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Основной контент в горизонтальном расположении
        content_frame = tk.Frame(inner_frame, bg=COLORS['card_bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая часть - изображение
        left_image_frame = tk.Frame(content_frame, bg=COLORS['card_bg'], width=200)
        left_image_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_image_frame.pack_propagate(False)
        
        # Загружаем изображение (может быть заглушкой)
        recipe_image = self.image_manager.load_recipe_image(recipe.id, recipe.image_url, recipe.image_data)
        
        # Фрейм для изображения
        img_display_frame = tk.Frame(left_image_frame, bg=COLORS['surface'], 
                                    highlightbackground=COLORS['border'], 
                                    highlightthickness=1,
                                    width=200, height=150)
        img_display_frame.pack_propagate(False)
        img_display_frame.pack()
        
        # Отображаем изображение
        img_label = tk.Label(img_display_frame, image=recipe_image, bg=COLORS['surface'])
        img_label.image = recipe_image
        img_label.pack(expand=True, fill=tk.BOTH)
        
        # Кнопка добавления/смены фото
        add_photo_btn = tk.Button(left_image_frame, text="📷 Добавить фото", 
                                 command=lambda rid=recipe.id, rname=recipe.name: self.add_image_to_recipe(rid, rname),
                                 bg=COLORS['secondary_light'], fg='white',
                                 font=('Segoe UI', 9), relief=tk.FLAT,
                                 padx=10, pady=5, cursor='hand2')
        add_photo_btn.pack(pady=5)
        
        # Правая часть - информация о рецепте
        right_info_frame = tk.Frame(content_frame, bg=COLORS['card_bg'])
        right_info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Заголовок
        header_frame = tk.Frame(right_info_frame, bg=COLORS['card_bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Название рецепта
        name_label = tk.Label(
            header_frame, 
            text=recipe.name, 
            font=('Segoe UI', 16, 'bold'),
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        )
        name_label.pack(side=tk.LEFT)
        
        # Информация о совпадениях
        match_percentage = int(recipe.match_percentage)
        match_color = COLORS['success'] if match_percentage > 70 else COLORS['warning'] if match_percentage > 40 else COLORS['error']
        
        match_frame = tk.Frame(header_frame, bg=match_color)
        match_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        match_label = tk.Label(match_frame, 
                              text=f"✓{recipe.matches}/{recipe.selected_count} ({match_percentage}%)",
                              font=('Segoe UI', 10, 'bold'),
                              bg=match_color,
                              fg='white',
                              padx=8,
                              pady=2)
        match_label.pack()
        
        # Мета-информация
        meta_frame = tk.Frame(right_info_frame, bg=COLORS['card_bg'])
        meta_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(meta_frame, text=f"📁 {recipe.category}", 
                font=('Segoe UI', 11),
                fg=COLORS['primary'],
                bg=COLORS['card_bg']).pack(side=tk.LEFT, padx=(0, 15))
        
        # Сложность с цветом
        difficulty_colors = {
            'Легкая': COLORS['success'],
            'Средняя': COLORS['warning'],
            'Сложная': COLORS['error']
        }
        diff_color = difficulty_colors.get(recipe.difficulty, COLORS['text_secondary'])
        tk.Label(meta_frame, text=f"⚡ {recipe.difficulty}", 
                font=('Segoe UI', 11),
                fg=diff_color,
                bg=COLORS['card_bg']).pack(side=tk.LEFT, padx=(0, 15))
        
        # Время приготовления
        tk.Label(meta_frame, text=f"⏱ {recipe.prep_time} мин", 
                font=('Segoe UI', 11),
                fg=COLORS['text_secondary'],
                bg=COLORS['card_bg']).pack(side=tk.LEFT, padx=(0, 15))
        
        # Рейтинг
        tk.Label(meta_frame, text=f"⭐ {recipe.rating}", 
                font=('Segoe UI', 11),
                fg=COLORS['warning'],
                bg=COLORS['card_bg']).pack(side=tk.LEFT, padx=(0, 15))
        
        # Ингредиенты (первые 5)
        ingredients_list = [ing.strip() for ing in recipe.ingredients.split(',')]
        ingredients_text = ", ".join(ingredients_list[:5])
        if len(ingredients_list) > 5:
            ingredients_text += "..."
        
        ingredients_label = tk.Label(
            right_info_frame,
            text=f"🛒 {ingredients_text}",
            font=('Segoe UI', 11),
            fg=COLORS['text_primary'],
            bg=COLORS['card_bg'],
            wraplength=400,
            justify=tk.LEFT
        )
        ingredients_label.pack(fill=tk.X, pady=(0, 15))
        
        # Кнопка "Подробнее"
        details_btn = tk.Button(
            right_info_frame,
            text="📖 Подробнее",
            command=lambda rd=recipe: self.open_recipe_details(rd),
            bg=COLORS['primary'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        details_btn.pack(anchor=tk.W)
        
        # Эффект при наведении
        def on_enter(e):
            card_frame.config(bg=COLORS['hover_bg'])
            inner_frame.config(bg=COLORS['hover_bg'])
            content_frame.config(bg=COLORS['hover_bg'])
            left_image_frame.config(bg=COLORS['hover_bg'])
            right_info_frame.config(bg=COLORS['hover_bg'])
            header_frame.config(bg=COLORS['hover_bg'])
            meta_frame.config(bg=COLORS['hover_bg'])
            img_display_frame.config(bg=COLORS['hover_bg'])
            img_label.config(bg=COLORS['hover_bg'])
        
        def on_leave(e):
            card_frame.config(bg=COLORS['card_bg'])
            inner_frame.config(bg=COLORS['card_bg'])
            content_frame.config(bg=COLORS['card_bg'])
            left_image_frame.config(bg=COLORS['card_bg'])
            right_info_frame.config(bg=COLORS['card_bg'])
            header_frame.config(bg=COLORS['card_bg'])
            meta_frame.config(bg=COLORS['card_bg'])
            img_display_frame.config(bg=COLORS['surface'])
            img_label.config(bg=COLORS['surface'])
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
    
    def open_recipe_details(self, recipe):
        """Открывает детальное окно с рецептом"""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Рецепт: {recipe.name}")
        details_window.geometry("800x800")
        details_window.configure(bg='white')
        
        # Заголовок
        header_frame = tk.Frame(details_window, bg=COLORS['primary'], height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=recipe.name, 
                font=('Segoe UI', 18, 'bold'), bg=COLORS['primary'], 
                fg='white').pack(expand=True)
        
        # Кнопка добавления фото в заголовке
        add_btn = tk.Button(header_frame, text="📷 Добавить фото", 
                           command=lambda: self.add_image_to_recipe(recipe.id, recipe.name),
                           bg=COLORS['secondary_light'], fg='white',
                           font=('Segoe UI', 10), relief=tk.FLAT,
                           padx=10, pady=3)
        add_btn.pack(side=tk.RIGHT, padx=10)
        
        # Основной контент с прокруткой
        main_frame = tk.Frame(details_window, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Изображение рецепта (большое)
        image_frame = tk.Frame(main_frame, bg='white')
        image_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Загружаем изображение в большем размере
        recipe_image_large = None
        try:
            # Пробуем загрузить полноразмерное изображение
            local_path = RECIPE_IMAGES_DIR / f"recipe_{recipe.id}.jpg"
            if local_path.exists():
                img = Image.open(local_path)
                # Ограничиваем размер для отображения
                max_size = (600, 300)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                recipe_image_large = ImageTk.PhotoImage(img)
            else:
                # Используем стандартное изображение или заглушку
                recipe_image_large = self.image_manager.load_recipe_image(recipe.id, 
                                                                         recipe.image_url, 
                                                                         recipe.image_data)
        except:
            recipe_image_large = self.image_manager.load_recipe_image(recipe.id)
        
        if recipe_image_large:
            img_label = tk.Label(image_frame, image=recipe_image_large, bg='white')
            img_label.image = recipe_image_large
            img_label.pack()
        
        # Создаем Canvas для прокрутки остального контента
        canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Информация о рецепте
        info_frame = tk.Frame(scrollable_frame, bg='white')
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Детали в строку
        details_row = tk.Frame(info_frame, bg='white')
        details_row.pack()
        
        # Категория
        tk.Label(details_row, text=f"📁 {recipe.category}", 
                font=('Segoe UI', 11), bg='white').pack(side=tk.LEFT, padx=10)
        
        # Время
        tk.Label(details_row, text=f"⏱ {recipe.prep_time} мин", 
                font=('Segoe UI', 11), bg='white').pack(side=tk.LEFT, padx=10)
        
        # Сложность
        difficulty_colors = {
            'Легкая': COLORS['success'],
            'Средняя': COLORS['warning'],
            'Сложная': COLORS['error']
        }
        diff_color = difficulty_colors.get(recipe.difficulty, COLORS['text_secondary'])
        tk.Label(details_row, text=f"⚡ {recipe.difficulty}", 
                font=('Segoe UI', 11), fg=diff_color, bg='white').pack(side=tk.LEFT, padx=10)
        
        # Рейтинг
        tk.Label(details_row, text=f"⭐ {recipe.rating}", 
                font=('Segoe UI', 11), fg=COLORS['warning'], bg='white').pack(side=tk.LEFT, padx=10)
        
        # Ингредиенты
        tk.Label(scrollable_frame, text="🛒 Ингредиенты:", 
                font=('Segoe UI', 14, 'bold'), bg='white', anchor=tk.W).pack(anchor=tk.W, pady=(0, 10))
        
        ingredient_list = [ing.strip() for ing in recipe.ingredients.split(',')]
        for ingredient in ingredient_list:
            ing_frame = tk.Frame(scrollable_frame, bg='white')
            ing_frame.pack(fill=tk.X, pady=3)
            
            # Название ингредиента
            tk.Label(ing_frame, text=f"• {ingredient}", font=('Segoe UI', 12), 
                    bg='white').pack(side=tk.LEFT, padx=10)
            
            # Индикатор выбора
            if ingredient.lower() in [i.lower() for i in self.selected_ingredients]:
                tk.Label(ing_frame, text="✓", font=('Segoe UI', 12, 'bold'), 
                        fg=COLORS['success'], bg='white').pack(side=tk.RIGHT)
        
        # Инструкции приготовления
        tk.Label(scrollable_frame, text="📝 Способ приготовления:", 
                font=('Segoe UI', 14, 'bold'), bg='white', anchor=tk.W).pack(anchor=tk.W, pady=(20, 10))
        
        instructions_text = tk.Text(scrollable_frame, height=15, width=65, 
                                   font=('Segoe UI', 11), wrap=tk.WORD, bg='#F9F9F9')
        instructions_text.pack(fill=tk.X, pady=(0, 20))
        instructions_text.insert('1.0', recipe.instructions)
        instructions_text.config(state='disabled')
        
        # Кнопка закрытия
        tk.Button(details_window, text="✕ Закрыть", command=details_window.destroy,
                 bg=COLORS['error'], fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10, relief=tk.FLAT).pack(pady=10)
        
        # Центрируем окно
        details_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 800) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 800) // 2
        details_window.geometry(f"+{x}+{y}")
    
    def add_image_to_recipe(self, recipe_id, recipe_name):
        """Добавляет изображение к рецепту"""
        # Диалог выбора источника
        source_window = tk.Toplevel(self.root)
        source_window.title("Добавить изображение")
        source_window.geometry("400x250")
        source_window.configure(bg=COLORS['background'])
        source_window.transient(self.root)
        source_window.grab_set()
        
        # Центрируем окно
        source_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 250) // 2
        source_window.geometry(f"+{x}+{y}")
        
        # Заголовок
        tk.Label(source_window, text=f"Добавить фото для рецепта:", 
                font=('Segoe UI', 14, 'bold'), bg=COLORS['background']).pack(pady=20)
        
        tk.Label(source_window, text=f"«{recipe_name}»", 
                font=('Segoe UI', 12), bg=COLORS['background'], fg=COLORS['primary']).pack()
        
        # Кнопки выбора
        btn_frame = tk.Frame(source_window, bg=COLORS['background'])
        btn_frame.pack(pady=30)
        
        def from_file():
            source_window.destroy()
            file_path = filedialog.askopenfilename(
                title="Выберите изображение",
                filetypes=[
                    ("Изображения", "*.jpg *.jpeg *.png *.bmp *.gif"),
                    ("Все файлы", "*.*")
                ]
            )
            if file_path:
                self.process_image_file(recipe_id, file_path)
        
        def from_url():
            source_window.destroy()
            self.ask_for_url(recipe_id, recipe_name)
        
        def from_camera():
            source_window.destroy()
            messagebox.showinfo("Камера", "Функция съемки с камеры будет добавлена в следующей версии")
        
        tk.Button(btn_frame, text="📁 Из файла", command=from_file,
                 bg=COLORS['primary'], fg='white', font=('Segoe UI', 11),
                 padx=20, pady=10, width=15).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="🌐 Из интернета", command=from_url,
                 bg=COLORS['secondary'], fg='white', font=('Segoe UI', 11),
                 padx=20, pady=10, width=15).pack(side=tk.LEFT, padx=10)
        
        # Кнопка отмены
        tk.Button(source_window, text="Отмена", command=source_window.destroy,
                 bg=COLORS['text_secondary'], fg='white', font=('Segoe UI', 10),
                 padx=20, pady=5).pack(pady=10)
    
    def ask_for_url(self, recipe_id, recipe_name):
        """Запрашивает URL изображения"""
        url_window = tk.Toplevel(self.root)
        url_window.title("Добавить изображение из интернета")
        url_window.geometry("500x200")
        url_window.configure(bg=COLORS['background'])
        url_window.transient(self.root)
        url_window.grab_set()
        
        # Центрируем окно
        url_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 500) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 200) // 2
        url_window.geometry(f"+{x}+{y}")
        
        # Заголовок
        tk.Label(url_window, text=f"URL изображения для рецепта:", 
                font=('Segoe UI', 12, 'bold'), bg=COLORS['background']).pack(pady=10)
        
        tk.Label(url_window, text=f"«{recipe_name}»", 
                font=('Segoe UI', 11), bg=COLORS['background'], fg=COLORS['primary']).pack()
        
        # Поле ввода URL
        url_frame = tk.Frame(url_window, bg=COLORS['background'])
        url_frame.pack(pady=20, padx=20, fill=tk.X)
        
        tk.Label(url_frame, text="URL:", 
                font=('Segoe UI', 10), bg=COLORS['background']).pack(side=tk.LEFT)
        
        url_var = tk.StringVar(value="https://")
        url_entry = tk.Entry(url_frame, textvariable=url_var, font=('Segoe UI', 10),
                            bg=COLORS['surface'], relief=tk.SOLID, width=40)
        url_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        url_entry.select_range(0, tk.END)
        url_entry.focus()
        
        # Примеры URL
        example_frame = tk.Frame(url_window, bg=COLORS['background'])
        example_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(example_frame, text="Пример: https://example.com/image.jpg", 
                font=('Segoe UI', 9), bg=COLORS['background'], fg=COLORS['text_secondary']).pack(anchor=tk.W)
        
        # Кнопки
        btn_frame = tk.Frame(url_window, bg=COLORS['background'])
        btn_frame.pack(pady=10)
        
        def load_from_url():
            url = url_var.get().strip()
            if url and url.startswith('http'):
                url_window.destroy()
                self.load_and_save_image_from_url(recipe_id, url)
            else:
                messagebox.showerror("Ошибка", "Пожалуйста, введите корректный URL (начинается с http/https)")
        
        tk.Button(btn_frame, text="📥 Загрузить", command=load_from_url,
                 bg=COLORS['primary'], fg='white', font=('Segoe UI', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Отмена", command=url_window.destroy,
                 bg=COLORS['text_secondary'], fg='white', font=('Segoe UI', 10),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
    
    def load_and_save_image_from_url(self, recipe_id, url):
        """Загружает и сохраняет изображение из URL"""
        try:
            # Показываем индикатор загрузки
            if self.status_bar:
                self.status_bar.config(text=f"⏳ Загружаем изображение из {url[:30]}...", fg=COLORS['warning'])
            self.root.update()
            
            # Загружаем изображение
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Сохраняем в файл
                local_path = RECIPE_IMAGES_DIR / f"recipe_{recipe_id}.jpg"
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                # Обновляем базу данных
                self.db_manager.update_recipe_image_url(recipe_id, url)
                
                # Очищаем кэш для этого рецепта
                self.image_manager.recipe_images = {k: v for k, v in self.image_manager.recipe_images.items() if str(recipe_id) not in k}
                
                # Перезагружаем рецепты если они отображаются
                if self.selected_ingredients:
                    self.show_recipes()
                
                if self.status_bar:
                    self.status_bar.config(text=f"✅ Изображение успешно загружено и сохранено", fg=COLORS['success'])
                messagebox.showinfo("Успех", "Изображение успешно загружено и сохранено!")
            else:
                if self.status_bar:
                    self.status_bar.config(text="❌ Ошибка при загрузке изображения", fg=COLORS['error'])
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение. Код ошибки: {response.status_code}")
                
        except Exception as e:
            if self.status_bar:
                self.status_bar.config(text="❌ Ошибка при загрузке изображения", fg=COLORS['error'])
            messagebox.showerror("Ошибка", f"Ошибка при загрузке изображения: {str(e)}")
    
    def process_image_file(self, recipe_id, file_path):
        """Обрабатывает выбранный файл изображения"""
        try:
            if self.status_bar:
                self.status_bar.config(text=f"⏳ Обрабатываем изображение...", fg=COLORS['warning'])
            self.root.update()
            
            # Открываем и проверяем изображение
            img = Image.open(file_path)
            
            # Показываем предпросмотр
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Предпросмотр изображения")
            preview_window.geometry("400x400")
            preview_window.configure(bg=COLORS['background'])
            preview_window.transient(self.root)
            
            # Центрируем окно
            preview_window.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
            y = self.root.winfo_y() + (self.root.winfo_height() - 400) // 2
            preview_window.geometry(f"+{x}+{y}")
            
            # Предпросмотр
            img_preview = img.copy()
            img_preview.thumbnail((300, 300), Image.Resampling.LANCZOS)
            photo_preview = ImageTk.PhotoImage(img_preview)
            
            preview_label = tk.Label(preview_window, image=photo_preview, bg=COLORS['background'])
            preview_label.image = photo_preview
            preview_label.pack(pady=20)
            
            # Информация об изображении
            info_text = f"Размер: {img.width}x{img.height}\nФормат: {img.format}\nФайл: {os.path.basename(file_path)}"
            tk.Label(preview_window, text=info_text, font=('Segoe UI', 10), 
                    bg=COLORS['background']).pack()
            
            # Кнопки
            btn_frame = tk.Frame(preview_window, bg=COLORS['background'])
            btn_frame.pack(pady=20)
            
            def save_image():
                try:
                    # Сохраняем в директорию рецептов
                    local_path = RECIPE_IMAGES_DIR / f"recipe_{recipe_id}.jpg"
                    img.save(local_path, 'JPEG', quality=90)
                    
                    # Обновляем базу данных
                    self.db_manager.update_recipe_image_url(recipe_id, None)
                    
                    # Очищаем кэш
                    self.image_manager.recipe_images = {k: v for k, v in self.image_manager.recipe_images.items() if str(recipe_id) not in k}
                    
                    # Перезагружаем рецепты если они отображаются
                    if self.selected_ingredients:
                        self.show_recipes()
                    
                    preview_window.destroy()
                    if self.status_bar:
                        self.status_bar.config(text="✅ Изображение успешно сохранено", fg=COLORS['success'])
                    messagebox.showinfo("Успех", "Изображение успешно сохранено!")
                    
                except Exception as e:
                    preview_window.destroy()
                    if self.status_bar:
                        self.status_bar.config(text="❌ Ошибка при сохранении изображения", fg=COLORS['error'])
                    messagebox.showerror("Ошибка", f"Ошибка при сохранении изображения: {str(e)}")
            
            def cancel():
                preview_window.destroy()
                if self.status_bar:
                    self.status_bar.config(text="❌ Отменено", fg=COLORS['text_secondary'])
            
            tk.Button(btn_frame, text="💾 Сохранить", command=save_image,
                     bg=COLORS['primary'], fg='white', font=('Segoe UI', 10, 'bold'),
                     padx=20, pady=5).pack(side=tk.LEFT, padx=10)
            
            tk.Button(btn_frame, text="Отмена", command=cancel,
                     bg=COLORS['text_secondary'], fg='white', font=('Segoe UI', 10),
                     padx=20, pady=5).pack(side=tk.LEFT, padx=10)
            
        except Exception as e:
            if self.status_bar:
                self.status_bar.config(text="❌ Ошибка при обработке изображения", fg=COLORS['error'])
            messagebox.showerror("Ошибка", f"Не удалось открыть изображение: {str(e)}")
    
    def clear_selection(self):
        """Очищает выбранные продукты"""
        self.selected_ingredients.clear()
        
        # Обновляем отображение
        self.update_products_display(self.category_var.get())
        # Очищаем выбранные продукты
        for widget in self.selected_products_frame.winfo_children():
            widget.destroy()
        
        self.update_counters()
        self.clear_recipes()
        self.update_status("✅ Выбор очищен")
    
    def clear_recipes(self):
        """Очищает область с рецептами"""
        for widget in self.recipe_canvas_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.recipe_canvas_frame, text="👨‍🍳 Выберите продукты из списка слева\nчтобы найти подходящие рецепты",
                font=('Segoe UI', 14), fg=COLORS['text_secondary'], bg=COLORS['background'],
                justify=tk.CENTER).pack(expand=True, pady=100)
    
    def update_status(self, message, is_error=False):
        """Обновляет статус бар"""
        if self.status_bar:
            self.status_bar.config(text=message)
            if is_error:
                self.status_bar.config(fg=COLORS['error'])
            else:
                self.status_bar.config(fg=COLORS['text_secondary'])


# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = KitchenAssistant(root)
    
    # Настройка размеров окна
    root.geometry("1400x900")  # Немного увеличили для панели поиска
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 1400
    window_height = 900
    position_x = int(screen_width / 2 - window_width / 2)
    position_y = int(screen_height / 2 - window_height / 2)
    root.geometry(f'{window_width}x{window_height}+{position_x}+{position_y}')
    root.minsize(1200, 700)
    
    print("Приложение запущено")
    print(f"Всего продуктов: {len(ALL_INGREDIENTS)}")
    print(f"Всего рецептов: {len(recipes_data)}")
    print(f"Доступные режимы поиска: по ингредиентам, по названию, по категории")
    
    root.mainloop()