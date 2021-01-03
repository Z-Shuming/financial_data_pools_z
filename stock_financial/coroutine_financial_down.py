"""
协程获取财务利润表信息

使用示例（获取2020年第三季度利润）：
report_date = time_last_day_of_month(year=2020, month=9)

fina_run = FinacialRun(
    data_queue='fina_data_queue',
    page_queue='fina_page_queue'
)
fina_run.run(report_date = report_date)
"""

from data_urls import *
from comm_funcs import *
import json
import time
import pandas as pd
import asyncio


async def parse(url, engine):
    data = await async_crawl(url)
    parse_data_list = json.loads(data)
    data_all = parse_data_list['result']['data']
    columns = column()

    insert_values = []
    for row in data_all:
        insert_values.append(
            tuple(map(lambda x: row[x.upper()], columns)))

    df = pd.DataFrame(insert_values, columns=columns)

    df.set_index('report_date', inplace=True)
    df.fillna(0, inplace=True)

    df.to_sql(
        name='s_financial_profits',
        con=engine,
        if_exists='append')

def column():
    return [
        'security_code',
        'security_name_abbr',
        'notice_date',
        'report_date',
        'parent_netprofit',
        'total_operate_income',
        'operate_cost',
        'operate_expense',
        'operate_expense_ratio',
        'sale_expense',
        'manage_expense',
        'finance_expense',
        'total_operate_cost',
        'operate_profit',
        'income_tax',
        'operate_tax_add',
        'total_profit',
        'operate_profit_ratio',
        'deduct_parent_netprofit',
        'dpn_ratio'
    ]

def main():
    engine = get_db_engine_for_pandas()
    report_date = time_last_day_of_month(year=2010, month=6)
    total_page = int(get_page_num(get_financial_url(report_date=report_date))['result']['pages'])
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(parse(
            get_financial_url(report_date=report_date, page=p), engine)) for p in range(1, total_page+1) ]
    loop.run_until_complete(asyncio.wait(tasks))

class Coroutine(object):
    pass
if __name__ == '__main__':
    begin = time.time()
    main()
    end = time.time()
    print(end - begin)
