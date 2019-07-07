# -*- coding:utf-8 -*-

import re


def parseSQL(sql):
    """将sql使用正则表达式分割，然后保存到列表，输入参数为sql的字符串，返回数据为两个列表，
    分别代表字段名和值
    处理流程为：先将sql按照insert和values分开成列名和数据两大部分
    再对两部分分别处理，第一部分使用正则匹配，最终得到字段名（可能包括括号），
    然后处理成一个列表，包含字段名
    对第二部分直接处理，得到值的列表
    最终对列名和值处理，生成data文件
    写入data.txt文件内
    """

    string = sql.strip()
    """示例的sql语句
    INSERT INTO `member_stable`.`member_payment_password`
    (`id`, `member_id`, `password_salt`, `password`,
        `create_time`, `update_time`, `updated_by`,
        `created_by`, `is_deleted`, `opt_counter`)
    VALUES ('6552054397534273701', '6437245567739428916',
        'eU0Tyu05tFouxaBa', 'b5b977d14949902a077b35845f25e740',
        '2017-04-06 15:42:24', '2017-04-06 15:42:24',
        '6437245567739428916', '6437245567739428916', '0', '0');
    """
    sqlRe = re.compile(r"^insert\s+into\s*(.*)\s+values\s+(.*) *;?",
                       re.IGNORECASE)

    """
    columns和columns2分别保存key和value数据
    处理之后columns保存的数据为：
        `member_stable`.`member_payment_password`
            (`id`, `member_id`, `password_salt`, `password`,
            `create_time`, `update_time`, `updated_by`,
            `created_by`, `is_deleted`, `opt_counter`)
    处理之后columns2的值为：
        ('6552054397534273701', '6437245567739428916',
        'eU0Tyu05tFouxaBa', 'b5b977d14949902a077b35845f25e740',
        '2017-04-06 15:42:24', '2017-04-06 15:42:24',
        '6437245567739428916', '6437245567739428916', '0', '0');
    """
    columns = sqlRe.match(string).group(1)
    columns2 = sqlRe.match(string).group(2)

    # fileds保存字段，values保存字段的值
    fields = []
    values = []

    """
    用.把库和表名分开
    分开之后colums保存的值为：
    `member_payment_password`
        (`id`, `member_id`, `password_salt`, `password`,
        `create_time`, `update_time`, `updated_by`, `created_by`,
        `is_deleted`, `opt_counter`)
    """
    if len(columns.split('.')) > 1:
        colums = columns.split('.')[1]
    else:
        colums = columns.split('.')[0]
    print (colums)

    """
    取出表的名字
    field.group(2)的内容为字段名：
    (`id`, `member_id`, `password_salt`, `password`,
    `create_time`, `update_time`, `updated_by`, `created_by`,
    `is_deleted`, `opt_counter`)
    如果没有匹配到说明没有字段的名称，因为必须要字段名，所以无法继续，返回None
    """
    columnsRe = re.compile("[\"|`|']?([^\s\"`']+)[\"|`|']?\s*(.*)")
    field = columnsRe.match(colums)

    if field.group(2) == '':
        print (u"你的sql必须包含字段内容才能解析".encode("gbk"))
        return None, None
    else:
        """
        取出括号内容:
        进行匹配把括号去掉，然后使用,分割，取出每个字段
        """
        tempRe = re.compile("\(?\s*([^\(\)]+)\s*\)?")
        temp = tempRe.match(field.group(2)).group(1).split(",")
        """
        对每个字段循环，匹配取消引号，引号可能有三种情况，都进行匹配，然后把去掉引号之后的添加到fields
        """
        fieldRe = re.compile("[\"|`|']?\s*([^\s\"`']+)\s*[\"|`|']?")
        for i in temp:
            value = fieldRe.match(i.strip())
            fields.append(value.group(1))
    """
    对值进行匹配，去掉括号，然后使用,分割，处理方法同fields
    """
    valueRe = re.compile("\(?\s*([^\(\)]+)\s*\)?")
    defaults = valueRe.match(columns2).group(1).split(",")

    miniRe = re.compile("[\"|`|']?\s*([^\"`']+)\s*[\"|`|']?")
    for i in defaults:
        """
        对每个值进行 匹配，去掉引号，如果是null，则添加None，如果是空字符串，则添加""
        """
        value = miniRe.match(i.strip())
        if value is not None:
            if value.group(1).lower() == "null":
                values.append(None)
            else:
                values.append(value.group(1))
        else:
            values.append("")

    """比较值和字段长度，决定是否继续，返回字段和值
    """
    if len(fields) != len(values):
        print (u"你的字段跟值都不一样长".encode("gbk"))
        return None, None
    else:
        return (fields, values)

def generateData(fields, values):
    data = "data={\n"
    temp = []

    for index, i in enumerate(fields):
        if values[index] is None:
            print ("\"%s\": None" % (i))
            temp.append("\"%s\": None" % (i))
        elif values[index] == "":
            temp.append("\"%s\": \"\"" % (i))
        else:
            print(i)
            temp.append("\"%s\": \"%s\"" % (i, values[index]))
    print (temp)
    data += ",\n".join(temp)
    data += "\n}"
    return data


if __name__ == "__main__":

    files = []
    try:
        with open("sql.txt", "r") as f:
            lines = f.readlines()
    except IOError as e:
        print (u"sql.txt存在吗".encode("gbk"), e)
    else:
        for i in lines:
            try:
                fields, values = parseSQL(i)
            except AttributeError as  e:
                print (u"正则错误，可能是sql语句不支持".encode("gbk"), e)
            else:
                if fields is not None and values is not None:
                    files.append(generateData(fields, values))

        with open("data.txt", "a") as f:
            f.write("\n".join(files))

    print (u"成功".encode("gbk"))

    a = input(u"按任意键退出".encode("gbk"))
