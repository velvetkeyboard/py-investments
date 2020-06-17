import os
import re
import json
import string
import requests
from db import Database
from lxml import html


class Companies(object):

    def get_all_data(self):
        raise NotImplemented


class BovespaCompanies(Companies):

    def get_all_data(self):
        ret = []
        for letter in list(string.ascii_uppercase):
            ret += self.get_companies(letter)
            break
        return ret

    def get_company_data(self, code, lang='en'):
        if lang == 'en':
            url = 'http://bvmf.bmfbovespa.com.br/en-us/markets/equities/companies/ExecutaAcaoConsultaInfoEmp.asp'
            params = {
                'CodCVM': code,
                'ViewDoc': 1,
                'AnoDoc': 2020,
                'VersaoDoc': 1,
                'NumSeqDoc': 90684,
                }
        else:
            url = 'http://bvmf.bmfbovespa.com.br/pt-br/mercados/acoes/empresas/ExecutaAcaoConsultaInfoEmp.asp'
            params = {
                'CodCVM': f'{code}',
                'ViewDoc': 1,
                'AnoDoc': '2020',
                'VersaoDoc': '1',
                'NumSeqDoc': '93733',
                }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            }

        resp = requests.get(url, params=params, headers=headers)
        tree = html.fromstring(resp.content)
        if lang == 'en':
            company_data_tr = tree.xpath('//*[@id="panel1a"]/table/tr')
        else:
            company_data_tr = tree.xpath('//*[@id="accordionDados"]/table/tr')

        ret = {}
        for tr in company_data_tr:
            '''
            - Trading Name
            - Trading Codes 
            - Industry Classification
            - Website
            '''
            column_name_td, column_value_td = tr.xpath('./td')
            column_name = column_name_td.text.lower().replace(' ', '_')
            if column_name == 'trading_codes':
                column_value = column_value_td.xpath('./a/text()')
            elif column_name == 'website':
                column_value = column_value_td.xpath('./a')[0].get('href')
            elif column_name == 'industry_classification':
                column_value = column_value_td.text.split(' / ')
            else:
                column_value = column_value_td.text
            ret[column_name] = column_value

        # TODO split into a separated function
        # Financial Data - BRL - thousand -------------------------------------
        financial_data_headers = []
        financial_data_headers_th = tree.xpath(
            '//*[@id="divDadosEconNovo"]/table[1]/thead/tr/th')
        for th in financial_data_headers_th:
            header = th.text.lower()\
                        .replace(' ', '_')\
                        .replace('-', '')\
                        .replace('__', '_')
            financial_data_headers.append(header)

        financial_data_tr = tree.xpath('//*[@id="divDadosEconNovo"]/table/tr')
        financial_data = []
        for tr in financial_data_tr:
            financial_data_row = {}
            for i, td in enumerate(tr.xpath('./td')):
                financial_data_row.update({
                    financial_data_headers[i]: td.text,
                    })
            financial_data.append(financial_data_row)
        ret['financial_data'] = financial_data
        # Income Statement - Consolidated -------------------------------------
        # Cash Flow Statement - Consolidated ----------------------------------

        # Position of Shareholders
        # Outstanding Shares
        # Capital Stock Composition

        return ret


    def get_companies(self, letter):
        ret = []
        url = 'http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/BuscaEmpresaListada.aspx'
        params = {
            'Letra': f'{letter}',
            'idioma': 'en-us',
            }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            }
        resp = requests.get(url, params=params, headers=headers)
        # ------------------------------------------------------------[Parsing]
        tree = html.fromstring(resp.content)
        companies_tr = tree.xpath('//*[@id="ctl00_contentPlaceHolderConteudo_BuscaNomeEmpresa1_grdEmpresa_ctl01"]/tbody/tr')
        for tr in companies_tr:
            name_td, trading_floor_name_td, segment_td = tr.xpath('./td')
            name = name_td.xpath('./a/text()')[0]
            trading_floor_name = trading_floor_name_td.xpath('./a/text()')[0]
            segment = segment_td.xpath('./text()')[0]
            # ---------------------------------------------------[Sanitization]
            segment = str(segment).replace('\u00a0', '')
            resume_url = name_td.xpath('./a')[0].get('href')
            cvm_code = re.sub(r'\D', '', resume_url)
            # ----------------------------------------------------[Serializing]
            ret.append({
                'cvm_code': cvm_code,
                'name': name,
                'trading_floor_name': trading_floor_name,
                'segment': segment,
                'company_data': self.get_company_data(cvm_code),
                })
            break
        return ret


if __name__ == '__main__':
    companies_data = BovespaCompanies().get_all_data()
    print(json.dumps(companies_data, indent=2))
    #db = Database()
    #investments_db = db.get_database('investments')
    #investments_db.companies.insert_many(companies_data)
