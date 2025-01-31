#pylint: disable=W0403,C0103,R0901,R0904,R0913,C0302
from __future__ import (absolute_import, division, print_function)
from six.moves import range
import numpy
import sys
# from HFIR_4Circle_Reduction import fourcircle_utility
# from HFIR_4Circle_Reduction import guiutility

import py4circle.interface.gui.MyTableWidget as tableBase


class IntegratedCountsTable(tableBase.NTableWidget):
    """ Extended table widget for integrated counts in ROI
    """
    def __init__(self, parent):
        """

        :param parent:
        """
        tableBase.NTableWidget.__init__(self, parent)

        # set up list
        self._tableSetupList = list()
        self._tableColumnNames = list()
        # dictionary to map Pt number to row number
        self._ptNumberDict = dict()
        # calculated value column number
        self._calculatedColumnIndex = None

        return

    def append_integrated_pt_row(self, pt_number):
        """
        append a new row
        :param pt_number:
        :return:
        """
        # check inputs
        assert isinstance(pt_number, int), 'Pt number {0} shall be an integer but not a {1}' \
                                           ''.format(pt_number, type(pt_number))

        # construct
        row_value_list = [None] * len(self._tableSetupList)
        row_value_list[0] = pt_number

        self.append_row(row_value_list)

        # add to management
        self._ptNumberDict[pt_number] = self.rowCount() - 1

        return

    def get_column_data(self, col_name):
        """
        get column data
        :param col_name:
        :return:
        """
        # check input
        assert isinstance(col_name, str), 'Column name {0} must be an integer but not a {1}.' \
                                          ''.format(col_name, type(col_name))

        # get column
        try:
            col_index = self._tableColumnNames.index(col_name)
        except IndexError:
            err_msg = 'Column name {0} does not exist in table whose columns are {1}' \
                      ''.format(col_name, self._tableColumnNames)
            raise RuntimeError(err_msg)

        # set up vector
        num_rows = self.rowCount()
        value_list = list()
        for row_index in range(num_rows):
            value_list.append(self.get_cell_value(row_index, col_index))

        return numpy.array(value_list)

    def get_integrated_counts(self, pt_number=None, row_number=None):
        """ get the integrated counts of one row or one certain Pt
        :param pt_number:
        :param row_number:
        :return:
        """
        # check input and parse pt number to row number
        if pt_number is None and row_number is None:
            raise RuntimeError('Neither Pt number nor row number is given.')
        elif pt_number is not None:
            assert isinstance(pt_number, int), 'Pt number {0} must be an integer but not a {1}' \
                                               ''.format(pt_number, type(pt_number))
            row_number = self._ptNumberDict[pt_number]
        elif row_number is not None:
            assert isinstance(row_number, int), 'Row number {0} must be an integer but not a {1}' \
                                               ''.format(row_number, type(row_number))
        else:
            raise RuntimeError('Pt number and row number cannot be given simultaneously')

        # set the dictionary
        value_dict = dict()
        for col_index, col_tup in enumerate(self._tableSetupList):
            col_name = col_tup[0]
            if '0' <= col_name <= '9':
                col_name = 'roi{0}'.format(col_name)
            if col_index == self._calculatedColumnIndex:
                allow_blank = True
            else:
                allow_blank = False
            value_dict[col_name] = self.get_cell_value(row_number, col_index, allow_blank)
        # END-FOR

        print ('[DB...BAT] Integrated counts: {0}'.format(value_dict))

        return value_dict

    def set_calculated_value(self, pt_number, value):
        """
        set the calculated value to the table
        :param pt_number:
        :param value:
        :return:
        """
        # get row number
        try:
            row_number = self._ptNumberDict[pt_number]
        except KeyError as key_err:
            raise RuntimeError('Pt number {0} ({1}) does not exist in table. FYI {2}.'
                               ''.format(pt_number, type(pt_number), key_err))

        # update value
        self.update_cell_value(row_number, self._calculatedColumnIndex, value)

        return

    def set_column_values(self, col_index, value_vec, skip=0):
        """
        set column values
        :param col_index:
        :param value_vec:
        :param skip:
        :return:
        """
        for index in range(len(value_vec)):
            row_index = index * (1 + skip)
            if row_index >= self.rowCount():
                break
            else:
                self.update_cell_value(row_index, col_index, value_vec[index])

        # END-FOR

        return

    def set_integrated_value(self, pt_number, roi_name, value):
        """
        set an integrated value to a pt by its ROI name
        :param pt_number:
        :param roi_name:
        :param value:
        :return:
        """
        # check input
        assert isinstance(pt_number, int), 'Pt number {0} shall be an integer but not a {1}' \
                                           ''.format(pt_number, type(pt_number))
        # convert ROI name to be string
        roi_name = str(roi_name)

        # get row number
        if pt_number in self._ptNumberDict:
            row_number = self._ptNumberDict[pt_number]
        else:
            raise RuntimeError('Pt {0} is not in the table.'.format(pt_number))

        # get column number
        try:
            col_number = self._tableColumnNames.index(roi_name)
        except ValueError as index_err:
            raise RuntimeError('Unable to get column number for {0} due to {1}'
                               ''.format(roi_name, index_err))

        # set value
        self.update_cell_value(row_number, col_number, value)

        return

    def setup(self, index_name, index_type, roi_name_list):
        """
        Init setup: columns are to be created dynamically
        :return:
        """
        # check inputs
        assert isinstance(index_name, str), 'Index column name must be a string'
        assert isinstance(index_type, str), 'Index column type must be a string'
        self.check_cell_type(index_type, raise_if_wrong=True)

        # set up the set up list
        self._tableSetupList = list()
        self._tableColumnNames = list()

        # first item
        self._tableSetupList.append((index_name, index_type))
        self._tableColumnNames.append(index_name)

        for roi_name in sorted(roi_name_list):
            self._tableSetupList.append((str(roi_name), 'float'))
            self._tableColumnNames.append(str(roi_name))
        # END-FOR
        self._tableSetupList.append(('Result', 'float'))
        self._tableColumnNames.append('Result')
        self._calculatedColumnIndex = len(self._tableSetupList) - 1

        #
        self._tableSetupList.append(('Polarization', 'float'))
        self._tableColumnNames.append('Polarization')
        self._polarizationColumnIndex = len(self._tableSetupList) - 1

        # do set up
        self.init_setup(self._tableSetupList)

        return


