# -*- coding: utf-8 -*-
# Упрощенный декодер protobuf для MEXC Spot V3
# На основе PushDataV3ApiWrapper.proto и PublicSpotKlineV3Api.proto
# Важно: в Protobuf тег (field_number + wire_type) кодируется как VARINT, а не один байт.
# Поле 308 (publicSpotKline) даёт тег 2466 → два байта 0xA2 0x13. Один байт 0xA2 ошибочно даёт field_num=20.


def _read_varint(data, pos):
    """Читает varint из data начиная с pos. Возвращает (value, new_pos)."""
    value = 0
    shift = 0
    while pos < len(data):
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if (byte & 0x80) == 0:
            break
        shift += 7
        if shift >= 64:
            break
    return value, pos


def decode_public_spot_kline_v3_api(data_bytes):
    """
    Упрощенное декодирование PublicSpotKlineV3Api из protobuf
    Возвращает dict с полями или None при ошибке
    """
    try:
        # Создаем простой класс для декодирования
        class SimpleKlineDecoder:
            def __init__(self):
                self.interval = ""
                self.windowStart = 0
                self.openingPrice = ""
                self.closingPrice = ""
                self.highestPrice = ""
                self.lowestPrice = ""
                self.volume = ""
                self.amount = ""
                self.windowEnd = 0
            
            def ParseFromString(self, data):
                # Упрощенное декодирование protobuf wire format
                pos = 0
                while pos < len(data):
                    if pos >= len(data):
                        break
                    # Читаем tag (field number + wire type)
                    tag = data[pos]
                    pos += 1
                    field_num = tag >> 3
                    wire_type = tag & 0x7
                    
                    if wire_type == 0:  # Varint
                        value = 0
                        shift = 0
                        while pos < len(data):
                            byte = data[pos]
                            pos += 1
                            value |= (byte & 0x7F) << shift
                            if (byte & 0x80) == 0:
                                break
                            shift += 7
                        if field_num == 2:  # windowStart
                            self.windowStart = value
                        elif field_num == 9:  # windowEnd
                            self.windowEnd = value
                    elif wire_type == 2:  # Length-delimited (string)
                        length = 0
                        shift = 0
                        while pos < len(data):
                            byte = data[pos]
                            pos += 1
                            length |= (byte & 0x7F) << shift
                            if (byte & 0x80) == 0:
                                break
                            shift += 7
                        if pos + length > len(data):
                            break
                        value = data[pos:pos+length].decode('utf-8', errors='ignore')
                        pos += length
                        if field_num == 1:  # interval
                            self.interval = value
                        elif field_num == 3:  # openingPrice
                            self.openingPrice = value
                        elif field_num == 4:  # closingPrice
                            self.closingPrice = value
                        elif field_num == 5:  # highestPrice
                            self.highestPrice = value
                        elif field_num == 6:  # lowestPrice
                            self.lowestPrice = value
                        elif field_num == 7:  # volume
                            self.volume = value
                        elif field_num == 8:  # amount
                            self.amount = value
        
        decoder = SimpleKlineDecoder()
        decoder.ParseFromString(data_bytes)
        
        return {
            'interval': decoder.interval,
            'windowStart': decoder.windowStart,
            'openingPrice': decoder.openingPrice,
            'closingPrice': decoder.closingPrice,
            'highestPrice': decoder.highestPrice,
            'lowestPrice': decoder.lowestPrice,
            'volume': decoder.volume,
            'amount': decoder.amount,
            'windowEnd': decoder.windowEnd
        }
    except Exception as e:
        return None

