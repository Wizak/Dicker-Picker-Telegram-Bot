import random


def dick_grow():
    random_number = random.randint(1, 10)
    vector = random.randint(-1, 3)

    if vector > 0:
        vector = 1

    if random_number < 5:
        return random.randint(1, 10)*vector
    elif 5 < random_number < 10:
        return random.randint(11, 25)*vector
    else:
        return random.randint(26, 50)*vector


if __name__ == '__main__':
    print(dick_grow())
