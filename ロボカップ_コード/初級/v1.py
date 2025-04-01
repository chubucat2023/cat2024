import tkinter as tk
import re

forward_image = None
right_image = None
left_image = None


# This function generates and prints the custom code based on the user input
def generate_custom_code(commands):
    base_code = """
import DF_15RSMG
import time

def forward(t):
    DF_15RSMG.forward()
    time.sleep(t)
    DF_15RSMG.stop()

def turn_R(t):
    DF_15RSMG.turn_R()
    time.sleep(t)
    DF_15RSMG.stop()

def turn_L(t):
    DF_15RSMG.turn_L()
    time.sleep(t)
    DF_15RSMG.stop()

def main():
"""
    for command, delay in commands:
        base_code += f"    {command}({delay})\n"

    base_code += """
if __name__ == '__main__':
    DF_15RSMG.init_servo()
    main()
"""
    print(base_code)


# GUI の設定
def create_gui():
    global forward_image, right_image, left_image

    window = tk.Tk()
    window.title("Control DF_15RSMG Robot")

    # フォントの設定
    custom_font = ("Helvetica", 20, "bold")
    label = tk.Label(window, text="しょきゅう", font=custom_font)
    label.pack(pady=10)

    # 画像のロード
    forward_image = tk.PhotoImage(file="zensin.png")
    right_image = tk.PhotoImage(file="migi.png")
    left_image = tk.PhotoImage(file="hidari.png")

    if forward_image and right_image and left_image:
        print("Images loaded successfully")
    else:
        print("Error: Failed to load images")

    # コマンドのリストを格納する配列
    commands = []

    # ユーザー入力用のフレーム
    frame = tk.Frame(window)
    frame.pack(pady=10)

    # 操作部分のフレーム
    operation_frame = tk.Frame(frame, borderwidth=2, relief="solid")  # 枠線を追加
    operation_frame.grid(row=1, column=0, pady=(10, 0), padx=10)

    button_label = tk.Label(operation_frame, text="2.ほうこう", font=custom_font)
    button_label.grid(row=2, column=0, pady=(10, 0))

    action_label = tk.Label(operation_frame, text="")
    action_label.grid(row=5, column=0, columnspan=5)

    def add_command(action):
        delay = delay_entry.get()
        if action and delay:
            commands.append((action, delay))
            commands_listbox.insert(tk.END, f"{action}({delay})")
            delay_entry.delete(0, tk.END)

    # コマンドを削除する関数
    def remove_command():
        selected_indices = list(commands_listbox.curselection())
        if not selected_indices:
            return
        for index in reversed(selected_indices):
            del commands[index]
            commands_listbox.delete(index)

    # コマンド削除ボタン
    remove_button = tk.Button(window, text="選択したコマンドを削除", font=custom_font,
                              command=remove_command)
    remove_button.pack(side=tk.BOTTOM, pady=10)

    def validate_delay_input(delay):
        if delay == "":
            return True

        if re.match(r'^[0-9]+$', delay):
            return True
        else:
            return False

    def on_delay_entry_keypress(event):
        char = event.char
        if char and char.isdigit() and len(delay_entry.get()) < 2:
            return
        elif char and char == '\x08':  # バックスペース
            return
        else:
            return "break"

    def button_pressed(button_name):
        if button_name == "forward":
            action_label.config(text="↑　にすすむよ.", font=custom_font)  # 前進の表示を日本語に変更
        elif button_name == "turn_R":
            action_label.config(text="→　にまがるよ.", font=custom_font)  # 右の表示を日本語に変更
        elif button_name == "turn_L":
            action_label.config(text="← にまがるよ.", font=custom_font)  # 左の表示を日本語に変更

    column_width = 3
    operation_frame.columnconfigure(1, weight=1)

    forward_button = tk.Button(operation_frame, image=forward_image,
                               command=lambda: (add_command("forward"), button_pressed("forward")))
    forward_button.grid(row=4, column=0, pady=10, padx=(10, 0), columnspan=column_width)
    forward_label = tk.Label(operation_frame, text="まえ", font=custom_font)
    forward_label.grid(row=3, column=0, padx=(10, 0), columnspan=column_width)

    right_button = tk.Button(operation_frame, image=right_image,
                             command=lambda: (add_command("turn_R"), button_pressed("turn_R")))
    right_button.grid(row=4, column=1, padx=(100, 0), columnspan=column_width)
    right_label = tk.Label(operation_frame, text="みぎ", font=custom_font)
    right_label.grid(row=3, column=1, padx=(100, 0), columnspan=column_width)

    left_button = tk.Button(operation_frame, image=left_image,
                            command=lambda: (add_command("turn_L"), button_pressed("turn_L")))
    left_button.grid(row=4, column=0, padx=5)
    left_label = tk.Label(operation_frame, text="ひだり", font=custom_font)
    left_label.grid(row=3, column=0, padx=5)

    tk.Label(operation_frame, text="1.じかん(びょう)", font=custom_font).grid(row=0, column=0, pady=(0, 10))
    delay_entry = tk.Entry(operation_frame, font=custom_font, validate="key",
                           validatecommand=(window.register(validate_delay_input), "%P"))
    delay_entry.bind("<Key>", on_delay_entry_keypress)
    delay_entry.grid(row=0, column=1, columnspan=1)

    # Python スクリプトを生成するボタン
    generate_button = tk.Button(window, text="じゅんびかんりょう！", font=custom_font, fg="red",
                                command=lambda: generate_custom_code(commands))
    generate_button.pack(side=tk.BOTTOM, pady=10)

    remove_button.pack(after=generate_button)

    # 現在のコマンドリストを表示するリストボックス
    commands_listbox = tk.Listbox(window, height=5, width=30, font=custom_font)
    commands_listbox.pack(pady=5)

    window.mainloop()


# GUI を実行するメイン関数
if __name__ == "__main__":
    create_gui()