# -*- coding: utf-8 -*-

BUTTONS = {'enter_in_random_order': {'ru': ' В случайном порядке'},
           'start_brute_force': {'ru': 'Начать перебор'},
           'copy_codes': {'ru': 'Скопировать коды'},
           'paste_codes': {'ru': 'Вставить коды'},
           'settings': {'ru': 'Настройки'},
           'code_generator': {'ru': 'Генератор кодов'},
           'anagrams': {'ru': 'Анаграммы'},
           'clear': {'ru': 'Очистить'},
           'add_latin': {'ru': 'Добавить ЛАТИНИЦУ'},
           'add_cyrillic': {'ru': 'Добавить КИРИЛЛИЦУ'},
           'add_ukrainian': {'ru': 'Добавить УКРАИНСКИЕ'},
           'add_digits': {'ru': 'Добавить ЦИФРЫ'},
           'add_symbols': {'ru': 'Добавить ПУНКТУАЦИЮ'},
           'preview': {'ru': 'Просмотр'},
           'add_codes': {'ru': 'Добавить коды'},
           'cancel': {'ru': 'Отмена'},
           'search_words': {'ru': 'Поиск слов'},
           'help': {'ru': 'Помощь'},
           'save': {'ru': 'Сохранить'}}

LABELS = {'anagrams_letters': {'ru': 'Набор букв для анаграммирования:'},
          'length': {'ru': ' Длина:'},
          'mask': {'ru': ' Маска:'},
          'use_mask': {'ru': ' Использовать маску'},
          'leave_order': {'ru': ' Сохранять порядок букв'},
          'search_result': {'ru': ' Результат поиска:'},
          'dictionary': {'ru': ' Словарь:'},
          'symbols_to_generate': {'ru': ' Набор символов для генерации:'},
          'codes_length': {'ru': ' Длина кодов (от ... до ...):'},
          'preview': {'ru': ' Просмотр:'}}

HEADERS = {'main': {'ru': 'PrideBot'},
           'settings': {'ru': 'Настройки'},
           'code_generator': {'ru': 'Генератор кодов:'},
           'anagrams': {'ru': ' Анаграмматор'}}

HELPERS = {
    "anagram": {
        'ru': """
        Чтобы вывести все коды из словаря - укажите только %
        В поле длины можно указать:
            =0 - анаграмма будет делаться только из букв, введеных в поле ввода
            <4, >4 - длина генерируемых слов больше или меньше указанного числа

        Также, можно делать SQL инъекции, например, если ввести:
            <10 AND LEN(word)>5 - в результате будут все слова,
            длина которых между 5 и 10 символами.
         Для инъекции можно использовать имя столбца word - в нем хранятся слова.

        В маске используются регулярные выражения
        Основы:
            . - любая буква один раз
            .* - сколько угодно каких угодно букв
            .+ - 1 и больше каких угодно букв
            ^ - начало строки
            $ - конец строки
            [A-Z] - набор букв
        Поиск с учетом регистра!

        Например, чтобы найти все слова, которые начинаются
        на дра и заканчиваются на га:
            1. В поле "Буквы для анаграммы" вводим %
            2. В поле маска вводим:
                ^дра.*га$
            3. Ставим галочку "Использовать маску"
                ...
            Профит!

            Если надо найти все слова, внутри которых есть дра.*га - можно записать так:
            дра.*га
        """},
    "settings": {
        "ru": """
        Для локаторов элементов вводите значение в формате:
        %by%=%value%
        Где возможны варианты::
        - id (для quest.ua id=txtLogin - поле логина)
        - name (для play.cq.com.ua name="code" - поле для ввода кода)
        - css
        - class
        - xpath (например: xpath=//*[@id="gbqfq"] )
        - tag
        Если не нужно выполнять логин в систему - login = ''

        Лимит числа генерируемых кодов отсутсвует, если = 0
        Обратите внимание, что генерация кодов с длиной больше 6 -
        забирает невероятно много времени. Оно того не стоит.
        """}}

LOGS = {"codes_found": {"ru": u'Найдено кодов в словаре: %s за %s секунд'},
        "words_filtered": {"ru": u'Отфильтровано слов: %s за %s секунд'},
        "no_words_found": {"ru": u'Не найдено слов, удовлетворяющих запрос'},
        "wrong_field_length_from": {"ru": u'Неверное число в поле "длина от"'},
        "wrong_field_length_to": {"ru": u'Неверное число в поле "длина до"'},
        "created_codes": {"ru": u'Создано %s кодов за %s секунд'},
        "limit_exceeded": {"ru": u'Слишком много комбинаций: %s. На данный момент лимит: %s'},
        "trying_code": {"ru": u'Пробуем код: %s'},
        "error_occurred_stopping": {"ru": u'Возникла ошибка во время ввода кода. Остановка перебора...'},
        "codes_tried": {"ru": u'Перебрано кодов: %s за %s секунд'},
        "error_during_login": {"ru": u'Ошибка во время логина. Остановка...'},
        "error_during_opening_url": {"ru": u'Ошибка во время открытия адреса. Остановка...'},
        "unknown_error": {"ru": u'Неизвестная ошибка. Остановка...'},
        "no_codes_for_bruteforce": {"ru": u'Не задан набор кодов для перебора'},
        "trying_to_login": {"ru": u'Пробуем залогиниться'},
        "opening_firefox": {"ru": u'Открываем Firefox...'},
        "opening_login_page": {"ru": u'Открываем страницу логина'},
        "opening_game_page": {"ru": u'Открываем страничку с игрой'},
        "waiting_before_next_code": {"ru": u'Ждем %s секунд до ввода'},
        "can_not_find_code_field": {"ru": u"Не могу найти поле для ввода. Через 5 секунд попытка будет повторена."},
        "nothing_to_insert": {"ru": u"Буфер обмена пуст."},
        }

LANGUAGE = 'ru'
