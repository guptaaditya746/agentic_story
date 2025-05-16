import nltk
import numpy as np
from nltk.translate.bleu_score import SmoothingFunction
from multiprocessing import Pool, cpu_count

class SelfBleu:
    def __init__(self, generated_stories, gram=3, sample_size=500):
        """
        generated_stories: List of tokenized generated stories [[w1, w2, w3], [w1, w2, ...], ...]
        gram: BLEU n-gram size (default 3)
        sample_size: Number of examples to sample (default 500)
        """
        self.generated_stories = generated_stories
        self.gram = gram
        self.sample_size = min(sample_size, len(generated_stories))
        self.sampled_stories = self.generated_stories[:self.sample_size]
    
    def calc_bleu(self, reference, hypothesis, weight):
        return nltk.translate.bleu_score.sentence_bleu(
            reference, hypothesis, weight,
            smoothing_function=SmoothingFunction().method1
        )
    
    def get_score(self):
        weight = tuple((1. / self.gram for _ in range(self.gram)))
        pool = Pool(cpu_count())

        results = []
        for idx in range(len(self.sampled_stories)):
            hypothesis = self.sampled_stories[idx]
            reference = self.sampled_stories[:idx] + self.sampled_stories[idx+1:]
            results.append(pool.apply_async(self.calc_bleu, args=(reference, hypothesis, weight)))

        pool.close()
        pool.join()

        bleu_scores = [r.get() for r in results]
        avg_self_bleu = np.mean(bleu_scores)
        return avg_self_bleu
