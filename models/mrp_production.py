from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)
from dateutil.relativedelta import relativedelta


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def _get_default_date_move(self):
        return self._get_default_date_planned_start()

    date_move = fields.Date(copy=False, default=_get_default_date_move,help='组件预期到厂时间',string=u"需求时间")

    check=fields.Char(string=u'查询值')
    # check_1=fields.Char(string=u'查询值-1')

    check_list=fields.One2many('stock.move', 'raw_material_production_id',string=u'查询行')
    # check_list_1=fields.One2many('stock.move', 'x_check_production_id',string=u'查询行')

    @api.onchange('check')
    def _get_check_list_1(self):
        id=[]
        for i in self.move_raw_ids:
            if self.check in i.product_id.name:
                # self.check_list = [(0, 0, i)]
                id.append(i.id)
        self.check_list = [(6, 0, id)]


    
    
    # def write(self, vals):
    #     """Store move date before write and then restore."""

    #     # Update orig stock moves if date move has changed
    #     if vals.get('date_move'):
    #         for move in self.move_raw_ids:
    #             # _logger.warning(["UPDATE ORIG MOVES", move.move_orig_ids])
    #             move.move_orig_ids.write({'date': vals.get('date_move')})  

    #     # Store current stock moves and execute write
    #     old_move_ids =  [production.move_raw_ids.read(['id', 'date']) for production in self]
    #     res = super(MrpProduction, self).write(vals)

    #     # Rewrite stock moves if stock moves have changed
    #     if vals.get('move_raw_ids'):
    #         move_raw_ids = vals['move_raw_ids']
    #         vals.clear() 
    #         vals['move_raw_ids'] = move_raw_ids
    #         res = super(MrpProduction, self).write(vals)
    #     # Otherwise update stock moves with old date
    #     else:
    #         for moves in old_move_ids:
    #             for move in moves:
    #                 move_id = self.env['stock.move'].browse(move['id'])
    #                 move_id.write({'date': move['date']})

    @api.onchange('date_planned_start',"product_id")
    def _onchange_date_planned_start(self):
        """Do not update stock move date."""
        if self.date_planned_start and not self.is_planned:
            date_planned_finished = self.date_planned_start + relativedelta(days=self.product_id.produce_delay)
            date_planned_finished = date_planned_finished + relativedelta(days=self.company_id.manufacturing_lead)
            if date_planned_finished == self.date_planned_start:
                date_planned_finished = date_planned_finished + relativedelta(hours=1)
            self.date_planned_finished = date_planned_finished
            # self.move_raw_ids = [(1, m.id, {'date': self.date_planned_start}) for m in self.move_raw_ids]
            self.move_finished_ids = [(1, m.id, {'date': date_planned_finished}) for m in self.move_finished_ids]

    @api.onchange('date_move')
    def _onchange_date_move(self):
        """Update stock move date."""
        if self.date_move:
            self.move_raw_ids = [(1, m.id, {'date_move_list': self.date_move}) for m in self.move_raw_ids]
            att_model = self.env['stock.picking']
            query = [("state","!=","draft"),("state","!=","cancel"),("state","!=","done")]
            for i in att_model.search(query):
                if self.name == i.origin:
                    i.move_ids_without_package = [(1, m.id, {'date_move_list': self.date_move}) for m in i.move_ids_without_package]

        
