from odoo import api, fields, models, SUPERUSER_ID
import re
import base64
from odoo.exceptions import UserError
import os

class WizHospitalImage(models.TransientModel):
    _name = "wiz.hospital.image"

    name = fields.Char('Image Name', size=512)
    image = fields.Binary('Image')

    @api.model
    def default_get(self, fields):

        context = self._context or {}
        res = super(WizHospitalImage, self).default_get(fields)
        hospital = self.env['admit'].browse(self._context.get('active_id'))

        name = '%r' % hospital.name_pat
        name = re.sub(r'\\', "/", name)
        name = name.replace('/', '-')
        name = name.replace(' ', '')
        name = name.strip()
        if name.startswith("u'"):
            name = name[2:]
        elif name.startswith('u"'):
            name = name[2:]
        if name.endswith("'"):
            name = name[:-1]
        elif name.endswith('"'):
            name = name[:-1]

        res.update({'name': name + '.jpg', 'image': hospital.image})
        return res

    def create_image(self):

        context = self._context or {}
        adm = self.env['admit'].browse(self._context.get('active_id'))
        each = self.read(['image', 'name'])

        if each[0]['name'] and not each[0]['image']:
            raise UserError(_('Please select the image.'))
        try:
            if each[0]['name'] and each[0]['image']:
                import io, StringIO
                from PIL import Image
                image_stream = io.BytesIO(each[0]['image'].decode('base64'))
                img = Image.open(image_stream)
                img.thumbnail((240, 200), Image.ANTIALIAS)
                img_stream = StringIO.StringIO()
                img.save(img_stream, "JPEG")
                bin = base64.decodestring(img_stream.getvalue().encode('base64'))
                filename = str(os.getcwd() + '/Photo/Hospital/Hos.' + each[0]['name'])
                f = open(filename, 'wb')
                f.write(bin)
                adm.write({'image_url': 'Hos.' + each[0]['name']})
        except:
            pass

        return {'type': 'ir.actions.act_window_close'}



    def clear_image(self):

        context = self._context or {}
        adm = self._context.get('active_ids', [])
        model = self._context.get('active_model')
        if model == None:
            return {'type': 'ir.actions.act_window_close'}
        try:
            precost = self.env['admit'].browse(self._context.get('active_id')).write({'image_url': False})

        except:
            pass
        return {'type': 'ir.actions.act_window_close'}
