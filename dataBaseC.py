SCHEMA_FILE = 'schema.txt'


class DbException(Exception):
    Message = ''

    def __init__(self, message):
        self.Message = message


class Response:
    IsSuccess = True
    ErrorMessage = ''
    Result = []

    def __init__(self):
        self.IsSuccess = True
        self.ErrorMessage = ''
        self.Result = []


class Field:
    FieldName = ''
    Type = ''
    IsUnique = False

    def __init__(self):
        self.FieldName = ''
        self.Type = ''
        self.IsUnique = False

    def GetVal(self, value):
        if self.Type.upper() == 'INTEGER' or self.Type.upper() == 'TIMESTAMP':
            try:
                return int(value)
            except:
                raise DbException('Invalid value')
        elif self.Type.upper() == 'BOOLEAN':
            if value.upper() == 'TRUE':
                return True
            elif value.upper() == 'FALSE':
                return False
            else:
                raise DbException('Invalid value')
        elif self.Type.upper().startswith('CHAR'):
            return value

    def ConvertVal(self, value):
        if self.Type.upper() == 'INTEGER' or self.Type.upper() == 'TIMESTAMP':
            try:
                return int(value)
            except:
                raise DbException('Invalid value')
        elif self.Type.upper() == 'BOOLEAN':
            if value.upper() == 'TRUE':
                return True
            elif value.upper() == 'FALSE':
                return False
            else:
                raise DbException('Invalid value')
        elif self.Type.upper().startswith('CHAR'):
            if value[0] != '"' or value[-1] != '"':
                raise DbException('Invalid value')
            if len(value) < 2 or len(value) - 2 > int(self.Type[5:len(self.Type) - 1]):
                raise DbException('Invalid value')
            return value[1:len(value) - 1]


class Table:
    Fields = []
    Rows = []
    TableName = ''
    MaxId = 1

    def __init__(self):
        self.Fields = []
        self.Rows = []
        self.TableName = ''
        self.MaxId = 1

    def GetFieldId(self, fieldName):
        for i in range(len(self.Fields)):
            if self.Fields[i].FieldName == fieldName:
                return i
        raise DbException('Invalid field name')

    def Load(self):
        fName = self.TableName + '.txt'
        with open(fName, 'r') as fd:
            cols = fd.readline().strip()
            while True:
                rowStr = fd.readline().strip()
                if rowStr == '' or rowStr == '\n':
                    break
                r = []
                rowList = rowStr.split(' ')
                for i in range(len(self.Fields)):
                    r.append(self.Fields[i].GetVal(rowList[i]))
                self.Rows.append(r)
        if len(self.Rows) > 0:
            self.MaxId = self.Rows[-1][0] + 1


