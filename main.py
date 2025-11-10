from tools.generate_urls_to_parse import runner

league_map = {
    "1": "_superleague",
    "2": "nhl",
    "3": "_highleague",
    "4": "mhl",
    "5": "all",
    "khl": "_superleague",
    "nhl": "nhl",
    "vhl": "_highleague",
    "mhl": "mhl",
    "all": "all",
}


def main():
    while True:
        league = input(
            "Введите лигу для парсинга \n1)'khl\n2)'nhl'\n3)'vhl'\n4)'mhl'\n5)'all'\n"
        ).strip()
        if league in ["khl", "nhl", "vhl", "mhl", "all"] or league in [
            "1",
            "2",
            "3",
            "4",
            "5",
        ]:
            league = league_map.get(league, league)
            break
        else:
            print("Лига не может быть пустой. Пожалуйста, введите корректное значение.")
    while True:
        days = input("Введите количество дней для парсинга (например, 7): ").strip()
        if days.isdigit() and int(days) > 0:
            days = int(days)
            break
        else:
            print("Пожалуйста, введите корректное положительное число для дней.")
    runner(days=days, league=league)


if __name__ == "__main__":
    main()
