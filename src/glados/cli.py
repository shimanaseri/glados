from glados.llm import stream_reply


def main() -> None:
    history = []
    print("GLaDOS is online. Type 'quit' to exit, 'reset' to clear history.")
    print("You should be fast cause she has zero patience\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("GLaDOS: Leaving so soon? How predictable.")
            break
        if user_input.lower() == "reset":
            history = []
            print("GLaDOS: Memory wiped. Not that you were memorable.\n")
            continue

        print("GLaDOS: ", end="", flush=True)
        full_reply = ""
        for chunk in stream_reply(history, user_input):
            print(chunk, end="", flush=True)
            full_reply += chunk
        print("\n")

        history.append(("user", user_input))
        history.append(("assistant", full_reply))


if __name__ == "__main__":
    main()