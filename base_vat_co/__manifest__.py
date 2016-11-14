# -*- coding: utf-8 -*-
# Copyright (C) 2016 John W. Viloria Amaris <john.viloria.amaris@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name":"Base Vat Colombia",
    "description":"""\
Base Vat Colombia
==================================

Module for Colombian Rut/Nit checking.
    """,
    "depends":['base','base_vat'],
    "category":"Invoice",
    "author":"John Viloria Amaris",
    'license': 'AGPL-3',
    "data":[
        "partner_data.xml",
        "views/res_partner_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable":True
 }
