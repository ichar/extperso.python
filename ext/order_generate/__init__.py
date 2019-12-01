# -*- coding: cp1251 -*-

# ------------------ #
#   order.generate   #
# ------------------ #

from app.types.actions import *
from app.types.statuses import *

from ..defaults import *

from . import otkrytie
from . import postbank
from . import raund_megafon

"""
    Методы (атрибуты) базового класса.

    Функция-генератор дополнительных данных в заказе
    ------------------------------------------------

        `custom`    --  генератор XML-контента заказа

    Назначение: генерация узлов дерева, создание дополнительных тегов, модификация
    структуры контента.

    Функция декларации списка тегов для анализа генератором контента заказа
    -----------------------------------------------------------------------

        `tags`      --  теги заказа

    Назначение: определение списка тегов для обработки вида.

    Список тегов по умолчанию: 

        ('FileBody_Record',)

    Аргументы: нет.

    Возвращаемое значение: 

        tuple   -- кортеж имен тегов
"""

# ----------------------------------------------- #
#   FileType : FileStatus From-To-Error : Attrs   #
# ----------------------------------------------- #

scenario = [
    #('Dolinsk',
    #    [STATUS_DATA_VERIFIED, STATUS_ACCEPTED],
    #    {
    #        'custom' : dolinsk.custom,
    #    },
    #),
    # -------------
    # БАНК ОТКРЫТИЕ
    # -------------
    #(0, 'Otkrytie_v1',
    #    [STATUS_DATA_CHECKED, STATUS_DATA_GENERATED, STATUS_REJECTED_INVALID],
    #    {
    #        'tags'   : otkrytie.tags,
    #        'custom' : otkrytie.custom,
    #    },
    #),
    # ----------
    # ПОЧТА БАНК
    # ----------
    (0, 'PostBank_v1',
        [STATUS_DATA_CHECKED, postbank.status_to, STATUS_REJECTED_INVALID],
        {
            'tags'   : postbank.tags,
            'custom' : postbank.custom_step1,
        },
    ),
    (0, 'PostBank_v1',
        [STATUS_ON_GROUPED, STATUS_FILTER_VERIFIED, STATUS_REJECTED_INVALID],
        {
            'tags'   : everything,
            'custom' : postbank.custom_step2,
            'phases' : 2,

            'keep_history' : 1,
        },
    ),
    (0, 'PostBank_v1',
        [STATUS_FILTER_VERIFIED, STATUS_DATA_GENERATED, STATUS_REJECTED_INVALID],
        {
            'tags'   : everything,
            'custom' : postbank.custom_step3,

            'keep_history' : 1,
        },
    ),
    (0, 'PostBank_ID',
        [STATUS_DATA_CHECKED, STATUS_ON_CHECK_ICARD, STATUS_REJECTED_INVALID],
        {
            'tags'   : postbank.tags,
            'custom' : postbank.custom_step1,
        },
    ),
    (0, 'PostBank_IDM',
        [STATUS_DATA_CHECKED, STATUS_ON_CHECK_ICARD, STATUS_REJECTED_INVALID],
        {
            'tags'   : postbank.tags,
            'custom' : postbank.custom_step1,
        },
    ),
    (0, 'PostBank_X5',
        [STATUS_DATA_CHECKED, postbank.status_to, STATUS_REJECTED_INVALID],
        {
            'tags'   : postbank.tags,
            'custom' : postbank.custom_step1,
        },
    ),
    (0, 'PostBank_X5',
        [STATUS_ON_GROUPED, STATUS_FILTER_VERIFIED, STATUS_REJECTED_INVALID],
        {
            'tags'   : everything,
            'custom' : postbank.custom_step2,
            'phases' : 2,

            'keep_history' : 1,
        },
    ),
    (0, 'PostBank_X5',
        [STATUS_FILTER_VERIFIED, STATUS_DATA_GENERATED, STATUS_REJECTED_INVALID],
        {
            'tags'   : everything,
            'custom' : postbank.custom_step3,

            'keep_history' : 1,
        },
    ),
    # ------------------------------------------
    # РЕГИСТРАЦИЯ ОТПРАВЛЕНИЙ ПОЧТАРОССИИ-ОНЛАЙН
    # ------------------------------------------
    (1, 'PostBank_v1',  
        [STATUS_BANKCHIP_READY, postbank.status_postonline_to, STATUS_ON_SUSPENDED],
        {
            'tags'   : everything,
            'custom' : postbank.custom_postonline,
            'phases' : 2,

            'keep_history' : 1,
        },
    ),
    (1, 'PostBank_v1',  
        [STATUS_POST_ONLINE_STARTED, STATUS_POST_ONLINE_FINISHED, STATUS_ON_SUSPENDED],
        {
            'tags'   : processinfo,
            'custom' : postbank.custom_postonline_sender,

            'keep_history' : 1,
        },
    ),
    (1, 'PostBank_ID',  
        [STATUS_BANKCHIP_READY, postbank.status_postonline_to, STATUS_ON_SUSPENDED],
        {
            'tags'   : everything,
            'custom' : postbank.custom_postonline,
            'phases' : 2,

            'keep_history' : 1,
        },
    ),
    (1, 'PostBank_ID',  
        [STATUS_POST_ONLINE_STARTED, STATUS_POST_ONLINE_FINISHED, STATUS_ON_SUSPENDED],
        {
            'tags'   : processinfo,
            'custom' : postbank.custom_postonline_sender,

            'keep_history' : 1,
        },
    ),
    (1, 'PostBank_IDM',  
        [STATUS_BANKCHIP_READY, postbank.status_postonline_to, STATUS_ON_SUSPENDED],
        {
            'tags'   : everything,
            'custom' : postbank.custom_postonline,
            'phases' : 2,

            'keep_history' : 1,
        },
    ),
    (1, 'PostBank_IDM',  
        [STATUS_POST_ONLINE_STARTED, STATUS_POST_ONLINE_FINISHED, STATUS_ON_SUSPENDED],
        {
            'tags'   : processinfo,
            'custom' : postbank.custom_postonline_sender,

            'keep_history' : 1,
        },
    ),
    (1, 'PostBank_X5',  
        [STATUS_BANKCHIP_READY, postbank.status_postonline_to, STATUS_ON_SUSPENDED],
        {
            'tags'   : everything,
            'custom' : postbank.custom_postonline,
            'phases' : 2,

            'keep_history' : 1,
        },
    ),
    (1, 'PostBank_X5',  
        [STATUS_POST_ONLINE_STARTED, STATUS_POST_ONLINE_FINISHED, STATUS_ON_SUSPENDED],
        {
            'tags'   : processinfo,
            'custom' : postbank.custom_postonline_sender,

            'keep_history' : 1,
        },
    ),
    # ------------------
    # БАНК РАУНД МЕГАФОН
    # ------------------
    #(0, 'Raund_Megafon',
    #    [STATUS_DATA_GENERATED, STATUS_PINGEN_FINISHED],
    #    {
    #        'custom' : raund_megafon.custom, 
    #    },
    #),
    # ------------
    # Обслуживание
    # ------------
    """
    (1, 'PostBank_v1',  
        [21, 0],
        {
            'tags'   : everything,
            'custom' : postbank.custom_postonline,
            'phases' : 2,
            'forced' : 287884,

            'change_status' : 0,
        },
    ),
    (1, 'PostBank_v1',  
        [198, 0],
        {
            'tags'   : processinfo,
            'custom' : postbank.custom_postonline_sender,
            'forced' : 287884,

            'change_status' : 0,
        },
    ),
    (1, 'PostBank_v1',
        [21, 0,],
        {
            'tags'   : everything,
            'custom' : postbank.change_delivery_date,
            'params' : {'date' : '16.05.2019'},
            'forced' : 296750,

            'change_status' : 0,
        },
    ),
    (1, 'PostBank_X5',
        [21, 0,],
        {
            'tags'   : everything,
            'custom' : postbank.change_delivery_date,
            'params' : {'date' : '23.10.2019', 'auto' : 0},
            'forced' : 218281,

            'change_status' : 0,
        },
    ),
    (1, 'PostBank_v1',
        [6, 0,],
        {
            'custom' : postbank.checker,
            'forced' : 294508,

            'change_status' : 0,
        },
    ),
    (1, 'PostBank_ID',
        [78, 4,],
        {
            'forced' : 294508,
        },
    ),
    (1, 'PostBank_v1',
        [21, 0,],
        {
            'tags'   : everything,
            'custom' : postbank.restart_perso,
            'forced' : 295625,

            'change_status' : 0,
        },
    ),
    (1, 'PostBank_v1',
        [27, 0,],
        {
            'tags'   : everything,
            'custom' : postbank.restart_inc_cards,
            'forced' : 295709,

            'change_status' : 0,
        },
    ),
    """
]
