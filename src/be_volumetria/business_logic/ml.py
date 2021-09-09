from be_volumetria.core.config import UNKNOWN_CLASS_THRESHOLD, VOLUMETRIA_MODEL_SX, VOLUMETRIA_MODEL_DX
from be_volumetria.business_logic.utils import load_automl_model, reorder_predictions
from loguru import logger

import warnings
#suppressing deprecation warnings due to the use of 'imp' module
#deprecation warnings would break pytest tests
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import tensorflow as tf 
import numpy as np


class IncompatibleClassificationsError(Exception):
    pass


class VolumetriaInferenceModel:
    @classmethod
    def from_filepath(cls, model_path):
        """
            Creates an instance containing a model loaded from a filepath
            
            :param model_path: a filepath, can be a GCS path too
            
            :returns: VolumetriaInferenceModel instance
        """
        inference_function = load_automl_model(model_path)
        return cls(inference_function)
    
    def __init__(self, inference_function):
        """
            It is advisable to use a classmethod to create instances instead of this constructor
        """
        self.inference_function = inference_function
        self.debug = False
        
    def _debug(self, val):
        self.debug = val
        
    def infer_images(self, batch_of_image_bytes):
        """
            produces ordered predctions (by class alphabetical order) given a batch of images
            :param batch_of_image_bytes: batch of images in bytes format

            :returns: tuple of (ordered labels, ordered scores by corresponding labels)
        """
        pred = self.inference_function(
            image_bytes=tf.convert_to_tensor(batch_of_image_bytes), 
            key=tf.convert_to_tensor('')
        )
        labels = pred["labels"].numpy()
        scores = pred["scores"].numpy()
        ordered_labels, ordered_scores = reorder_predictions(labels, scores)
        if self.debug:
            print(f"pred: {pred}")
            print(f"labels: {labels}")
            print(f"scores: {scores}")
            print(f"ordered_labels: {ordered_labels}")
            print(f"ordered_scores: {ordered_scores}")
        return ordered_labels, ordered_scores


