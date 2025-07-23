# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round
import requests
from lxml import etree
import logging

class Partner(models.Model):
    _inherit = 'res.partner'

    def guardar_nombre_facturacion_fel(self):
        vat = self.vat
        if self.nit_facturacion_fel:
            vat = self.nit_facturacion_fel
            
        res = self.obtener_datos_facturacion_fel(self.env.company, vat)
        self.nombre_facturacion_fel = res['nombre']

    def obtener_datos_facturacion_fel(self, company, vat):
        res = self._datos_sat(self.env.company, vat)
        if not res['nombre']:
            res = self._datos_sat_cui(self.env.company, vat)
        return res
    
    def _datos_sat(self, company, vat):
        request_url = "apiv2"
        request_path = ""
        if company.pruebas_fel:
            request_url = "dev2.api"
        headers = { "Content-Type": "application/xml" }
        data = '<?xml version="1.0" encoding="UTF-8"?><SolicitaTokenRequest><usuario>{}</usuario><apikey>{}</apikey></SolicitaTokenRequest>'.format(company.usuario_fel, company.clave_fel)
        resultado_certificador_token = requests.post('https://'+request_url+'.ifacere-fel.com/'+request_path+'api/solicitarToken', data=data.encode('utf-8'), headers=headers)
        logging.info(resultado_certificador_token.text)

        datos_contribuyente = { 'nombre': '', 'nit': '', 'mensaje': '' }

        try:
            resultado_token_XML = etree.XML(bytes(resultado_certificador_token.text, encoding='utf-8'))
            if len(resultado_token_XML.xpath("//token")) > 0:
                token = resultado_token_XML.xpath("//token")[0].text

                headers = { "Content-Type": "application/xml", "authorization": "Bearer "+token }
                data = '<?xml version="1.0" encoding="UTF-8"?><RetornaDatosClienteRequest><nit>{}</nit></RetornaDatosClienteRequest>'.format(vat)
                resultado_certificador = requests.post('https://'+request_url+'.ifacere-fel.com/'+request_path+'api/retornarDatosCliente', data=data.encode('utf-8'), headers=headers)
                logging.info(resultado_certificador.text)

                resultado_certificador_XML = etree.XML(bytes(resultado_certificador.text, encoding='utf-8'))
                
                if len(resultado_certificador_XML.xpath("//listado_errores")) == 0:
                    if resultado_certificador_XML.xpath("//nombre"):
                        datos_contribuyente['nombre'] = resultado_certificador_XML.xpath("//nombre")[0].text
                        datos_contribuyente['nit'] = vat
                else:
                    datos_contribuyente['mensaje'] =  "\n".join(f"{error.findtext('cod_error')}: {error.findtext('desc_error')}" for error in resultado_certificador_XML.xpath("//listado_errores/error"))

        except Exception as e:
            logging.warning(e)
            datos_contribuyente['mensaje'] = e

        return datos_contribuyente

    def _datos_sat_cui(self, company, cui):
        request_url = "apiv2"
        if company.pruebas_fel:
            request_url = "dev2.api"
        
        headers = { "Content-Type": "application/xml" }
        data = '<?xml version="1.0" encoding="UTF-8"?><SolicitaTokenRequest><usuario>{}</usuario><apikey>{}</apikey></SolicitaTokenRequest>'.format(company.usuario_fel, company.clave_fel)
        resultado_certificador_token = requests.post('https://'+request_url+'.ifacere-fel.com/api/solicitarToken', data=data.encode('utf-8'), headers=headers)
        logging.info(resultado_certificador_token.text)

        datos_contribuyente = { 'nombre': '', 'nit': '', 'mensaje': '' }

        try:
            resultado_token_XML = etree.XML(bytes(resultado_certificador_token.text, encoding='utf-8'))
            if len(resultado_token_XML.xpath("//token")) > 0:
                token = resultado_token_XML.xpath("//token")[0].text

                headers = { "Content-Type": "application/xml", "authorization": "Bearer "+token }
                data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><RetornaDatosClienteRequestCUI><CUI>{}</CUI></RetornaDatosClienteRequestCUI>'.format(cui)
                resultado_certificador = requests.post('https://'+request_url+'.ifacere-fel.com/api/retornarDatosClienteCui', data=data.encode('utf-8'), headers=headers)
                logging.info(resultado_certificador.text)

                resultado_certificador_XML = etree.XML(bytes(resultado_certificador.text, encoding='utf-8'))
                if len(resultado_certificador_XML.xpath("//listado_errores")) == 0:
                    if resultado_certificador_XML.xpath("//nombre"):
                        datos_contribuyente['nombre'] = resultado_certificador_XML.xpath("//nombre")[0].text
                        datos_contribuyente['nit'] = cui
                else:
                    datos_contribuyente['mensaje'] =  "\n".join(f"{error.findtext('cod_error')}: {error.findtext('desc_error')}" for error in resultado_certificador_XML.xpath("//listado_errores/error"))

        except Exception as e:
            logging.warning(e)
            datos_contribuyente['mensaje'] = e

        return datos_contribuyente