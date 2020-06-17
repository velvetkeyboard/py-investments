# -*- coding: utf-8 -*-
import os
import re
import json
import string
import requests
import utils
from db import Database
from lxml import html
from lxml import etree
from tqdm import tqdm


class RealEstateInvestmentFunds(object):

    def get_all_data(self):
        raise NotImplemented


class BovespaREIF(RealEstateInvestmentFunds):

    def get_all_data(self):
        return self.get_details('a')

    def get_details(self, code):
        url = 'https://www.fundsexplorer.com.br/funds'
        params = {
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            }
        resp = requests.get(url, params=params, headers=headers)
        tree = html.fromstring(resp.text)

        funds_div = tree.xpath('//*[@id="fiis-list-container"]/div')
        ret = []
        for div in tqdm(funds_div, ascii=True, desc='Downloading REIFs'):
            fund = {}
            # -------------------------------------------[Collecting Basic Info]
            tick = div.xpath('./div/a/span')[0].text
            company_name = div.xpath('./div/a/div/span')[0].text
            link = div.xpath('./div/a')[0].get('href')
            fund['tick'] = tick
            fund['company_name'] = company_name
            # -------------------------------------------[Scrapping for details]
            url = f'https://www.fundsexplorer.com.br{link}'
            resp = requests.get(url)
            detail_tree = html.fromstring(resp.text)
            resume_div = detail_tree.xpath('//*[@id="main-indicators-carousel"]/div')
            for div2 in resume_div:
                column_name_span = div2.xpath("./span[contains(@class, 'indicator-title')]")[0]
                column_value_span = div2.xpath("./span[contains(@class, 'indicator-value')]")[0]
                column_name = utils.utf8_to_ascii(column_name_span.text)
                column_value = utils.utf8_to_ascii(column_value_span.text)
                column_name = column_name.replace(' ', '_').replace('.', '').lower()
                column_value = column_value.strip()
                fund[column_name] = column_value
            basic_info_li = detail_tree.xpath('//*[@id="basic-infos"]/div/div/div[2]/div/div[2]/ul/li')
            for li in basic_info_li:
                column_name, column_value = li.xpath('./div/span/text()')
                column_name = utils.sanitize(column_name)
                column_value = utils.sanitize_value(column_value)
                fund[column_name] = column_value
            ret.append(fund)
        return ret


def sync(mode):
    data = BovespaREIF().get_all_data()
    if mode == 'f':
        with open('backups/fii.json', 'w') as f:
            json.dump(data, f, indent=2)
    elif mode == 'd':
        db = Database()
        investments_db = db.get_database('investments')
        investments_db.real_estate_investment_funds.insert_many(data)


if __name__ == '__main__':
    # reif_data = {'foo': 'bar'}
    sync('f')
