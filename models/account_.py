from odoo import api, fields, models
from datetime import date, timedelta, datetime
import logging

_logger = logging.getLogger(__name__)

class AccountReportByCity(models.TransientModel):
    _name = 'report.turnover.city'

    city_ids = fields.Many2many("vit.kota", string='Kota', required=False)
    over_due = fields.Selection([
        ('30', '30 Hari'),
        ('60', '60 Hari'),
        ('90', '90 Hari'),
    ], 'Piutang Jatuh Tempo: ', default='30')
    
    @api.multi
    def print_report_turnover_by_city(self):
        months = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        groupby_dict = {}
        today = date.today()
        check_date = datetime.combine(today, datetime.min.time())
        over_due = int( self.over_due )

        if len(self.city_ids) == 0:
            self.city_ids = self.env['vit.kota'].search([])

        for city in self.city_ids:
            salespersons = self.env['res.users'].search([])

            for salesperson in salespersons:
                invoices = self.env['account.invoice'].search([ 
                    ('state', '=', 'open'), 
                    ('type', '=', 'out_invoice'), 
                    ('user_id.name', '=', salesperson.name),
                    ('date_due', '<=', today) 
                ],
                order="date_invoice asc")

                for invoice in invoices:
                    due_date = datetime.strptime(invoice.date_invoice, '%Y-%m-%d') + timedelta(days=over_due)
                    if due_date > check_date:
                        continue

                    month = months[datetime.strptime(invoice.date_invoice, '%Y-%m-%d').month-1]

                    if city.name not in groupby_dict:
                        groupby_dict[city.name] = {
                            'Januari': {},
                            'Februari': {},
                            'Maret': {},
                            'April': {},
                            'Mei': {},
                            'Juni': {},
                            'Juli': {},
                            'Agustus': {},
                            'September': {},
                            'Oktober': {},
                            'November': {},
                            'Desember': {}
                        }

                    curr_dist = groupby_dict[city.name][month]

                    if salesperson.name not in curr_dist:
                        curr_dist[salesperson.name] = invoice.residual_signed
                    else:
                        curr_dist[salesperson.name] = curr_dist[salesperson.name] + invoice.residual_signed

        datas = {
            'ids': self.ids,
            'model': 'report.turnover.city',
            'form': groupby_dict,

        }
        return self.env['report'].get_action(self,'report_turnover_by_city.temp_report_turnover_by_city', data=datas)