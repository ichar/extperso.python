# -*- coding: utf-8 -*-

import re
from sqlalchemy import create_engine
import pymssql

from config import (
     CONNECTION, IsDebug, IsDeepDebug,
     default_unicode, default_encoding, default_iso,
     print_to, print_exception
     )

from .utils import splitter, worder, getMaskedPAN

default_connection = CONNECTION['bankperso']

database_config = { \
    # ---------
    # BANKPERSO
    # ---------
    'orders' : { \
        'columns' : ('FileID', 'FName', 'FQty', 'BankName', 'FileType', 'StatusDate', 'FileStatus', 'RegisterDate', 'ReadyDate',),
        'view'    : '[BankDB].[dbo].[WEB_OrdersStatus_vw]',
        'headers' : { \
            'FileID'       : 'ID файла',
            'FName'        : 'ФАЙЛ',
            'FQty'         : 'Кол-во',
            'BankName'     : 'КЛИЕНТ',
            'FileType'     : 'Тип файла',
            'StatusDate'   : 'Дата статуса',
            'FileStatus'   : 'СТАТУС',
            'RegisterDate' : 'Дата регистрации',
            'ReadyDate'    : 'Ожидаемая дата готовности',
        },
        'clients' : 'ClientID',
        'export'  : ('FileID', 'FileTypeID', 'ClientID', 'FileStatusID', 'FName', 'FQty', 'BankName', 'FileType', 'StatusDate', 'FileStatus', 'RegisterDate', 'ReadyDate',),
    },
    'batches' : { \
        'columns' : ('TZ', 'TID', 'BatchType', 'BatchNo', 'ElementQty', 'Status', 'StatusDate',),
        'view'    : '[BankDB].[dbo].[WEB_OrdersBatchList_vw]',
        'headers' : { \
            'TZ'           : 'ТЗ',
            'TID'          : 'ID партии',
            'BatchType'    : 'Тип',
            'BatchNo'      : '№ партии',
            'ElementQty'   : 'Кол-во',
            'Status'       : 'Статус партии',
            'StatusDate'   : 'Дата статуса',
        },
        'export'  : ('TZ', 'TID', 'BatchType', 'BatchNo', 'ElementQty', 'Status', 'StatusDate', 'FileID', 'BatchTypeID',) #  'BatchStatusID', 'ERP_TZ', 'ClientID', 'FileTypeID', 'FileStatusID', 'FName', 'FQty', 'RegisterDate', 'BankName'
    },
    'clients' : { \
        'columns' : ('TID', 'CName'),
        'view'    : '[BankDB].[dbo].[DIC_Clients_tb]',
        'headers' : { \
            'TID'          : 'ID',
            'CName'        : 'Наименование',
        },
        'clients' : 'TID',
    },
    'types' : { \
        'columns' : ('TID', 'CName', 'ClientID',),
        'view'    : '[BankDB].[dbo].[DIC_FileType_tb]',
        'headers' : { \
            'TID'          : 'ID',
            'ClientID'     : 'ID клиента',
            'CName'        : 'Тип файла',
        },
        'clients' : 'ClientID',
    },
    'statuses' : { \
        'columns' : ('TID', 'CName',),
        'view'    : '[BankDB].[dbo].[DIC_FileStatus_tb]',
        'headers' : { \
            'TID'          : 'ID',
            'Status'       : 'Статус файла',
        },
    },
    'filestatuses' : { \
        'columns' : ('FileID', 'FileStatusID',),
        'view'    : '[BankDB].[dbo].[OrderFilesBody_tb]',
        'headers' : { \
            'Status'       : 'Статус файла',
        },
    },
    'filestatuslist' : { \
        'columns' : ('TID', 'StatusTypeID', 'CName',),
        'view'    : '[BankDB].[dbo].[DIC_FileStatus_tb]',
        'headers' : { \
            'TID'          : 'ID',
            'StatusTypeID' : 'Тип cтатуса',
            'CName'        : 'Наименование',
        },
    },
    'batchstatuslist' : { \
        'columns' : ('TID', 'CName',),
        'view'    : '[BankDB].[dbo].[DIC_BatchStatus_tb]',
        'headers' : { \
            'TID'          : 'ID',
            'CName'        : 'Наименование',
        },
    },
    'batchtypelist' : { \
        'columns' : ('TID', 'CName',),
        'view'    : '[BankDB].[dbo].[DIC_BatchType_tb]',
        'headers' : { \
            'TID'          : 'ID',
            'CName'        : 'Наименование',
        },
    },
    'params' : { \
        'columns' : ('TID', 'PName', 'PValue', 'PSortIndex', 'TName', 'TValue', 'FTVLinkID', 'TagParamID', 'FileTypeID', 'FileID', 'BatchID', 'PERS_TZ', 'BatchTypeID', 'ElementQty',),
        'exec'    : '[BankDB].[dbo].[WEB_GetBatchParamValues_sp]',
        'headers' : { \
            'TID'          : 'ID параметра',
            'PName'        : 'Название параметра',
            'PValue'       : 'Значение',
            'PSortIndex'   : 'Индекс сортировки',
            'TName'        : 'Параметр конфигурации',
            'TValue'       : 'Код значения',
            'FTVLinkID'    : 'ID значения тега',
            'TagParamID'   : 'ID параметра',
            'FileTypeID'   : 'ID типа файла',
            'FileID'       : 'ID файла',
            'BatchID'      : 'ID партии',
            'PERS_TZ'      : 'Номер ТЗ',
            'BatchTypeID'  : 'ID типа партии',
            'ElementQty'   : 'Количество элементов в партии',
        },
    },
    'image': { \
        'columns' : ('FileID', 'FBody',),
        'exec'    : '[BankDB].[dbo].[WEB_GetOrderFileBodyImage_sp]',
        'headers' : { \
            'FileID'       : 'ID файла',
            'FBody'        : 'Контент заказа',
        },
    },
    'body': { \
        'columns' : ('FileID', 'FileStatusID', 'IBody',),
        'exec'    : '[BankDB].[dbo].[WEB_GetOrderFileBody_sp]',
        'headers' : { \
            'FileID'       : 'ID файла',
            'FileStatusID' : 'ID статуса файла',
            'IBody'        : 'Контент заказа',
        },
    },
    'TZ' : { \
        'columns' : ('PName', 'PValue', 'PSortIndex', 'PType',), #, 'ElementQty'
        'exec'    : '[BankDB].[dbo].[WEB_GetBatchParamValues_sp]',
        'headers' : { \
            'PName'        : 'Название параметра',
            'PValue'       : 'Значение',
            'ElementQty'   : 'Количество элементов в партии',
            'PSortIndex'   : 'Индекс сортировки',
            'PType'        : 'Тип параметра',
        },
        'exclude' : ('CLIENTID', 'DeliveryType', 'PackageCode',),
        'rename'  : { \
            'PlasticType'  : ('', 25),
        },
    },
    # ---------------
    # Операции BankDB
    # ---------------
    'activate' : { \
        'params'  : '%(batch_id)s',
        'exec'    : '[BankDB].[dbo].[WEB_BatchActivate_sp]',
    },
    'changefilestatus' : { \
        'params'  : "null,null,0,%(file_id)s,%(check_file_status)s,%(new_file_status)s,null,null,null,1,0,0,0,%(keep_history)s",
        'exec'    : '[BankDB].[dbo].[WEB_ChangeOrderState_sp]',
    },
    'changebatchstatus' : { \
        'params'  : "null,null,0,%(file_id)s,null,null,%(batch_id)s,null,%(new_batch_status)s,0,1,0,0",
        'exec'    : '[BankDB].[dbo].[WEB_ChangeOrderState_sp]',
    },
    'deletefile' : { \
        'params'  : "null,null,0,%(file_id)s,null,0,null,null,0,1,1,1,1",
        'exec'    : '[BankDB].[dbo].[WEB_ChangeOrderState_sp]',
    },
    'createfile'  : { \
        'params'  : "null,null,0,%(file_id)s,1,1,null,null,0,1,1,1,0",
        'exec'    : '[BankDB].[dbo].[WEB_ChangeOrderState_sp]',
    },
    'dostowin' : { \
        'params'  : "0,'%s'",
        'exec'    : '[BankDB].[dbo].[WEB_DecodeCyrillic_sp]',
    },
    'wintodos' : { \
        'params'  : "1,'%s'",
        'exec'    : '[BankDB].[dbo].[WEB_DecodeCyrillic_sp]',
    },
}


