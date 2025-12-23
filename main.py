import os
import winsound

def play_music(folder, song_name):
    file_path = os.path.join(folder, song_name)

    if not os.path.exists(file_path):
        print("File not found")
        return

    print(f"\nNow playing: {song_name}")
    print("Commands: [S]top  [Q]uit")

    # ▶️ PLAY ASYNC (NON-BLOCKING)
    winsound.PlaySound(
        file_path,
        winsound.SND_FILENAME | winsound.SND_ASYNC
    )

    while True:
        command = input("> ").upper()

        if command == "S":
            winsound.PlaySound(None, winsound.SND_PURGE)
            print("Stopped")
            return

        elif command == "Q":
            winsound.PlaySound(None, winsound.SND_PURGE)
            print("Exit player")
            exit()

        else:
            print("Invalid command")


def main():
    folder = "music"

    if not os.path.isdir(folder):
        print(f"Folder '{folder}' not found")
        return

    songs = [f for f in os.listdir(folder) if f.endswith(".wav")]

    if not songs:
        print("No WAV files found")
        return

    while True:
        print("\n********** WAV PLAYER **********")
        for i, song in enumerate(songs, start=1):
            print(f"{i}. {song}")

        choice = input("\nEnter song number or Q to quit: ")

        if choice.upper() == "Q":
            print("Byeeeeee 👋")
            break

        if not choice.isdigit():
            print("Enter a valid number")
            continue

        index = int(choice) - 1

        if 0 <= index < len(songs):
            play_music(folder, songs[index])
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
