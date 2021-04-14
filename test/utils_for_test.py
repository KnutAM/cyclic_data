import numpy as np


def get_sawtooth(time, cycle_time, amp):
    data = np.zeros(time.size)
    seg_sign = 1
    for t0, t1 in zip(cycle_time[:-1], cycle_time[1:]):
        i0 = np.argmax(time > t0)
        i1 = np.argmax(time > t1)
        i1 = len(data) if i1 == 0 else i1

        if i0 > 1:
            data[i0:i1] = -seg_sign*amp + 2*seg_sign*amp*(time[i0:i1]-t0) / (t1 - t0)
        else:
            data[i0:i1] = seg_sign * amp * (time[i0:i1] - t0) / (t1 - t0)

        seg_sign *= -1

    return data
