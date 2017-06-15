import binascii


def fingerprint(tokens, dict_limit=25, token_limit=None, debug=False):
    '''
    Paper:
    https://west.uni-koblenz.de/de/forschung/datensaetze/template-detection
    https://dl.acm.org/citation.cfm?id=2505673

    Adapted from https://github.com/vignesh-babu/Structural-Web-Document-Clustering/blob/master/src/rsl/webCluster/compression/lzw.java
    '''
    d = {}
    dict_entry_id = 1
    buff = tuple()
    prefix_id = 0
    output = []

    for cnt, tok in enumerate(tokens, start=1):
        if token_limit is not None and cnt > token_limit:
            break
        token = (tok,)
        buffer_token = buff + token
        if buffer_token in d:
            buff = buffer_token
        else:
            prefix_id = d.get(buff)
            if prefix_id is not None:
                output.append(prefix_id)
            else:
                output.append(0)
            d[buffer_token] = dict_entry_id
            dict_entry_id += 1
            buff = tuple()
        if dict_entry_id > dict_limit:
            break
    return output


def hexfp(fingerprint):
    return binascii.hexlify(bytes(fingerprint)).decode('ascii')


if __name__ == '__main__':
    test = '''html, body, p, b, b, p, p, strong, strong, p, p, big, big, p, p, em, em, p, p, i, i, p, p, small, small, p, p, sub, sub, sup, sup, p, body, html'''.split(', ')
    fp = fingerprint(test)
    assert fp == [0, 0, 0, 0, 4, 3, 0, 3, 0, 9, 3, 0, 8, 0, 8, 0, 8, 0, 0, 19, 2]
    assert hexfp(fp) == '000000000403000300090300080008000800001302'