class VolumetriaInferenceEnsamble:
    @classmethod
    def from_filepath(cls, model_path_sx, model_path_dx=None):
        """
            Creates an instance containing SX and DX models loaded from a filepath
            
            :param model_path_sx: a filepath, can be a GCS path too
            :param model_path_dx: a filepath, can be a GCS path too, if omitted, 
                                  SX model will be used for DX inference
                                  
            :returns: VolumetriaInferenceEnsamble instance
        """
        vol_model_sx = VolumetriaInferenceModel.from_filepath(model_path_sx)
        if model_path_dx is None:
            # same model for DX and SX
            vol_model_dx = vol_model_sx
        else:
            vol_model_dx = VolumetriaInferenceModel.from_filepath(model_path_dx)
        return cls(vol_model_sx, vol_model_dx)
    
    
    @staticmethod
    def get_predicted_class(labels, scores, is_unknown_class=None, unknown_label=b'unknown', debug=False):
        """
            Extracts label and confidence from predictions typically 
            coming from VolumetriaInferenceEnsamble.infer function
            
            :param labels: batch of labels
            :param scores:  batch of scores
            :param is_unknown_class: batch of booleans, if omitted, unknown class will be ignored
            :param debug: enables debug stdout prints, defaults to False
                                  
            :returns: tuple containing:
            - ordered_labels: batch of alphabetically oredered labels
            - ordered_scores: batch of scores associated with each label
            - unknown_class: batch of booleans, when true, the class is unknown 
        """
        positional_predictions = scores.argmax(axis=1)
        predicted_labels = labels[np.arange(labels.shape[0]), positional_predictions]
        predicted_scores = scores[np.arange(scores.shape[0]), positional_predictions]
        if is_unknown_class is not None:
            predicted_labels[is_unknown_class] = unknown_label
        if debug:
            print(f"positional_predictions: {positional_predictions}")
            print(f"predicted_labels: {predicted_labels}")
            print(f"predicted_scores: {predicted_scores}")
        return predicted_labels, predicted_scores
    
    
    def __init__(self, vol_model_sx, vol_model_dx):
        """
            It is advisable to use a classmethod to create instances instead of this constructor
        """
        self.vol_model_sx = vol_model_sx
        self.vol_model_dx = vol_model_dx
        self.debug = False
    
    def _debug(self, val):
        self.vol_model_sx._debug(val)
        self.vol_model_dx._debug(val)
        self.debug = val  
    

    def infer(self, batch_of_sx_image_bytes, batch_of_dx_image_bytes, unknown_class_threshold = 0.0, return_intermediate_results = False):
        """
            Performs ensambled batch prediction on SX and DX images
            
            :param batch_of_sx_image_bytes: an iterable containing SX image bytes 
            :param batch_of_dx_image_bytes: an iterable containing DX image bytes 
            :param unknown_class_threshold: score threshold under which the inferred 
                                            class will be considered unknown
            :param return_intermediate_results: if true, also returns DX and SX results
                                            
            :returns: tuple containing
                      - ordered_labels: batch of alphabetically oredered labels
                      - ordered_scores: batch of scores associated with each label
                      - unknown_class: batch of booleans, when true, the class is unknown 
                      - ordered_scores_sx: batch of SX scores associated with each label 
                                           only returned if return_intermediate_results
                                           is True
                      - ordered_scores_dx: batch of DX scores associated with each label 
                                           only returned if return_intermediate_results
                                           is True
        """
        ordered_labels_sx, ordered_scores_sx = self.vol_model_sx.infer_images(batch_of_sx_image_bytes)
        ordered_labels_dx, ordered_scores_dx = self.vol_model_dx.infer_images(batch_of_dx_image_bytes)
        if not (ordered_labels_sx == ordered_labels_dx).all():
            if self.debug:
                print(f"ordered_labels_sx: {ordered_labels_sx}")
                print(f"ordered_scores_sx: {ordered_scores_sx}")
                print(f"ordered_labels_dx: {ordered_labels_dx}")
                print(f"ordered_scores_dx: {ordered_scores_dx}")
            raise IncompatibleClassificationsError("DX and SX predictions are not compatible, please verify that SX and DX models produce the same labels")
        ordered_labels = ordered_labels_sx
        ensambled_scores = (ordered_scores_dx + ordered_scores_sx)/2
        is_unknown_class = ensambled_scores.max(axis=1) < unknown_class_threshold
        if self.debug:
            print(f"ordered_labels: {ordered_labels}")
            print(f"ordered_scores_sx: {ordered_scores_sx}")
            print(f"ordered_scores_dx: {ordered_scores_dx}")
            print(f"ensambled_scores: {ensambled_scores}")
            print(f"is_unknown_class: {is_unknown_class}")
        if return_intermediate_results:
            return ordered_labels, ensambled_scores, is_unknown_class, ordered_scores_sx, ordered_scores_dx
        else:
            return ordered_labels, ensambled_scores, is_unknown_class
        

class VolumetriaInferenceEnsambleHub:
    def __init__(self):
        logger.info(f"Loading models from {VOLUMETRIA_MODEL_SX}, {VOLUMETRIA_MODEL_DX}")
        self.model = VolumetriaInferenceEnsamble.from_filepath(VOLUMETRIA_MODEL_SX, VOLUMETRIA_MODEL_DX)
        logger.info("Model(s) loaded")

    def check_model(self):
        logger.info(f"checking if model is loaded")
        logger.info(f"{self.model}")
        return self.model

    def predict(self, sx_bytes: bytes, dx_bytes: bytes) -> dict:
        """
            Main function for volume prediction \n
            The predictions for the two images are ensambled and the result score is thresholded.
            If the score does not exceed the threshold, the 'unknown' class is returned

            :param sx_bytes: bytes of left image to be predicted
            :param sx_bytes: bytes of right image to be predicted

            :returns: dictionary containing labels and scores for thresholded ensamble class
        """
        logger.debug("Performing volume inference")
        ordered_labels, ensambled_scores, is_unknown_class, _, _ = self.model.infer(
            [sx_bytes], [dx_bytes], unknown_class_threshold = UNKNOWN_CLASS_THRESHOLD, return_intermediate_results = True
        )

        logger.debug(f"Packing results")
        #ensamble_predictions = dict(zip(ordered_labels[0],ensambled_scores[0]))
        labels_batch, scores_batch = VolumetriaInferenceEnsamble.get_predicted_class(
            ordered_labels, ensambled_scores, is_unknown_class
        )
        ensamble_thresholded_prediction = {
            "label": labels_batch[0],
            "score": scores_batch[0]
        }
        return ensamble_thresholded_prediction
