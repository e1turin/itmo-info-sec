#!/usr/bin/env python

# 4. Реализовать в программе шифрование и дешифрацию файла с использованием
#    квадрата Полибия, обеспечив его случайное заполнение.

import random
import string
from typing import Literal
from sys import argv

type PolybiySquare = dict[str, tuple[int, int]]
type Mode = Literal["encrypt", "decrypt"]


def generate_polibiy_square() -> PolybiySquare:
    alphabet = string.ascii_uppercase.replace("J", "")
    assert len(alphabet) == 25, "alphabet length shoud be square number"

    permutation = random.sample(alphabet, len(alphabet))
    square = {permutation[i]: (i // 5 + 1, i % 5 + 1) for i in range(len(permutation))}
    return square


def encrypt(text: str, square: PolybiySquare) -> str:
    text = text.upper().replace("J", "I")
    encrypted_text = []
    for char in text:
        if char in square:
            row, col = square[char]
            encrypted_text.append(f"{row}{col}")
        else:
            encrypted_text.append("??")
    return "".join(encrypted_text)


def decrypt(encrypted_text: str, square: PolybiySquare) -> str:
    reverse_square = {v: k for k, v in square.items()}
    decrypted_text = []
    for i in range(0, len(encrypted_text), 2):
        try:
            row, col = int(encrypted_text[i]), int(encrypted_text[i + 1])
            decrypted_text.append(reverse_square[(row, col)])
        except ValueError:
            decrypted_text.append("?")
    return "".join(decrypted_text)


def process_file(
    input_filename, output_filename, square: PolybiySquare, mode: Mode = "encrypt"
):
    with open(input_filename, "r") as file:
        text = file.read()

    if mode == "encrypt":
        result = encrypt(text, square)
    elif mode == "decrypt":
        result = decrypt(text, square)

    with open(output_filename, "w") as file:
        file.write(result)


def main(
    input_filename: str, output_filename: str, square_data_filename: str, mode: Mode
):
    if mode == "encrypt":
        square = generate_polibiy_square()
        with open(square_data_filename, "w") as file:
            data = "\n".join([f"{k}:{square[k][0]},{square[k][1]}" for k in square])
            file.write(data)
    else:
        with open(square_data_filename, "r") as file:
            square = {}
            for row in file.readlines():
                [char, pos] = row.split(":")
                [i, j] = map(int, pos.split(","))
                square[char] = (i, j)

    process_file(input_filename, output_filename, square, mode=mode)


if __name__ == "__main__":
    if argv[1] == "encrypt":
        mode = "encrypt"
    elif argv[1] == "decrypt":
        mode = "decrypt"
    else:
        raise KeyError("first argument specify wether 'encrypt' or 'decrypt' text")

    main(
        input_filename=argv[2],
        output_filename=argv[3],
        square_data_filename=argv[4],
        mode=mode,
    )
