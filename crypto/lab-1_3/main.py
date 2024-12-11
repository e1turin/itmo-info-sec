#!/usr/bin/env python

from argparse import ArgumentParser
from functools import reduce
from typing import Literal


type Mode = Literal["encrypt", "decrypt"]


class LSR:
    def __init__(self, size: int, init_state: int, fb_ids: list[int]):
        self.size: int = size
        self.state: int = init_state & ((1 << size) - 1)
        self.fb_ids: list[int] = fb_ids
        for i in fb_ids:
            assert (i < size), f"bit {i} must be in reg with size {size}"

    def shift(self) -> int:
        shift_bit = self.state & 1
        feedback_bit = reduce(
            lambda a, b: a ^ b, [(self.state & (1 << i)) >> i for i in self.fb_ids], 0
        )
        self.state = (feedback_bit << (self.size - 1)) | (self.state >> 1) & ((1 << self.size) - 1)
        return shift_bit

def setup(seed: int,debug=False):
    lsr0 = LSR(78, seed, [77, 6, 5, 2, 0])
    lsr1 = LSR(80, seed, [79, 4, 3, 2, 0])
    lsrc = LSR(78, seed, [75, 6, 3, 1, 0])

    def y_gen() -> int:
        cbit = lsrc.shift()
        match cbit:
            case 0:
                sbit = lsr0.shift()
            case 1:
                sbit = lsr1.shift()
            case _:
                raise ValueError(f"control bit out of bounds: {cbit}")
        if debug:
            print(f"cbit={cbit} sbit={sbit} lsr0={lsr0.state} lsr1={lsr1.state} lsrc={lsrc.state}")
        return sbit

    def y_byte_gen() -> int:
        y_byte = 0
        for i in range(8):
            y_byte |= y_gen() << i
        return y_byte
    
    return (y_gen, y_byte_gen)


def process_file(
    seed: int,
    mode: Mode,
    input_file: str,
    output_file: str,
):
    with open(input_file, "rb") as f:
        data = bytearray(f.read())

    _, y_byte_gen = setup(seed, debug=False)
    result = bytearray()

    match mode:
        case "encrypt": 
            for b in data:
                y = y_byte_gen()
                nb = b ^ y
                result.append(nb)
        case "decrypt": 
            for b in data:
                y = y_byte_gen()
                nb = b ^ y
                result.append(nb)

    with open(output_file, "wb") as f:
        f.write(result)


def main():
    parser = ArgumentParser(description="")
    parser.add_argument("--seed", "-s", required=False, 
                        help="Начальное состояние для генератора ключей")
    parser.add_argument("--mode", "-m", choices=["encrypt", "decrypt"], 
                        required=True, help="Режим работы",)
    parser.add_argument("--input", "-i", required=True, help="Входной файл")
    parser.add_argument("--output", "-o", required=True, help="Выходной файл")
    args = parser.parse_args()
    
    seed: int = args.seed or 0xABCDEF123456790ABCDE
    mode: Mode = args.mode

    ifile: str = args.input
    ofile: str = args.output
    process_file(seed, mode, ifile, ofile)

if __name__ == "__main__":
    main()
