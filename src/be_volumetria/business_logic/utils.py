import warnings
#suppressing deprecation warnings due to the use of 'imp' module
#deprecation warnings would break pytest tests
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import tensorflow as tf 
import numpy as np
import os


def load_automl_model(path: str):
    print(os.path.curdir)
    my_model = tf.saved_model.load(path)
    #print(list(my_model.signatures.keys()))
    infer = my_model.signatures["serving_default"]
    #print(infer.structured_outputs)
    return infer


def reorder_predictions(labels, scores):
    """
        Reorders a batch of predictions by labels alphabetical order along the predictions axis

        :param labels: numpy array with axes
                        0: batch
                        1: predictions

        :param scores: numpy array with axes
                        0: batch
                        1: predictions
    """
    # Structured numpy arrays! :D
    data=np.zeros(labels.shape,dtype={'names':('labels', 'scores'), 'formats':(labels.dtype, scores.dtype)})
    data['labels']=labels
    data['scores']=scores
    ordered_preds = np.sort(data, axis=1, order=['labels'])
    reordered_labels = ordered_preds['labels']
    reordered_scores = ordered_preds['scores']
    return reordered_labels, reordered_scores