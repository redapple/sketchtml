from collections import OrderedDict, Counter, defaultdict
from functools import partial
from itertools import zip_longest, combinations
import re

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import coherence
from sklearn.cluster import SpectralClustering

from sketchtml.tree import TreeHelper


class TagPathSimilarity(object):

    def __init__(self, tagpaths):
        self.tagpaths = tagpaths
        self.len_tagpaths = len(tagpaths)
        self.signals = self.get_signals()

    def get_signals(self):
        signals = OrderedDict()
        for i, t in enumerate(self.tagpaths, start=0):
            if t not in signals:
                signals[t] = []
            signals[t].append(i)
        return signals

    def segments(self, positions):
        for a, b in zip_longest(positions, positions[1:],
                                fillvalue=self.len_tagpaths):
            if a is not None and b is not None and (b-a) > 1:
                yield (a, b)

    def overlap(self, positions1, positions2, debug=False):
        min1, max1 = min(positions1), max(positions1)
        min2, max2 = min(positions2), max(positions2)
        if debug:
            print('Signal 1 [{} - {}]'.format(min1, max1))
            print('Signal 2 [{} - {}]'.format(min2, max2))

        if max1 < min2:
            return 0
        elif max2 < min1:
            return 0
        elif min2 < max1:
            return (min(max1, max2) - min2) / min((max1 - min1), (max2 - min2))
        elif min1 < max2:
            return (min(max1, max2) - min1) / min((max1 - min1), (max2 - min2))

    def occurrence_counts(self, signal1, signal2):
        return [len([p for p in signal1 if (s[0] < p <= s[1])])
                for s in self.segments(signal2)]

    def interleaving(self, positions1, positions2, debug=False):
        D_1_2 = self.occurrence_counts(positions1, positions2)
        D_2_1 = self.occurrence_counts(positions2, positions1)
        if debug:
            print(D_1_2, D_2_1)
        variances = [np.var(occ) if occ else 0
                     for occ in [D_1_2, D_2_1]]
        means = [np.mean(occ) if occ else 0
                 for occ in [D_1_2, D_2_1]]
        return max(*variances)

    def make_vector(self, positions):
        vector = [0] * self.len_tagpaths
        for p in positions:
            vector[p] = 1
        return vector

    @staticmethod
    def gravity_center(positions):
        return np.mean(positions)

    def plot_similarity(self, positions1, positions2):
        v1 = self.make_vector(positions1)
        v2 = self.make_vector(positions2)
        plt.plot(*coherence(v1, v2))

    def plot_signals(self, size=100):
        p = np.zeros((self.len_tagpaths, len(self.signals)))
        for tagid, (path, positions) in enumerate(self.signals.items()):
            for position in positions:
                p[(position, tagid)] = 1
        plt.figure(figsize = (size, size))
        plt.imshow(p, cmap='gray');

    def measures(self, signal1, signal2, debug=False):
        center_diff = abs(self.gravity_center(signal1) - self.gravity_center(signal2))
        interleaving_measure = self.interleaving(signal1, signal2)
        overlap = self.overlap(signal1, signal2, debug=debug)

        return center_diff, interleaving_measure, overlap

    def similarity(self, tagpath1, tagpath2, epsilon=10, plot=False, debug=False):
        signal1 = self.signals[tagpath1]
        signal2 = self.signals[tagpath2]

        center_diff, interleaving_measure, overlap = self.measures(
            signal1, signal2, debug=debug)

        if plot:
            self.plot_similarity(signal1, signal2)

        if overlap == 0:
            return 0
        return epsilon / (center_diff * interleaving_measure + epsilon)


class TagPathClustering(object):

    def __init__(self, htmltext,
                 with_classes=True,
                 with_id=True,
                 with_attr_names=False,
                 strip_digits=False,
                 ignore_classes=None,
                 text_only=False):

        self.htmltext = htmltext
        self.with_classes=with_classes
        self.with_id=with_id
        self.with_attr_names=with_attr_names
        self.strip_digits = strip_digits
        self.ignore_classes = ignore_classes
        self.text_only = text_only

        self._node_repr = partial(TagPathClustering.node_repr,
                             with_classes=self.with_classes,
                             with_id=self.with_id,
                             with_attr_names=self.with_attr_names,
                             strip_digits=self.strip_digits,
                             ignore_classes=self.ignore_classes)

    def clusters(self, min_repeat=2, max_repeat=None):
        self._build_tagpaths()
        self.simhelper = TagPathSimilarity(self.tagpaths)

        repeating_tagpaths = [
            tp for tp, cnt in Counter(self.tagpaths).most_common()
            if cnt >= min_repeat and (max_repeat is None or cnt <= max_repeat)
        ]
        return self._spectral_clustering(repeating_tagpaths)

    def _affinity_matrix(self, tagpaths):
        l = len(tagpaths)
        matrix = np.zeros((l, l))
        for a, b in combinations(tagpaths, 2):
            ia, ib = tagpaths.index(a), tagpaths.index(b)
            matrix[ia, ib] = self.simhelper.similarity(a, b, epsilon=5)
            matrix[ib, ia] = matrix[ia, ib]
            matrix[ia, ia] = 1
            matrix[ib, ib] = 1
        matrix = np.exp(matrix / matrix.std())
        return matrix

    def _spectral_clustering(self, tagpaths):
        matrix = self._affinity_matrix(tagpaths)

        clustering = SpectralClustering(affinity='precomputed')
        pred = clustering.fit_predict(matrix)

        clusters = defaultdict(list)
        for i, p in enumerate(pred):
            clusters[p].append(tagpaths[i])
        for p in clusters.keys():
            clusters[p] = sorted(clusters[p])

        self.affinity_matrix = matrix

        return clusters

    def plot_affinity_matrix(self):
        plt.matshow(self.affinity_matrix)

    @staticmethod
    def node_repr(node, with_classes=False, with_id=False, with_attr_names=False, strip_digits=False, ignore_classes=None):
        classes = None
        ids = None
        attr_names = None
        attribs = node.attribs
        if with_classes:
            classes = attribs.get('class', '').split()
            if ignore_classes:
                classes = [cl for cl in classes
                           if cl not in ignore_classes]

        if with_id:
            ids = attribs.get('id')
        if with_attr_names:
            attr_names = sorted(set(attribs) - {'id', 'class'})
        output = node.tag

        if ids:
            if strip_digits and re.sub(r'\d+', '', ids) != ids:
                ids = re.sub(r'\d+', '', ids)
                output += '#*{}'.format(ids)
            else:
                output += '#'+ids

        if classes:
            if strip_digits and [re.sub(r'\d+', '', cl) for cl in classes] != classes:
                classes = set(re.sub(r'\d+', '', cl) for cl in classes)
                output += ''.join('.*{}'.format(cls) for cls in sorted(classes))
            else:
                output += ''.join('.{}'.format(cls) for cls in sorted(classes))

        if attr_names:
            output += ''.join('[{}]'.format(a) for a in attr_names)
        return output

    def _build_tagpaths(self):
        self.treehelper = TreeHelper(textonly=self.text_only)
        self.treehelper.tagpath_join = '/'
        self.tagpaths = []
        self.tagpath_nodes = defaultdict(list)
        for nodes in self.treehelper.iter_nodepaths(self.htmltext, keep_element_refs=True):
            if nodes[-1].tag in ('script', 'style'):
                continue
            tagpath = '/' + '/'.join(map(self._node_repr, nodes))
            self.tagpaths.append(tagpath)
            self.tagpath_nodes[tagpath].append(nodes)