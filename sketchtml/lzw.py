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


def compress(uncompressed):
    """Compress a sequence of tuples to a list of output symbols."""

    metatags = [t.strip('< >') for t in '''
        <html>
        <base>
        <head>
        <link>
        <meta>
        <style>
        <title>'''.splitlines()]
    # Build the dictionary.
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Inline_elements
    inline_tags = [t.strip('<>') for t in '''
        <a>
        <b>
        <big>
        <i>
        <small>
        <tt>
        <abbr>
        <acronym>
        <cite>
        <code>
        <em>
        <strong>
        <time>
        <br>
        <img>
        <map>
        <object>
        <q>
        <script>
        <span>
        <sub>
        <sup>
        <button>
        <input>
        <label>
        <select>
        <textarea>
        <dfn>
        <kbd>
        <samp>
        <var>
        <bdo>'''.strip().splitlines()]

    # https://developer.mozilla.org/en-US/docs/Web/HTML/Block-level_elements
    block_level_tags = [t.strip('<>') for t in '''
        <address>
        <article>
        <aside>
        <blockquote>
        <canvas>
        <dd>
        <div>
        <dl>
        <dt>
        <fieldset>
        <figcaption>
        <figure>
        <footer>
        <form>
        <h1>
        <h2>
        <h3>
        <h4>
        <h5>
        <h6>
        <header>
        <hgroup>
        <hr>
        <li>
        <main>
        <nav>
        <noscript>
        <ol>
        <output>
        <p>
        <pre>
        <section>
        <table>
        <tfoot>
        <ul>
        <video>'''.strip().splitlines()]
    tags = metatags + block_level_tags + inline_tags + ['other']
    closingtags = ['!'+t for t in tags]
    dictionary = {(t,): i for i, t in enumerate(tags+closingtags, start=1)}
    dict_size = len(dictionary)

    w = tuple()
    result = []
    for c in uncompressed:
        c = tuple((c,))
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            prefix_idx = dictionary.get(w)
            if prefix_idx is not None:
                result.append(prefix_idx)
            else:
                result.append(
                    dictionary.get(('other',))
                )
            dictionary[wc] = dict_size
            dict_size += 1
            w = c
            if dict_size >= 256:
                break
    # Output the code for w.
    if w:
        result.append(dictionary.get(w, dictionary.get(('other',))))
    return result


def hexfp(fingerprint):
    _bytes = bytearray(fingerprint)
    return binascii.hexlify(_bytes).decode('ascii')
