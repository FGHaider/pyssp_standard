# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 14:14:27 2023

@author: robha67
"""

from pyssp_standard import SRMD, Classification, ClassificationEntry


def create_credibilityinfo_srmd(write_file):
    """Input: name and path of srmd file to be created
    Output: srmd file created at input path
    
    The Function creates an empty xml skeleton of the format specified in 'A concept for Credibility assessment of Arcraft System Simualtors, 
    Eek, Hällqvist, Gavel, and Ölvander. In Journal of Aerospace and Information Systems, AIAA, June, 2016. This skeleton is realized 
    in the format of the SRMD specification usch that it can be parsed by any SRMD supporting tool. 
    The format contains three different top level classifications: model_info, static_measures, and dynamic measures. The model_info 
    classification groups all genereal model information. The static_measures classification type groups any static (not varyin with simulated time) measures
    of credibility. See, for example, the Credibility Assesment Scale for more examples of static measures. The last classification type groups all dynamic_measures  
    of credibility into one category. The 'credibility_level' metric is an integer ranging from 0 to 3 where 0) tranlates to not implemented, 1) 
    no credibility, 2) degraded credibility, and 3) Normal credibility""" 
    
    with SRMD(write_file,'w') as file:
        classification = Classification(classification_type='model_info')
        classification.add_classification_entry(ClassificationEntry('Material Group', 'XX'))
        file.add_classification(classification)
        
        classification = Classification(classification_type='static_measures')
        classification.add_classification_entry(ClassificationEntry('system_type', 'XX'))
        classification.add_classification_entry(ClassificationEntry('fidelity', 'XX'))
        classification.add_classification_entry(ClassificationEntry('signal_propagation', 'XX'))
        file.add_classification(classification)
        classification = Classification(classification_type='dynamic_measures')
        classification.add_classification_entry(ClassificationEntry('credibility_level', 'Dynamic measure provided as output by an executable meta-model'))
        classification.add_classification_entry(ClassificationEntry('reason_1', 'Explaination for credibility_level=1'))
        classification.add_classification_entry(ClassificationEntry('reason_2', 'Explaination for credibility_level=2'))
        classification.add_classification_entry(ClassificationEntry('reason_n', 'Explaination for credibility_level=n'))
        file.add_classification(classification)