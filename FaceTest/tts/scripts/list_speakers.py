"""List the XTTS-v2 built-in speakers."""
import common


def main():
    model = common.load_model()
    names = common.builtin_speakers(model)
    print(f"{len(names)} built-in speakers:")
    for n in names:
        print(n)


if __name__ == "__main__":
    main()
