# -*- coding: utf-8 -*-
# Copyright (C) 2016 John W. Viloria Amaris <john.viloria.amaris@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartnerDocumentType(models.Model):
    _name = 'res.partner.document.type'
    _description = 'Partner Document Type'

    name = fields.Char('Document Type', size=100, required=True)
    code = fields.Char('Code', size=2, required=True)
    checking_required = fields.Boolean('VAT Check Required',
                                       default=False)


class ResPartner(models.Model):
    _inherit = ['res.partner']

    document_type_id = fields.Many2one('res.partner.document.type',
                                       'Document Type')

    @api.constrains('vat', 'document_type_id', 'country_id')
    def check_vat(self):
        '''
        Check the VAT number depending of the country.
        http://sima-pc.com/nif.php
        '''
        def _checking_required(partner):
            '''
            Este método solo aplica para Colombia y obliga a seleccionar
            un tipo de documento de identidad con el fin de determinar
            si es verificable por el algoritmo VAT. Si no se define,
            de todas formas el VAT se evalua como un NIT/RUT.
            '''
            return ((partner.document_type_id and \
                partner.document_type_id.checking_required) or \
                not partner.document_type_id) == True

        msg = 'The Vat does not seems to be correct.'
        for partner in self:
            if not partner.vat:
                continue
            if partner.country_id:
                vat_country = partner.country_id.code.lower()
                vat_number = partner.vat
            else:
                vat_country, vat_number = self._split_vat(partner.vat)
            if not hasattr(self, 'check_vat_' + vat_country):
                continue
            check = getattr(self, 'check_vat_' + vat_country)
            if vat_country == 'co':
                if not _checking_required(partner):
                    continue
            if not check(vat_number):
                raise ValidationError(_(msg))
        return True

    def check_vat_co(self, vat):
        '''
        Check VAT Routine for Colombia.
        '''
        if type(vat) == str:
            vat = vat.replace('-', '', 1).replace('.', '', 2)
        if len(str(vat)) < 4:
            return False
        try:
            int(vat)
        except ValueError:
            return False
        # Validación Nit Terceros del exterior
        if len(str(vat)) == 9 and str(vat)[0:5] == '44444' \
                and int(str(vat)[5:]) <= 9000 \
                and int(str(vat)[5:]) >= 4001:
            return True
        prime = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
        sum = 0
        vat_len = len(str(vat))
        for i in range(vat_len - 2, -1, -1):
            sum += int(str(vat)[i]) * prime[vat_len - 2 - i]
        if sum % 11 > 1:
            return str(vat)[vat_len - 1] == str(11 - (sum % 11))
        else:
            return str(vat)[vat_len - 1] == str(sum % 11)
