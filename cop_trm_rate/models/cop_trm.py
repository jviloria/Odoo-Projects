# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    John W. Viloria Amaris <john.viloria.amaris@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#
# Dependencias:   -- python selenium [sudo apt-get -y install python-pip;sudo pip install selenium]
#                 -- python PhantomJS [sudo apt-get -y install phantomjs]
# NOTA: Si se presenta error al instalar PhantomJS, seguir los pasos de la url: https://gist.github.com/julionc/7476620
#
##############################################################################

from openerp import models, api
from selenium import webdriver
from os import path

BANREP_URL ="http://obieebr.banrep.gov.co/analytics/saw.dll?Go&path=/shared/Series%20Estad%C3%ADsticas/1.%20Tasa%20de%20Cambio%20Peso%20Colombiano/1.1%20TRM%20-%20Disponible%20desde%20el%2027%20de%20noviembre%20de%201991/1.1.6.TCM_TRM%20para%20un%20d%C3%ADa&lang=es&options=rdf&NQUser=publico&NQPassword=publico"


class trmColombian(models.Model):
    _inherit = 'res.currency.rate'

    def _banrep_scraping(self):
        res = False
        driver = webdriver.PhantomJS(service_log_path=path.devnull)
        for x in range(1,5):    # 5 intentos de obtener la trm
            driver.get(BANREP_URL)
            try:
                res = driver.find_element_by_xpath("//strong")
                res = res.text
                break
            except:
                pass
        driver.close()
        return res

    @api.model
    def get_colombian_trm(self):    #Este método debe ser llamado por un cron de Odoo
        trm = self._banrep_scraping()
        if trm:
            try:
                trm = trm.replace(".","").replace(",",".")  #Preparación para conversión
                trm = float(trm)                            #a Float
            except:
                trm = trm.replace(",","").replace(".",",")
                trm = float(trm)
        else:
            trm = 0
        currency_id = self.env['res.currency'].search([('name','in',('USD','usd'))])[0].id
        try:
            old_trm = self.search([('currency_id','=',currency_id)], limit=1, order='id desc')[0].rate
        except:
            old_trm = 0
        if trm > 0 and trm != old_trm:  #Solo se actualiza si ha cambiado
            vals = {
                'rate': trm,
                'currency_id': currency_id,
                'company_id': self.env.user.company_id.id
            }
            self.create(vals)