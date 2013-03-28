# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Camptocamp SA
#    Author Joel Grand-Guillaume
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tools.translate import _
import base64
import csv
import tempfile
import datetime
from file_parser import FileParser
try:
    import xlrd
except:
    raise Exception(_('Please install python lib xlrd'))

def float_or_zero(val):
    """ Conversion function used to manage
    empty string into float usecase"""
    return float(val) if val else 0.0


class GenericFileParser(FileParser):
    """
    Standard parser that use a define format in csv or xls to import into a
    bank statement. This is mostely an example of how to proceed to create a new
    parser, but will also be useful as it allow to import a basic flat file.
    """

    def __init__(self, parse_name, ftype='csv'):
        conversion_dict = {
                            'ref': unicode,
                            'label': unicode,
                            'date': datetime.datetime,
                            'amount': float_or_zero,
                            'commission_amount': float_or_zero
                          }
        # Order of cols does not matter but first row of the file has to be header
        keys_to_validate = ['ref', 'label', 'date', 'amount', 'commission_amount']
        super(GenericFileParser, self).__init__(parse_name, keys_to_validate=keys_to_validate, ftype=ftype, conversion_dict=conversion_dict)

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == 'generic_csvxls_so'

    def get_st_line_vals(self, line, *args, **kwargs):
        """
        This method must return a dict of vals that can be passed to create
        method of statement line in order to record it. It is the responsibility
        of every parser to give this dict of vals, so each one can implement his
        own way of recording the lines.
            :param:  line: a dict of vals that represent a line of result_row_list
            :return: dict of values to give to the create method of statement line,
                     it MUST contain at least:
                {
                    'name':value,
                    'date':value,
                    'amount':value,
                    'ref':value,
                    'label':value,
                    'commission_amount':value,
                }
        In this generic parser, the commission is given for every line, so we store it
        for each one.
        """
        return {
            'name': line.get('label', line.get('ref', '/')),
            'date': line.get('date', datetime.datetime.now().date()),
            'amount': line.get('amount', 0.0),
            'ref': line.get('ref', '/'),
            'label': line.get('label', ''),
            'commission_amount': line.get('commission_amount', 0.0),
        }

    def _post(self, *args, **kwargs):
        """
        Compute the commission from value of each line
        """
        res = super(GenericFileParser, self)._post(*args, **kwargs)
        val = 0.0
        for row in self.result_row_list:
            val += row.get('commission_amount', 0.0)
        self.commission_global_amount = val
        return res