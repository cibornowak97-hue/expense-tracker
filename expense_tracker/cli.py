import argparse
import csv
import sys

from .database import ExpenseDB


def money(cents):
    return f"{cents / 100:,.2f}"


def build_parser():
    parser = argparse.ArgumentParser(
        prog="expense_tracker", description="Track your spending from the terminal."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add an expense")
    add.add_argument("amount", type=float)
    add.add_argument("category")
    add.add_argument("-n", "--note", default="")
    add.add_argument("-d", "--date", help="YYYY-MM-DD (default: today)")

    ls = sub.add_parser("list", help="list expenses")
    ls.add_argument("-c", "--category")
    ls.add_argument("-m", "--month", help="YYYY-MM")

    rm = sub.add_parser("delete", help="delete an expense by id")
    rm.add_argument("id", type=int)

    sm = sub.add_parser("summary", help="total per category")
    sm.add_argument("-m", "--month", help="YYYY-MM")
    ex = sub.add_parser("export", help="export all expenses to a CSV file")
    ex.add_argument("filename")
    return parser


def run(args, db):
    if args.command == "add":
        new_id = db.add(args.amount, args.category, args.note, args.date)
        print(f"Added expense #{new_id}: {args.amount:.2f} on {args.category}")

    elif args.command == "list":
        rows = db.list(args.category, args.month)
        if not rows:
            print("No expenses found.")
            return
        print(f"{'ID':<5}{'Date':<12}{'Category':<14}{'Amount':>10}  Note")
        for r in rows:
            print(f"{r['id']:<5}{r['spent_on']:<12}{r['category']:<14}"
                  f"{money(r['amount_cents']):>10}  {r['note']}")

    elif args.command == "delete":
        if db.delete(args.id):
            print(f"Deleted expense #{args.id}")
        else:
            print(f"No expense with id {args.id}")

    elif args.command == "summary":
        rows = db.summary(args.month)
        if not rows:
            print("No expenses found.")
            return
        for category, total in rows:
            print(f"{category:<14}{money(total):>12}")
        print("-" * 26)
        print(f"{'TOTAL':<14}{money(sum(t for _, t in rows)):>12}")
    elif args.command == "export":
        rows = db.list()
        with open(args.filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "date", "category", "amount", "note"])
            for r in rows:
                writer.writerow([r["id"], r["spent_on"], r["category"],
                                 f"{r['amount_cents'] / 100:.2f}", r["note"]])
        print(f"Exported {len(rows)} expenses to {args.filename}")


def main(argv=None):
    args = build_parser().parse_args(argv)
    db = ExpenseDB()
    try:
        run(args, db)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()