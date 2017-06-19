import binascii


def fingerprint(tokens, dict_limit=25, token_limit=None, debug=False):
    '''
    Paper: "Locality Sensitive Hashing for Scalable Structural
            Classification and Clustering of Web Documents"
    Hachenberg, Christian; Gottron, Thomas (2013)
    https://west.uni-koblenz.de/de/forschung/datensaetze/template-detection
    https://dl.acm.org/citation.cfm?id=2505673
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
    _bytes = bytearray(fingerprint)
    return binascii.hexlify(_bytes).decode('ascii')
