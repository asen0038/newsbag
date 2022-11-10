import statistics


def average(nums):
    n = len(nums)
    add = 0
    for i in nums:
        add = add + i

    avg = add/n
    return avg


def threshold(nums):
    if len(nums) == 1:
        return 0.5
    else:
        avg = average(nums)
        sd = statistics.stdev(nums)
        temp = 0.75 * sd
        value = avg + temp
        return value
