import sys

def naked(start, end, amount):
    # naked position: don't buy any stock
    if end > start:
        return amount*(end-start)
    else:
        return 0


def covered(start, end, amount, rate, time):
    return amount*(start-end) + amount*start*((1+rate)**time-1)

if __name__ == "__main__":
    pass

