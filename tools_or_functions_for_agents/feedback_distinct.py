#   Copyright (c) 2019 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# https://github.com/PaddlePaddle/models/blob/release/1.6/PaddleNLP/Research/Dialogue-PLATO/plato/metrics/metrics.py
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Metrics class.
"""

from collections import Counter

from nltk.translate import bleu_score
from nltk.translate.bleu_score import SmoothingFunction
import numpy as np


def distinct(seqs):
    """ Calculate intra/inter distinct 1/2. """
    batch_size = len(seqs)
    intra_dist1, intra_dist2 = [], []
    unigrams_all, bigrams_all = Counter(), Counter()
    for seq in seqs:
        unigrams = Counter(seq)
        bigrams = Counter(zip(seq, seq[1:]))
        intra_dist1.append((len(unigrams)+1e-12) / (len(seq)+1e-5))
        intra_dist2.append((len(bigrams)+1e-12) / (max(0, len(seq)-1)+1e-5))

        unigrams_all.update(unigrams)
        bigrams_all.update(bigrams)

    inter_dist1 = (len(unigrams_all)+1e-12) / (sum(unigrams_all.values())+1e-5)
    inter_dist2 = (len(bigrams_all)+1e-12) / (sum(bigrams_all.values())+1e-5)
    intra_dist1 = np.average(intra_dist1)
    intra_dist2 = np.average(intra_dist2)
    return intra_dist1, intra_dist2, inter_dist1, inter_dist2


"""
Purpose: It measures the diversity of n-grams (unigrams and bigrams) in a collection of sequences (like sentences or lists of words/tokens). This is a common metric in Natural Language Generation (NLG) to assess how varied and non-repetitive generated text is.
Inputs: It takes a list of sequences (seqs). Each sequence in the list is expected to be an iterable of items (e.g., a list of words).
Calculations:
Intra-Distinct Scores (intra_dist1, intra_dist2):
For each individual sequence, it calculates the ratio of unique unigrams (single words/tokens) to the total number of unigrams in that sequence (intra_dist1).
Similarly, it calculates the ratio of unique bigrams (pairs of adjacent words/tokens) to the total number of bigrams in that sequence (intra_dist2).
These individual intra-distinct scores are then averaged across all sequences.
Inter-Distinct Scores (inter_dist1, inter_dist2):
It considers all unigrams from all sequences together and calculates the ratio of unique unigrams across the entire collection to the total number of unigrams in the entire collection (inter_dist1).
It does the same for bigrams (inter_dist2).
Output: The function returns four values:
intra_dist1: Average Distinct-1 score within sequences.
intra_dist2: Average Distinct-2 score within sequences.
inter_dist1: Overall Distinct-1 score across all sequences.
inter_dist2: Overall Distinct-2 score across all sequences.
Higher distinct scores generally indicate more diverse and less repetitive text. The file also includes imports for bleu_score from NLTK, but this isn't used in the distinct function itself, suggesting it might have been part of a larger metrics module originally or intended for other evaluations.
"""