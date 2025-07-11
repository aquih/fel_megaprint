# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round
import requests
from lxml import etree
import logging

class Partner(models.Model):
    _inherit = 'res.partner'

    def obtener_partner_name_con_datos_sat(self, company_id, vat):
        if vat:
            company = self.env['res.company'].search([('id', '=', company_id)])
            datos_facturacion_fel = self._datos_sat(company, vat)
            if(not datos_facturacion_fel.get('nombre', {})):
                datos_facturacion_fel = self.env['res.partner']._datos_sat_cui(company, vat)
        return datos_facturacion_fel
    
    def _datos_sat(self, company, vat):
        res = {'nombre': '', 'nit': '', 'mensaje': ''}
        if vat:
            request_url = "apiv2"
            request_path = ""
            if company.pruebas_fel:
                request_url = "dev2.api"
                request_path = ""
            
            headers = { "Content-Type": "application/xml" }
            data = '<?xml version="1.0" encoding="UTF-8"?><SolicitaTokenRequest><usuario>{}</usuario><apikey>{}</apikey></SolicitaTokenRequest>'.format(company.usuario_fel, company.clave_fel)
            r = requests.post('https://'+request_url+'.ifacere-fel.com/'+request_path+'api/solicitarToken', data=data.encode('utf-8'), headers=headers)
            try: 
                resultadoXML = etree.XML(bytes(r.text, encoding='utf-8'))
            except Exception as e:
                logging.warning(f"Error al procesar respuesta: {e}")
                res['mensaje'] = 'No se pudo procesar la respuesta de token.'
                return res 

            if len(resultadoXML.xpath("//token")) > 0:
                token = resultadoXML.xpath("//token")[0].text

                headers = { "Content-Type": "application/xml", "authorization": "Bearer "+token }
                data = '<?xml version="1.0" encoding="UTF-8"?><RetornaDatosClienteRequest><nit>{}</nit></RetornaDatosClienteRequest>'.format(vat)
                r = requests.post('https://'+request_url+'.ifacere-fel.com/'+request_path+'api/retornarDatosCliente', data=data.encode('utf-8'), headers=headers)
                logging.warning(r.text)

                try:
                    resultadoXML = etree.XML(bytes(r.text, encoding='utf-8'))
                    if len(resultadoXML.xpath("//listado_errores")) == 0:
                        if resultadoXML.xpath("//nombre"):
                            res['nombre'] = resultadoXML.xpath("//nombre")[0].text
                            res['nit'] = vat
                            logging.warning(res)
                            return res
                    else:
                        res['mensaje'] =  "\n".join(f"{error.findtext('cod_error')}: {error.findtext('desc_error')}" for error in resultadoXML.xpath("//listado_errores/error"))
                        logging.warning(res)
                        return res

                except Exception as e:
                    logging.warning(f"Error al procesar respuesta: {e}")
                    res['mensaje'] = 'No se pudo procesar la respuesta.'
                    return res
        res['mensaje'] = 'No encontrado'
        return res

    def _datos_sat_cui(self, company, cui):
        res = {'nombre': '', 'nit': '', 'mensaje': ''}
        if cui:
            request_url = "apiv2"
            if company.pruebas_fel:
                request_url = "dev2.api"
            
            headers = { "Content-Type": "application/xml" }
            data = '<?xml version="1.0" encoding="UTF-8"?><SolicitaTokenRequest><usuario>{}</usuario><apikey>{}</apikey></SolicitaTokenRequest>'.format(company.usuario_fel, company.clave_fel)
            r = requests.post('https://'+request_url+'.ifacere-fel.com/api/solicitarToken', data=data.encode('utf-8'), headers=headers)
            
            try: 
                resultadoXML = etree.XML(bytes(r.text, encoding='utf-8'))
            except Exception as e:
                logging.warning(f"Error al procesar respuesta: {e}")
                res['mensaje'] = 'No se pudo procesar la respuesta de token.'
                return res 

            if len(resultadoXML.xpath("//token")) > 0:
                token = resultadoXML.xpath("//token")[0].text

                headers = { "Content-Type": "application/xml", "authorization": "Bearer "+token }
                data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><RetornaDatosClienteRequestCUI><CUI>{}</CUI></RetornaDatosClienteRequestCUI>'.format(cui)
                r = requests.post('https://'+request_url+'.ifacere-fel.com/api/retornarDatosClienteCui', data=data.encode('utf-8'), headers=headers)
                logging.warning(r.text)

                try: 
                    resultadoXML = etree.XML(bytes(r.text, encoding='utf-8'))
                    if len(resultadoXML.xpath("//listado_errores")) == 0:
                        if resultadoXML.xpath("//nombre"):
                            res['nombre'] = resultadoXML.xpath("//nombre")[0].text
                            res['nit'] = cui
                            logging.warning(res)
                            return res
                    else:
                        res['mensaje'] =  "\n".join(f"{error.findtext('cod_error')}: {error.findtext('desc_error')}" for error in resultadoXML.xpath("//listado_errores/error"))
                        logging.warning(res)
                        return res
                    
                except Exception as e:
                    logging.warning(f"Error al procesar respuesta: {e}")
                    res['mensaje'] = 'No se pudo procesar la respuesta.'
                    return res
        res['mensaje'] = 'No encontrado'
        return res
