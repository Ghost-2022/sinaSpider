# -*- coding: utf-8 -*-
"""
    @Date:  2022/3/3 17:01
    @Author: Ghost
    @Desc: 
"""
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


# 10进制转为62进制
def base62_encode(num, alphabet=ALPHABET):
    """Encode a number in Base X
    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


# 62进制转为10进制
def base62_decode(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number
    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0
    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1
    return num


# article_id转换为mid
def id2mid(article_id):
    article_id = str(article_id)[::-1]
    size = int(len(article_id) / 7) if len(article_id) % 7 == 0 else int(len(article_id) / 7 + 1)
    result = []
    for i in range(size):
        s = article_id[i * 7: (i + 1) * 7][::-1]
        s = base62_encode(int(s))
        s_len = len(s)
        if i < size - 1 and len(s) < 4:
            s = '0' * (4 - s_len) + s
        result.append(s)
    result.reverse()
    return ''.join(result)


# id转换为mid
def mid2id(mid):
    mid = str(mid)[::-1]
    size = int(len(mid) / 4) if len(mid) % 4 == 0 else int(len(mid) / 4 + 1)
    result = []
    for i in range(size):
        s = mid[i * 4: (i + 1) * 4][::-1]
        s = str(base62_decode(str(s)))
        s_len = len(s)
        if i < size - 1 and s_len < 7:
            s = (7 - s_len) * '0' + s
        result.append(s)
    result.reverse()
    return ''.join(result)


if __name__ == '__main__':
    print ('mdi2id: ' + id2mid('4723198292132060'))