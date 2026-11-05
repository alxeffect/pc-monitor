import json

from agent.collector import collect_stats


def main():
    stats = collect_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()