def decode_push_data_v3_api_wrapper(data_bytes):
    """
    Декодирует PushDataV3ApiWrapper из protobuf
    Возвращает dict с полями: channel, symbol, publicSpotKline (dict) или None при ошибке
    """
    try:
        pos = 0
        channel = ""
        symbol = ""
        symbol_id = ""
        create_time = 0
        send_time = 0
        kline_data = None
        
        # Для отладки при отсутствии kline
        debug_fields = []
        debug_count = 0  # Счетчик для ограничения логирования
        
        while pos < len(data_bytes):
            if pos >= len(data_bytes):
                break
            
            # Читаем tag как VARINT (field number + wire type). Поле 308 = два байта!
            tag, pos = _read_varint(data_bytes, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7
            
            # Логируем поле для отладки
            debug_fields.append((field_num, wire_type))
            
            debug_count += 1
            
            if wire_type == 0:  # Varint
                value = 0
                shift = 0
                while pos < len(data_bytes):
                    byte = data_bytes[pos]
                    pos += 1
                    value |= (byte & 0x7F) << shift
                    if (byte & 0x80) == 0:
                        break
                    shift += 7
                if field_num == 5:  # createTime
                    create_time = value
                elif field_num == 6:  # sendTime
                    send_time = value
            elif wire_type == 2:  # Length-delimited (string или embedded message)
                length = 0
                shift = 0
                while pos < len(data_bytes):
                    byte = data_bytes[pos]
                    pos += 1
                    length |= (byte & 0x7F) << shift
                    if (byte & 0x80) == 0:
                        break
                    shift += 7
                
                if pos + length > len(data_bytes):
                    break
                
                data_chunk = data_bytes[pos:pos+length]
                pos += length
                
                if field_num == 1:  # channel
                    try:
                        channel = data_chunk.decode('utf-8', errors='ignore')
                    except:
                        pass
                elif field_num == 3:  # symbol
                    try:
                        symbol = data_chunk.decode('utf-8', errors='ignore')
                    except:
                        pass
                elif field_num == 4:  # symbolId
                    try:
                        symbol_id = data_chunk.decode('utf-8', errors='ignore')
                    except:
                        pass
                elif field_num >= 301 and field_num <= 315:  # oneof body fields (301-315)
                    # Проверяем, это ли поле 308 (publicSpotKline)
                    if field_num == 308:  # publicSpotKline (oneof body, field 308)
                        kline_data = decode_public_spot_kline_v3_api(data_chunk)
        
        result = {
            'channel': channel,
            'symbol': symbol,
            'symbolId': symbol_id,
            'createTime': create_time,
            'sendTime': send_time,
            'publicSpotKline': kline_data
        }
        
        # Логируем для отладки, если нет kline данных, но есть channel
        if not kline_data and channel and 'kline' in channel.lower():
            # Выводим информацию о найденных полях для отладки
            print(f"🔍 PushDataV3ApiWrapper: найдены поля: {debug_fields}, но kline_data=None", flush=True)
            print(f"🔍 channel={channel}, symbol={symbol}, размер данных={len(data_bytes)} байт", flush=True)
            # Показываем все hex данные для анализа
            hex_all = ' '.join(f'{b:02x}' for b in data_bytes[:100])
            print(f"🔍 Первые 100 байт (hex): {hex_all}", flush=True)
        
        return result
    except Exception as e:
        # Логируем ошибку для отладки
        import traceback
        print(f"❌ Ошибка декодирования PushDataV3ApiWrapper: {e}", flush=True)
        print(f"❌ Traceback: {traceback.format_exc()}", flush=True)
        return None

def decode_public_spot_kline_v3_api(data_bytes):
    """
    Упрощенное декодирование PublicSpotKlineV3Api из protobuf
    Возвращает dict с полями или None при ошибке
    """
    try:
        # Используем google.protobuf для декодирования
        from google.protobuf import message
        
        # Создаем простой класс для декодирования
        class SimpleKlineDecoder:
            def __init__(self):
                self.interval = ""
                self.windowStart = 0
                self.openingPrice = ""
                self.closingPrice = ""
                self.highestPrice = ""
                self.lowestPrice = ""
                self.volume = ""
                self.amount = ""
                self.windowEnd = 0
            
            def ParseFromString(self, data):
                # Упрощенное декодирование protobuf wire format
                # Это базовая реализация, для полной поддержки нужен правильный protobuf модуль
                pos = 0
                while pos < len(data):
                    if pos >= len(data):
                        break
                    # Читаем tag (field number + wire type)
                    tag = data[pos]
                    pos += 1
                    field_num = tag >> 3
                    wire_type = tag & 0x7
                    
                    if wire_type == 0:  # Varint
                        value = 0
                        shift = 0
                        while pos < len(data):
                            byte = data[pos]
                            pos += 1
                            value |= (byte & 0x7F) << shift
                            if (byte & 0x80) == 0:
                                break
                            shift += 7
                        if field_num == 2:  # windowStart
                            self.windowStart = value
                        elif field_num == 9:  # windowEnd
                            self.windowEnd = value
                    elif wire_type == 2:  # Length-delimited (string)
                        length = 0
                        shift = 0
                        while pos < len(data):
                            byte = data[pos]
                            pos += 1
                            length |= (byte & 0x7F) << shift
                            if (byte & 0x80) == 0:
                                break
                            shift += 7
                        if pos + length > len(data):
                            break
                        value = data[pos:pos+length].decode('utf-8', errors='ignore')
                        pos += length
                        if field_num == 1:  # interval
                            self.interval = value
                        elif field_num == 3:  # openingPrice
                            self.openingPrice = value
                        elif field_num == 4:  # closingPrice
                            self.closingPrice = value
                        elif field_num == 5:  # highestPrice
                            self.highestPrice = value
                        elif field_num == 6:  # lowestPrice
                            self.lowestPrice = value
                        elif field_num == 7:  # volume
                            self.volume = value
                        elif field_num == 8:  # amount
                            self.amount = value
        
        decoder = SimpleKlineDecoder()
        decoder.ParseFromString(data_bytes)
        
        return {
            'interval': decoder.interval,
            'windowStart': decoder.windowStart,
            'openingPrice': decoder.openingPrice,
            'closingPrice': decoder.closingPrice,
            'highestPrice': decoder.highestPrice,
            'lowestPrice': decoder.lowestPrice,
            'volume': decoder.volume,
            'amount': decoder.amount,
            'windowEnd': decoder.windowEnd
        }
    except Exception as e:
        return None
