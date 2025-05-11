import asyncio

structure_menu = {
    "Основное меню": {
        "📋 Каталоги товаров и цен": "Каталоги товаров и цен",
        "📦 Закупка оптом": {
            "Проекторы": {
                "Everycom": [
                    "Rondo",
                    "Cabulite max",
                    "Cabulite mini",
                    "HQ9W ultra(HQ10W)",
                    "YG628 ULtra",
                    "HY300PRO(Genunine)",
                    "A10",
                    "K1",
                    "K2",
                    "C1",
                    "P30",
                    "HY320",
                    "H50",
                    "H5PRO",
                    "X30wpro",
                    "H6 PRO",
                    "H6 MAX",
                    "Q10W Max",
                    "RD828W",
                    "E700 PRO",
                    "E700 2K MAX"
                ],
                "Dangei": [
                    "Mars pro 2"
                ],
                "Formovie":[
                    "Theater Premium LaserTV"
                ],
                "AWOL":[
                    "LTV-3000pro",
                    "LTV-3500pro"
                ],
                "💰 Каталог с ценами": "💰 Проекторы"
            },
            "Экраны для проекторов": [
                "Настенный с элеткроприводом",
                "Настенный с механическим",
                "На штативе",
                "Наполный выдвижной для UST",
                "Настенный для UST"
                ],
            "GPU (графические процессоры)": {
                "Nvidia": [
                    "A4000",
                    "A6000E",
                    "RTX6000 ADA",
                    "H100 80G",
                    "H100 NVL 94G",
                    "H200 NVL 141G"
                ]
            },
            "Серверные материнские платы": {
                "Supermicro motherboard": [
                    "X10 DAI",
                    "X11SSL-F",
                    "X11SPL-F",
                    "X11SSM-F",
                    "X11DPI-N",
                ]
            },
            "CPU (центральные процессоры)": {
                "AMD": [
                    "AMD 7713"
                ]
            },
            "HDD (жесткие диски)": {
                "Seagate HDD": [
                    "ST8000NM017B",
                    "ST10000NM017B",
                    "ST10000NM018B",
                    "ST16000NM000J",
                    "ST16000NM004J",
                    "ST18000NM000J",
                    "ST18000NM004J",
                    "ST20000NM007D",
                    "ST20000NM002H",
                    "ST600MM0009",
                    "ST1800MM0129",
                    "ST2400MM0129"
                ]
            },
            "Лазерные сканеры": {
                "Shenzhen DYscan": [
                    "DI...",
                    "DS...",
                    "DF...",
                    "DP...",
                    "DE..."
                ],
                "💰 Каталог с ценами": "💰 Сканеры"
            },
            "Чехлы и кейсы": {
                "XUNDD": [
                    "New case series",
                    "Fold & Flip Case",
                    "Magnetic With Holder Case",
                    "Magnetic Case",
                    "Beatle 1",
                    "Beatle 2",
                    "Other Case",
                    "iPad Cover",
                    "Keyboard Cover"
                ]


            },
            "Беспроводные наушники": {
                "XUNDD": [
                    "B series",
                    "D series",
                    "H series",
                    "W series",
                    "X series"
                ],
                "BAVIN": [
                    "BH series",
                    "BAVIN series",
                    "MP series",
                    "💰 Каталог с ценами"
                ]


            },
            "Проводные наушники и аксессуары": {
                "BAVIN": [
                    "AUX series",
                    "HX series",
                ],
                "💰 Каталог с ценами": "💰 Наушники"
            },
            "Автомобильные зарядки": {
                "XUNDD": [
                    "XDCC series",
                    "XDCH series"
                ],
                "BAVIN": [
                    "PC-series",
                    "💰 Каталог с ценами"
                ]

            },
            "Держатели/подставки устройств": {
                "XUNDD": [
                    "A series",
                    "Mikko series",
                    "XDHO series"
                ],
                "BAVIN": [
                    "AP series",
                    "CA series",
                    "D-SPS series",
                    "DS series",
                    "PC series",
                    "PS series",
                    "💰 Каталог с ценами"
                ]

            },
            "Power banks и станции питания": {
                "XUNDD": [
                    "XDPB-series",
                    "XDCH-series"
                ],
                "BAVIN":[
                    "BST series",
                    "PC series",
                    "💰 Каталог с ценами"
                ]
            },
            "Блоки зарядки": {
                "XUNDD": [
                    "XDCH-series"
                ],
                "BAVIN": [
                    "PC series",
                    "💰 Каталог с ценами"
                ]
            },
            "Беспроводные зарядки": {
                "BAVIN": [
                    "PC017",
                    "PC832Y",
                    "PC832E",
                    "PC962",
                    "PC1033",
                    "PC1065",
                    "PC1069",
                    "PC1071",
                    "PC1129",
                    "PC2021",
                    "PC2032"
                ],
                "💰 Каталог с ценами": "💰 Беспроводные зарядки"
            },
            "Кабели": {
                "XUNDD": [
                    "XDDC-series"
                ],
                "BAVIN": [
                    "CB series",
                    "💰 Каталог с ценами"
                ]

            },
            "Умные часы": {
                "XUNDD": [
                    "SW002",
                    "SW001"
                ]
            },
            "Сетевые фильры": {
                "BAVIN": [
                    "PC512",
                    "PC588",
                    "PC589",
                    "PC803-EU",
                    "PC825",
                    "PC823Y-EU",
                    "PC830Y",
                    "PC830E",
                    "PC833Y",
                    "PC2026",
                    "PC2026Y",
                    "PC2026E",
                    "PC2080",
                    "PC2081",
                    "PC2082"
                ],
                "💰 Каталог с ценами": "💰 Сетевые фильтры"
            },
            "Переходники/хабы/кардридеры":{
                "BAVIN": [
                    "HUB series",
                    "OTG series"
                ],
                "💰 Каталог с ценами": "💰 Сетевые фильтры"
            }
            },
        "🚚 Вопросы по логистике": "Вопросы по логистике",
        "💰 Вопросы по оплате": "Вопросы по оплате",
        "👨🏻‍💻 Чат с администратором": "Чат с администратором",
        "ℹ️ О нас": "О нас"
    }

    }

# for i in structure_menu['Основное меню'].keys():
#     index = list(structure_menu['Основное меню'].keys()).index(i)
#     print(i)
