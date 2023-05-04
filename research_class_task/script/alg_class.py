import statistics


def main():
    z_mean = 16.3
    z_disp = 7.5
    hard_mean = 26.0468
    hard_disp = 7.0228
    easy_mean = 6.899
    easy_disp = 1.8
    ans = [0, 1, 2]

    dtw = input()
    for symb in [' ', '[', ']']:
        dtw = dtw.replace(symb, '')
    dtw = [float(it) for it in dtw.split(',')]

    mean = statistics.fmean(dtw)
    disp = statistics.stdev(dtw)
    if mean < 6.234:
        print('2')  # easy class
        return
    if mean > 32:
        print('1')  # hard class
        return
    if mean < 14:
        ans.remove(1)
    else:
        ans.remove(2)
    proximity_z = abs(z_mean - mean) + abs(z_disp - disp)
    if 1 in ans:
        proximity_h = abs(hard_mean - mean) + abs(hard_disp - disp)
        if proximity_h < proximity_z:
            print("1")  # hard class
            return
    else:
        proximity_e = abs(easy_mean - mean) + abs(easy_disp - disp)
        if proximity_e < proximity_z:
            print("2")  # easy class
            return
    print("0")  # zpd class
    return


if __name__ == '__main__':
    main()


def main2(data):
    z_mean = 16.3
    z_disp = 7.5
    hard_mean = 26.0468
    hard_disp = 7.0228
    easy_mean = 6.899
    easy_disp = 1.8
    ans = [0, 1, 2]
    dtw = data
    for symb in [' ', '[', ']']:
        dtw = dtw.replace(symb, '')
    dtw = [float(it) for it in dtw.split(',')]

    mean = statistics.fmean(dtw)
    disp = statistics.stdev(dtw)
    if mean < 6.234:
        return 2
    if mean > 32:
        return 1
    if mean < 14:
        ans.remove(1)
    else:
        ans.remove(2)
    proximity_z = abs(z_mean - mean) + abs(z_disp - disp)
    if 1 in ans:
        proximity_h = abs(hard_mean - mean) + abs(hard_disp - disp)
        if proximity_h < proximity_z:
            return 1
    else:
        proximity_e = abs(easy_mean - mean) + abs(easy_disp - disp)
        if proximity_e < proximity_z:
            return 2
    return 0
