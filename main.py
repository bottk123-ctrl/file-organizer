import argparse
import json
import os

import config
from core.history import clear_history, load_history, save_history
from core.organizer import SortResult, apply_plan, plan_sort, undo_sort


def build_parser():
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Сортировка файлов по категориям. Без аргументов открывается окно приложения.",
    )
    parser.add_argument("-f", "--folder", help="папка для сортировки")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="показать план перемещений, ничего не меняя",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="отменить последнюю сортировку",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="не спрашивать подтверждение перед перемещением",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="вывести результат в JSON (удобно для скриптов)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{config.APP_NAME} {config.VERSION}",
    )
    return parser


def _moves_payload(moves):
    return [
        {
            "source": source,
            "destination": destination,
            "category": os.path.basename(os.path.dirname(destination)),
        }
        for source, destination in moves
    ]


def _plan_payload(plan, folder, mode):
    return {
        "mode": mode,
        "folder": folder,
        "planned": len(plan.moves),
        "skipped": plan.skipped,
        "ignored": plan.ignored,
        "moves": _moves_payload(plan.moves),
        "errors": plan.errors,
    }


def _print_json(payload):
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _print_plan(plan):
    if not plan.moves:
        print("Нет файлов для перемещения.")
    for source, destination in plan.moves:
        category = os.path.basename(os.path.dirname(destination))
        print(f"{os.path.basename(source)}  ->  {category}")
    print()
    print(plan.summary())


def _run_undo(args):
    pairs = load_history()
    if not pairs:
        message = "Нет сохранённой сортировки для отмены."
        if args.json:
            _print_json({"mode": "undo", "restored": 0, "remaining": 0, "errors": [message]})
        else:
            print(message)
        return 1

    result = SortResult.from_paths(pairs)
    undo = undo_sort(result)
    if result.moved_paths:
        save_history(result.moved_paths)
    else:
        clear_history()

    if args.json:
        _print_json(
            {
                "mode": "undo",
                "restored": undo.moved,
                "remaining": len(result.moved_paths),
                "errors": undo.errors,
            }
        )
    else:
        print(undo.summary())
    return 0 if undo.moved else 1


def run_cli(args):
    if args.undo:
        return _run_undo(args)

    if not args.folder:
        print("Укажите папку через --folder.")
        return 1

    folder = args.folder
    if not os.path.isdir(folder):
        print(f"Папка не найдена: {folder}")
        return 1

    plan = plan_sort(folder)
    if plan.errors:
        if args.json:
            _print_json(_plan_payload(plan, folder, "dry-run" if args.dry_run else "sort"))
        else:
            print(plan.summary())
        return 1

    if args.dry_run:
        if args.json:
            _print_json(_plan_payload(plan, folder, "dry-run"))
        else:
            _print_plan(plan)
        return 0

    if args.json and not args.yes:
        print("Для --json при реальной сортировке добавьте --yes.")
        return 1

    if not args.yes:
        answer = input(f"Переместить файлов: {len(plan.moves)}? [y/N] ")
        if answer.strip().lower() not in {"y", "yes", "д", "да"}:
            print("Отменено.")
            return 0

    result = apply_plan(plan)
    if result.moved_paths:
        save_history(result.moved_paths)

    if args.json:
        _print_json(
            {
                "mode": "sort",
                "folder": folder,
                "moved": result.moved,
                "skipped": result.skipped,
                "ignored": result.ignored,
                "moves": _moves_payload(result.moved_paths),
                "errors": result.errors,
            }
        )
    else:
        print(result.summary())
    return 0 if not result.errors else 1


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.folder or args.undo:
        return run_cli(args)

    # Окно импортируется лениво, чтобы CLI работал и без графической сессии.
    from ui.app import App

    App().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
