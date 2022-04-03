import subprocess as sub


def ping():
    command = ['ping', '8.8.8.8']
    response = sub.call(command)
    if response == 0:
        return 1
    else:
        return 0


if __name__ == '__main__':
    ping()