class BankPersoEngine():
    
    def __init__(self, name=None, user=None, connection=None):
        self.name = name or 'default'
        self.connection = connection or default_connection
        self.engine = create_engine('mssql+pymssql://%(user)s:%(password)s@%(server)s' % self.connection)
        self.conn = self.engine.connect()
        self.engine_error = False
        self.user = user

        if IsDeepDebug:
            print('>>> open connection[%s]' % self.name)

    def getReferenceID(self, name, key, value, tid='TID'):
        id = None
        
        if isinstance(value, str):
            where = "%s='%s'" % (key, value)
        else:
            where = '%s=%s' % (key, value)
            
        cursor = self.runQuery(name, top=1, columns=(tid,), where=where, distinct=True)
        if cursor:
            id = cursor[0][0]
        
        return id

    def _get_params(self, config, **kw):
        return 'exec_params' in kw and (config['params'] % kw['exec_params']) or kw.get('params') or ''

    def runProcedure(self, name, args=None, no_cursor=False, **kw):
        """
            Executes database stored procedure.
            Could be returned cursor.

            Parameter `with_error` can check error message/severity from SQL Server (raiserror).
        """
        if self.engine_error:
            return

        config = kw.get('config') or database_config[name]

        if args:
            sql = 'EXEC %(sql)s %(args)s' % { \
                'sql'    : config['exec'],
                'args'   : config['args'],
            }
        else:
            sql = 'EXEC %(sql)s %(params)s' % { \
                'sql'    : config['exec'],
                'params' : config['params'] % kw,
            }

        if IsDeepDebug:
            print('>>> runProcedure: %s' % sql)

        with_error = kw.get('with_error') and True or False

        return self.run(sql, args=args, no_cursor=no_cursor, with_error=with_error)

    def runQuery(self, name, top=None, columns=None, where=None, order=None, distinct=False, as_dict=False, **kw):
        """
            Executes as database query so a stored procedure.
            Returns cursor.
        """
        if self.engine_error:
            return []

        config = kw.get('config') or database_config[name]

        query_columns = columns or config.get('columns')

        if 'clients' in config and self.user is not None:
            profile_clients = self.user.get_profile_clients(True)
            if profile_clients:
                clients = '%s in (%s)' % ( \
                    config['clients'],
                    ','.join([str(x) for x in profile_clients])
                )

                if where:
                    where = '%s and %s' % (where, clients)
                else:
                    where = clients

        if 'view' in config and config['view']:
            params = { \
                'distinct' : distinct and 'DISTINCT' or '',
                'top'      : (top and 'TOP %s' % str(top)) or '',
                'columns'  : ','.join(query_columns),
                'view'     : config['view'],
                'where'    : (where and 'WHERE %s' % where) or '',
                'order'    : (order and 'ORDER BY %s' % order) or '',
            }
            sql = 'SELECT %(distinct)s %(top)s %(columns)s FROM %(view)s %(where)s %(order)s' % params
        else:
            params = { \
                'sql'      : config['exec'],
                'params'   : self._get_params(config, **kw),
            }
            sql = 'EXEC %(sql)s %(params)s' % params

        if IsDeepDebug:
            print('>>> runQuery: %s' % sql)

        rows = []

        encode_columns = kw.get('encode_columns') or []
        worder_columns = kw.get('worder_columns') or []

        mapping = kw.get('mapping')

        cursor = self.execute(sql)

        if cursor is not None and not cursor.closed:
            if IsDeepDebug:
                print('--> in_transaction:%s' % cursor.connection.in_transaction())

            for n, line in enumerate(cursor):
                if as_dict and query_columns:
                    row = dict(zip(query_columns, line))
                else:
                    row = [x for x in line]

                line = None
                del line

                for column in encode_columns:
                    if column in row or isinstance(column, int):
                        row[column] = row[column] and row[column].encode(default_iso).decode(default_encoding) or ''
                for column in worder_columns:
                    row[column] = splitter(row[column], length=None, comma=':')
                if mapping:
                    row = dict([(key, row.get(name)) for key, name in mapping])
                rows.append(row)

            cursor.close()

        return rows

    def runCommand(self, sql, **kw):
        """
            Run sql-command with transaction.
            Could be returned cursor.
        """
        if self.engine_error:
            return

        if IsDeepDebug:
            print('>>> runCommand: %s' % sql)

        if kw.get('no_cursor') is None:
            no_cursor = True
        else:
            no_cursor = kw['no_cursor'] and True or False

        with_error = kw.get('with_error') and True or False

        return self.run(sql, no_cursor=no_cursor, with_error=with_error)

    def run(self, sql, args=None, no_cursor=False, with_error=False):
        if self.conn is None or self.conn.closed:
            if with_error:
                return [], ''
            else:
                return None

        rows = []
        error_msg = ''

        with self.conn.begin() as trans:
            try:
                if args:
                    cursor = self.conn.execute(sql, args)
                else:
                    cursor = self.conn.execute(sql)

                if IsDeepDebug:
                    print('--> in_transaction:%s' % cursor.connection.in_transaction())

                if not no_cursor:
                    rows = [row for row in cursor if cursor]

                trans.commit()

            except Exception as err:
                try:
                    trans.rollback()
                except:
                    pass

                if err is not None and hasattr(err, 'orig') and (
                        isinstance(err.orig, pymssql.OperationalError) or 
                        isinstance(err.orig, pymssql.IntegrityError) or
                        isinstance(err.orig, pymssql.ProgrammingError)
                    ):
                    msg = len(err.orig.args) > 1 and err.orig.args[1] or ''
                    error_msg = msg and msg.decode().split('\n')[0] or 'unexpected error'
                    
                    if 'DB-Lib' in error_msg:
                        error_msg = re.sub(r'(,\s)', r':', re.sub(r'(DB-Lib)', r':\1', error_msg))
                else:
                    error_msg = 'database error'

                self.engine_error = True

                print_to(None, 'NO SQL QUERY: %s ERROR: %s' % (sql, error_msg))
                print_exception()

        if with_error:
            return rows, error_msg

        return rows

    def execute(self, sql):
        try:
            return self.engine.execute(sql)
        except:
            print_to(None, 'NO SQL EXEC: %s' % sql)
            print_exception()

            self.engine_error = True

            return None

    def dispose(self):
        self.engine.dispose()

        if IsDeepDebug:
            print('>>> dispose')

    def close(self):
        self.conn.close()

        if IsDeepDebug:
            print('>>> close connection[%s]' % self.name)

        self.dispose()
