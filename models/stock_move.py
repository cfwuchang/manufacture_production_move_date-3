from odoo.exceptions import UserError
from odoo import _, api, fields, models

class MrpProduction(models.Model):
    _inherit = "stock.move"
    

    x_check_production_id=fields.Many2one('mrp.production',string=u'查询id')
    date_move_list = fields.Date(copy=False,help='组件预期到厂时间',string=u"需求时间",)



    @api.onchange('date_move_list')
    def _onchange_date(self):
        if self.raw_material_production_id or self.picking_id:
            att_model = self.env['stock.move']
            query = [("state","!=","draft"),("state","!=","cancel"),("state","!=","done")]
            for i in att_model.search(query):
                if self.product_id==i.product_id:
                    if self.reference =='done':
                        raise UserError('此产品以移动完成了，不能修改产品时间')
                    else:
                        i.write({'date_move_list':self.date})
        else:
            pass
            
    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty(self):
        if self.state!='draft' and self.state!='cancel' and ("WH/MO" in self.reference):
            self.write({'product_uom_qty':self.product_uom_qty})
            return {
            "warning": {
            'title': '提示!',
            'message': '请告知仓库你这产品修改了数量',
            },
            }