class ScanListTable(tableBase.NTableWidget):
    """
    Extended table widget for peak integration
    """
    Table_Setup = [('Scan', 'int'),
                   ('Max Counts Pt', 'int'),
                   ('Max Counts', 'float'),
                   ('H', 'float'),
                   ('K', 'float'),
                   ('L', 'float'),
                   ('Q-range', 'float'),
                   ('Sample Temp', 'float'),
                   ('Selected', 'checkbox')]

    def __init__(self, parent):
        """
        :param parent:
        """
        tableBase.NTableWidget.__init__(self, parent)

        self._myScanSummaryList = list()

        self._currStartScan = 0
        self._currEndScan = sys.maxsize
        self._currMinCounts = 0.
        self._currMaxCounts = sys.float_info.max

        self._colIndexH = None
        self._colIndexK = None
        self._colIndexL = None

        return

    def filter_and_sort(self, start_scan, end_scan, min_counts, max_counts,
                        sort_by_column, sort_order):
        """
        Filter the survey table and sort
        Note: it might not be efficient here because the table will be refreshed twice
        :param start_scan:
        :param end_scan:
        :param min_counts:
        :param max_counts:
        :param sort_by_column:
        :param sort_order: 0 for ascending, 1 for descending
        :return:
        """
        # check
        assert isinstance(start_scan, int) and isinstance(end_scan, int) and end_scan >= start_scan
        assert isinstance(min_counts, float) and isinstance(max_counts, float) and min_counts < max_counts
        assert isinstance(sort_by_column, str), \
            'sort_by_column requires a string but not %s.' % str(type(sort_by_column))
        assert isinstance(sort_order, int), \
            'sort_order requires an integer but not %s.' % str(type(sort_order))

        # get column index to sort
        col_index = self.get_column_index(column_name=sort_by_column)

        # filter on the back end row contents list first
        self.filter_rows(start_scan, end_scan, min_counts, max_counts)

        # order
        self.sort_by_column(col_index, sort_order)

        return

    def filter_rows(self, start_scan, end_scan, min_counts, max_counts):
        """
        Filter by scan number, detector counts on self._myScanSummaryList
        and reset the table via the latest result
        :param start_scan:
        :param end_scan:
        :param min_counts:
        :param max_counts:
        :return:
        """
        # check whether it can be skipped
        if start_scan == self._currStartScan and end_scan == self._currEndScan \
                and min_counts == self._currMinCounts and max_counts == self._currMaxCounts:
            # same filter set up, return
            return

        # clear the table
        self.remove_all_rows()

        # go through all rows in the original list and then reconstruct
        for index in range(len(self._myScanSummaryList)):
            sum_item = self._myScanSummaryList[index]
            # check
            assert isinstance(sum_item, list)
            assert len(sum_item) == len(self._myColumnNameList) - 1
            # check with filters: original order is counts, scan, Pt., ...
            scan_number = sum_item[1]
            if scan_number < start_scan or scan_number > end_scan:
                continue
            counts = sum_item[0]
            if counts < min_counts or counts > max_counts:
                continue

            # modify for appending to table
            row_items = sum_item[:]
            counts = row_items.pop(0)
            row_items.insert(2, counts)
            row_items.append(False)

            # append to table
            self.append_row(row_items)
        # END-FOR (index)

        # Update
        self._currStartScan = start_scan
        self._currEndScan = end_scan
        self._currMinCounts = min_counts
        self._currMaxCounts = max_counts

        return

    def get_hkl(self, row_index):
        """
        Get peak index (HKL) from survey table (i.e., SPICE file)
        :param row_index:
        :return:
        """
        index_h = self.get_cell_value(row_index, self._colIndexH)
        index_k = self.get_cell_value(row_index, self._colIndexK)
        index_l = self.get_cell_value(row_index, self._colIndexL)

        return index_h, index_k, index_l

    def get_scan_numbers(self, row_index_list):
        """
        Get scan numbers with specified rows
        :param row_index_list:
        :return:
        """
        scan_list = list()
        scan_col_index = self.Table_Setup.index(('Scan', 'int'))
        for row_index in row_index_list:
            scan_number_i = self.get_cell_value(row_index, scan_col_index)
            scan_list.append(scan_number_i)
        scan_list.sort()

        return scan_list

    def get_selected_run_surveyed(self, required_size=1):
        """
        Purpose: Get selected pt number and run number that is set as selected
        Requirements: there must be one and only one run that is selected
        Guarantees: a 2-tuple for integer for return as scan number and Pt. number
        :param required_size: if specified as an integer, then if the number of selected rows is different,
                              an exception will be thrown.
        :return: a 2-tuple of integer if required size is 1 (as old implementation) or a list of 2-tuple of integer
        """
        # check required size?
        assert isinstance(required_size, int) or required_size is None, 'Required number of runs {0} must be None ' \
                                                                        'or an integer but not a {1}.' \
                                                                        ''.format(required_size, type(required_size))

        # get the selected row indexes and check
        row_index_list = self.get_selected_rows(True)

        if required_size is not None and required_size != len(row_index_list):
            raise RuntimeError('It is required to have {0} runs selected, but now there are {1} runs that are '
                               'selected.'.format(required_size, row_index_list))

        # get all the scans and rows that are selected
        scan_run_list = list()
        for i_row in row_index_list:
            # get scan and pt.
            scan_number = self.get_cell_value(i_row, 0)
            pt_number = self.get_cell_value(i_row, 1)
            scan_run_list.append((scan_number, pt_number))

        # special case for only 1 run that is selected
        if len(row_index_list) == 1 and required_size is not None:
            # get scan and pt
            return scan_run_list[0]
        # END-IF

        return scan_run_list

    def show_reflections(self, num_rows):
        """
        :param num_rows:
        :return:
        """
        assert isinstance(num_rows, int)
        assert num_rows > 0
        assert len(self._myScanSummaryList) > 0

        print ('Number of rows = {}; scan summary list = {}'.format(num_rows, len(self._myScanSummaryList)))

        for i_ref in range(min(num_rows, len(self._myScanSummaryList))):
            # get counts
            scan_summary = self._myScanSummaryList[i_ref]
            # check
            assert isinstance(scan_summary, list)
            assert len(scan_summary) == len(self._myColumnNameList) - 1
            # modify for appending to table
            row_items = scan_summary[:]
            max_count = row_items.pop(0)
            row_items.insert(2, max_count)
            row_items.append(False)
            # append
            self.append_row(row_items)
        # END-FOR

        return

    def set_survey_result(self, scan_summary_list):
        """

        :param scan_summary_list:
        :return:
        """
        # check
        assert isinstance(scan_summary_list, list)

        # Sort and set to class variable
        scan_summary_list.sort(reverse=True)
        self._myScanSummaryList = scan_summary_list

        return

    def setup(self):
        """
        Init setup
        :return:
        """
        self.init_setup(ScanListTable.Table_Setup)
        self.set_status_column_name('Selected')

        self._colIndexH = ScanListTable.Table_Setup.index(('H', 'float'))
        self._colIndexK = ScanListTable.Table_Setup.index(('K', 'float'))
        self._colIndexL = ScanListTable.Table_Setup.index(('L', 'float'))

        return

    def reset(self):
        """ Reset the inner survey summary table
        :return:
        """
        self._myScanSummaryList = list()

