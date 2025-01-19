from sympy import mod_inverse
from random import randint

type FP = tuple[int, int]
type O = tuple[None, None]
type Point = FP | O  # finite or infinity


class ElipticCurveGroup:
    def __init__(self, mod: int, a: int, b: int):
        self.a: int = a
        self.b: int = b
        self.mod: int = mod

    def sum(self, P: Point, Q: Point) -> Point:
        if P == (None, None):
            return Q
        if Q == (None, None):
            return P

        x1, y1 = P
        x2, y2 = Q

        mod = self.mod
        a = self.a

        if x1 % mod == x2 % mod and y1 % mod == -y2 % mod:
            return (None, None)

        if P == Q:
            s = (3 * x1**2 + a) * mod_inverse(2 * y1, mod) % mod
        else:
            s = (y2 - y1) * mod_inverse(x2 - x1, mod) % mod

        x3 = (s**2 - x1 - x2) % mod
        y3 = (s * (x1 - x3) - y1) % mod

        return (x3, y3)

    def mul(self, k: int, P: Point) -> Point:
        Q = (None, None)
        N = P

        while k:
            if k & 1:
                Q = self.sum(Q, N)
            N = self.sum(N, N)
            k >>= 1

        return Q

    def encrypt(
        self, msg: Point, G: Point, pub_key: Point, rand_k: int
    ) -> tuple[Point, Point]:
        C1: Point = self.mul(rand_k, G)
        C2: Point = self.sum(msg, self.mul(rand_k, pub_key))
        return C1, C2

    def decrypt(self, C1, C2, priv_key: int) -> Point:
        nkG: Point = self.mul(priv_key, C1)
        neg_nkG: Point = (nkG[0], -nkG[1] % self.mod)
        msg: Point = self.sum(C2, neg_nkG)
        return msg


def read_code_table(name) -> tuple[dict, dict]:
    encoding = {}
    with open(name, "r", encoding="utf-8") as f:
        for line in f.readlines():
            if line.strip() == "":
                continue
            i, char, *point = line.split()
            point = tuple(map(int, "".join(point).strip("()").split(",")))
            if char == "пробел":
                char = " "
            encoding[char] = {"id": int(i), "code": point}

    decoding = {v["code"]: k for k, v in encoding.items()}
    return encoding, decoding


def write_code_table(encoding):
    with open("code_table.txt", "w", encoding="utf-8") as f:
        for k, v in sorted(encoding.items(), key=lambda e: e[1]["id"]):
            if k == " ":
                k = "пробел"
            f.write(f"{v['id']} {k} {v['code']}\n")


def hack_ecc(ecg: ElipticCurveGroup, G: Point, pub_key: Point) -> int:
    for k in range(ecg.mod):
        if pub_key == ecg.mul(k, G):
            return k


def gen_rand():
    nums = [9, 10, 13, 2, 2, 12, 12, 5, 7]
    for r in nums:
        yield r

    print("[random sequence end]")

    while True:
        yield randint(1, 100)


def main():
    ecg = ElipticCurveGroup(751, a=-1, b=1)
    G = (0, 1)
    pub_key = (725, 195)  # or (406,397) in example
    text = "латентный"

    secret = hack_ecc(ecg, G, pub_key)  # or 45 in example

    encoding, decoding = read_code_table("code_table.txt")
    print("Секретное сообщение:", text)

    encoded_text = [encoding[c]["code"] for c in text]
    print("Закодированное сообщение:", encoded_text)

    cipher = [ecg.encrypt(p, G, pub_key, k) for p, k in zip(encoded_text, gen_rand())]
    print("Зашифрованное сообщение:", cipher)

    decrypted_text = [ecg.decrypt(C1, C2, secret) for C1, C2 in cipher]
    print("Расшифрованное сообщение:", decrypted_text)

    decoded_text = [decoding[p] for p in decrypted_text]
    print("Раскодированное сообщение:", "".join(decoded_text))


if __name__ == "__main__":
    main()
