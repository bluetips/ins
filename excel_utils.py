# -*- coding: utf-8 -*-
"""
@Time : 2020/6/16 14:53
@Author : keith wx:bluetips
@File : excel_utils.py
@Software: PyCharm 
@desc: 
"""

import xlwt

# 创建一个workbook 设置编码
workbook = xlwt.Workbook(encoding='utf-8')
# 创建一个worksheet
worksheet = workbook.add_sheet('My Worksheet')

# 写入excel
# 参数对应 行, 列, 值
worksheet.write(1, 0, label='this is test')

# 保存
workbook.save('Excel_test.xls')
