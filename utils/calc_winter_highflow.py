import numpy as np
import pandas as pd
from scipy import stats
from utils.helpers import median_of_time
from classes.FlowExceedance import FlowExceedance
from params import winter_params

def calc_winter_highflow_annual(matrix, exceedance_percent):
    max_nan_allowed_per_year = winter_params['max_nan_allowed_per_year']
    max_zero_allowed_per_year = winter_params['max_zero_allowed_per_year']

    exceedance_value = {}
    freq = {}
    duration = {}
    timing = {}

    exceedance_value[2] = 26
    exceedance_value[5] = 26
    exceedance_value[10] = 26
    exceedance_value[20] = 26
    exceedance_value[50] = 35

    for i in exceedance_percent:
        #exceedance_value[i] = np.nanpercentile(matrix, 100 - i)
        freq[i] = []
        duration[i] = []
        timing[i] = []

    for column_number, flow_column in enumerate(matrix[0]):

        if np.isnan(matrix[:, column_number]).sum() > max_nan_allowed_per_year or np.count_nonzero(matrix[:, column_number]==0) > max_zero_allowed_per_year:
            for percent in exceedance_percent:
                freq[percent].append(None)
                duration[percent].append(None)
                timing[percent].append(None)
            continue

        exceedance_object = {}
        exceedance_duration = {}
        current_flow_object = {}

        """Init current flow object"""
        for percent in exceedance_percent:
            exceedance_object[percent] = []
            exceedance_duration[percent] = []
            current_flow_object[percent] = None

        for row_number, flow_row in enumerate(matrix[:, column_number]):

            for percent in exceedance_percent:
                if bool(flow_row < exceedance_value[percent] and current_flow_object[percent]) or bool(row_number == len(matrix[:, column_number]) - 1 and current_flow_object[percent]):
                    """End of a object if it falls below threshold, or end of column"""
                    current_flow_object[percent].end_date = row_number + 1
                    exceedance_duration[percent].append(current_flow_object[percent].duration)
                    current_flow_object[percent] = None

                elif flow_row >= exceedance_value[percent]:
                    if not current_flow_object[percent]:
                        """Begining of a object"""
                        exceedance_object[percent].append(FlowExceedance(row_number, None, 1, percent))
                        current_flow_object[percent] = exceedance_object[percent][-1]
                        current_flow_object[percent].add_flow(flow_row)
                    else:
                        """Continue of a object"""
                        current_flow_object[percent].add_flow(flow_row)
                        current_flow_object[percent].duration = current_flow_object[percent].duration + 1

        for percent in exceedance_percent:
            freq[percent].append(len(exceedance_object[percent]))
            duration[percent].append(np.nanmedian(exceedance_duration[percent]))
            timing[percent].append(median_of_time(exceedance_object[percent]))

    return timing, duration, freq

def calc_winter_highflow_POR(matrix, exceedance_percent):

    exceedance_object = {}
    exceedance_value = {}
    current_flow_object = {}
    freq = {}
    duration = {}
    timing = {}
    magnitude = {}
    average_annual_flow = np.nanmedian(matrix)
    rank = {}

    exceedance_value[2] = 57.7
    exceedance_value[5] = 57.7
    exceedance_value[10] = 12.7
    exceedance_value[20] = 19.7
    exceedance_value[50] = 18.1


    for i in exceedance_percent:
        #exceedance_value[i] = np.nanpercentile(matrix, 100 - i)
        exceedance_object[i] = []
        current_flow_object[i] = None
        freq[i] = 0
        duration[i] = []
        timing[i] = []
        magnitude[i] = []
        matrix_winter = matrix[60:183,:] # pull out flows from Dec1-Apr30 for every year
        matrix_winter_nan = matrix_winter[~np.isnan(matrix_winter)] # remove all nan values for the percentile of score function
        rank[i] = stats.percentileofscore(matrix_winter_nan, exceedance_value[i], kind='mean')

        if i == 50:
            matrix_salmon = matrix_nan[62:213]
            print(len(matrix_salmon))
            rank[i] = stats.percentileofscore(matrix_salmon, exceedance_value[i], kind='mean')

    for column_number, flow_column in enumerate(matrix[0]):
        for row_number, flow_row in enumerate(matrix[:, column_number]):

            for percent in exceedance_percent:
                if flow_row < exceedance_value[percent] and current_flow_object[percent] or row_number == len(matrix[:, column_number]) - 1 and current_flow_object[percent]:
                    """End of a object if it falls below threshold, or end of column"""
                    current_flow_object[percent].end_date = row_number + 1
                    duration[percent].append(current_flow_object[percent].duration)
                    magnitude[percent].append(max(current_flow_object[percent].flow) / average_annual_flow)
                    current_flow_object[percent] = None

                elif flow_row >= exceedance_value[percent]:
                    if not current_flow_object[percent]:
                        """Begining of a object"""
                        exceedance_object[percent].append(FlowExceedance(row_number + 1, None, 1, percent))
                        current_flow_object[percent] = exceedance_object[percent][-1]
                        current_flow_object[percent].add_flow(flow_row)
                        timing[percent].append(row_number + 1)
                        freq[percent] = freq[percent] + 1
                    else:
                        """Continue of a object"""
                        current_flow_object[percent].add_flow(flow_row)
                        current_flow_object[percent].duration = current_flow_object[percent].duration + 1
    print(rank)
    return timing, duration, freq, magnitude, rank