class Database:
    Tables = []

    def __init__(self):
        self.Tables = []

    def Error(self, errMessage):
        res = Response()
        res.ErrorMessage = errMessage
        res.IsSuccess = False
        return res

    def Success(self, result):
        res = Response()
        res.IsSuccess = True
        res.Result = result
        return res

    def Request(self, query):
        try:
            if query[-1] != ';':
                return self.Error('Invalid query')
            query = query[:len(query) - 1]
            self.Tables = []
            self.LoadTables()
            queryList = query.split(' ')
            return self.RunQuery(queryList)
        except DbException as err:
            return self.Error(err.Message)
        except Exception as err:
            return self.Error('Unknown error!')

    def RunQuery(self, queryList):
        if queryList[0].upper() == 'SELECT':
            return self.Select(queryList[1:])
        if queryList[0].upper() == 'UPDATE':
            return self.Update(queryList[1:])
        if queryList[0].upper() == 'INSERT':
            return self.Insert(queryList[1:])
        if queryList[0].upper() == 'DELETE':
            return self.Delete(queryList[1:])
        raise DbException('Invalid query')

    def Select(self, queryList):
        if queryList[0].upper() != 'FROM':
            raise DbException('Invalid Query')
        for table in self.Tables:
            if table.TableName == queryList[1]:
                table.Load()
                if len(queryList) < 3:
                    return self.Success(table.Rows)
                if queryList[2].upper() != 'WHERE':
                    raise DbException('Invalid query')
                isOk = self.ApplyConditions(table, queryList[3:])
                res = []
                for i in range(len(table.Rows)):
                    if isOk[i]:
                        res.append(table.Rows[i])
                return self.Success(res)
        raise DbException('Table not found')

    def Update(self, queryList):
        if queryList[1].upper() != 'WHERE' or queryList[-2].upper() != 'VALUES' or not (
                queryList[-1].startswith('(') and queryList[-1].endswith(')')):
            raise DbException('Invalid query')
        for table in self.Tables:
            if table.TableName == queryList[0]:
                table.Load()
                isOk = []
                isOk = self.ApplyConditions(table, queryList[2:len(queryList) - 2])
                if sum(isOk) > 1:
                    raise DbException('Repeated value in unique field')
                r = [0]
                values = queryList[-1][1:len(queryList[-1]) - 1].split(',')
                for j in range(len(values)):
                    r.append(table.Fields[j + 1].ConvertVal(values[j]))
                if len(r) != len(table.Fields):
                    raise DbException('Not enough values')
                if sum(isOk) == 0:
                    return self.Success(None)
                for i in range(len(table.Rows)):
                    if isOk[i]:
                        r[0] = table.Rows[i][0]
                        table.Rows[i] = r
                    else:
                        for j in range(len(table.Fields)):
                            if table.Fields[j].IsUnique and r[j] == table.Rows[i][j]:
                                raise DbException('Repeated value in unique field')
                self.WriteTable(table)
                return self.Success(None)
        raise DbException('Table not found')

    def Insert(self, queryList):
        for table in self.Tables:
            if table.TableName == queryList[1]:
                table.Load()
                values = queryList[-1][1:len(queryList[-1]) - 1].split(',')
                r = [table.MaxId]
                for j in range(len(values)):
                    r.append(table.Fields[j + 1].ConvertVal(values[j]))
                if len(r) != len(table.Fields):
                    raise DbException('Not enough values')
                for row in table.Rows:
                    for j in range(len(r)):
                        if table.Fields[j].IsUnique and r[j] == row[j]:
                            raise DbException('Repeated value in unique field')
                with open(queryList[1] + '.txt', 'a') as fd:
                    for val in r:
                        fd.write(str(val) + ' ')
                    fd.write('\n')
                return self.Success(None)
        raise DbException('Table not found')

    def Delete(self, queryList):
        for table in self.Tables:
            if table.TableName == queryList[1]:
                table.Load()
                isOk = self.ApplyConditions(table, queryList[3:])
                res = []
                for i in range(len(table.Rows)):
                    if not isOk[i]:
                        res.append(table.Rows[i])
                table.Rows = res
                self.WriteTable(table)
                return self.Success(None)
        raise DbException('Table not found')

    def WriteTable(self, table):
        fName = table.TableName + '.txt'
        with open(fName, 'w') as fd:
            for f in table.Fields:
                fd.write(f.FieldName + ' ')
            fd.write('\n')
            for r in table.Rows:
                for val in r:
                    fd.write(str(val) + ' ')
                fd.write('\n')

    def ApplyConditions(self, table, queryList):
        isOk = [True] * len(table.Rows)
        i = 0
        while i < len(queryList):
            if queryList[i].upper() == 'AND':
                pass
            elif queryList[i].upper() == 'OR':
                temp = self.ApplyConditions(table, queryList[i + 1:len(queryList)])
                for k in range(len(isOk)):
                    isOk[k] = isOk[k] or temp[k]
                break
            elif queryList[i] == '(':
                j = i
                while queryList[j] != ')' and j < len(queryList):
                    j += 1
                if j == len(queryList):
                    raise DbException('Parenthesis is not closed')
                temp = self.ApplyConditions(table, queryList[i + 1:j])
                i = j
                for k in range(len(isOk)):
                    isOk[k] = isOk[k] and temp[k]
            else:
                temp = self.ApplyCondition(table, queryList[i])
                for k in range(len(isOk)):
                    isOk[k] = isOk[k] and temp[k]
            i += 1
        return isOk

    def ApplyCondition(self, table, cond):
        if '==' in cond:
            condList = cond.split('==')
            res = []
            i = table.GetFieldId(condList[0])
            for r in table.Rows:
                res.append(r[i] == table.Fields[i].ConvertVal(condList[1]))
            return res
        elif '!=' in cond:
            condList = cond.split('!=')
            res = []
            i = table.GetFieldId(condList[0])
            for r in table.Rows:
                res.append(r[i] != table.Fields[i].ConvertVal(condList[1]))
            return res
        raise DbException('Invalid condition for where')

    def LoadTables(self):
        with open(SCHEMA_FILE, "r") as fd:
            while True:
                tbName = fd.readline().strip()
                if tbName == '' or tbName == '\n':
                    break
                table = Table()
                table.TableName = tbName
                while True:
                    fieldStr = fd.readline().strip()
                    if fieldStr == '' or fieldStr == '\n':
                        break
                    field = Field()
                    fieldList = fieldStr.split(' ')
                    field.FieldName = fieldList[0]
                    if len(fieldList) == 3:
                        field.IsUnique = True
                    field.Type = fieldList[-1]
                    table.Fields.append(field)
                self.Tables.append(table)
