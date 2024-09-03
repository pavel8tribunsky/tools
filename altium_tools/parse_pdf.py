import fitz

# file = 'F://components//STMicroelectronics//STM32F4 Series//STM32F407VG Datasheet.pdf'
# file = 'D://components//STMicroelectronics//STM32F4 Series//STM32F407VG Datasheet.pdf'
file = '..//..//..//components//STMicroelectronics//STM32F4 Series//STM32F407VG Datasheet.pdf'
pinout_tmp = 'altium_tools//pinout.tmp'
altfnc_tmp = 'altium_tools//altfnc.tmp'

PINOUT_PAGE_START = 46
PINOUT_PAGE_STOP = 58
PINOUT_STRING_START = 2

ALTFNC_PAGE_START = 61
ALTFNC_PAGE_STOP = 69
ALTFNC_STRING_START = 2

def main(path, cmd='stm32'):
    if cmd == 'stm32':
        pinout = parse_stm32_pinout(path)
        af = parse_stm32_alternate_fn(path)
        print(pinout)
    else:
        pass


def parse_stm32_pinout(path):
    acc = []
    header = ['LQFP-64', 'WLCSP-90', 'LQFP-100', 'LQFP-144', 'UFBGA-176', 'LQFP-176',
              'Pin name', 'Pin type', 'Notes', 'Alternate functions', 'Additional functions']
    acc.append(header)
    with open(pinout_tmp, "w") as fw:
        with fitz.open(path) as doc:
            for num, page in enumerate(doc.pages()):            
                if PINOUT_PAGE_START <= num <= PINOUT_PAGE_STOP:
                    tabs = page.find_tables()  # detect the tables
                    for tab in tabs:
                        string = tab.extract()
                        for i, s in enumerate(string):
                            if i >= PINOUT_STRING_START:
                                c = []
                                for cell in s:
                                    t = cell.replace('\n', '')
                                    c.append(t)
                                    # cell.strip()
                                column = ",".join(c)
                                column += '\n'
                                fw.write(column)
                                acc.append(c)
    return acc

def parse_stm32_alternate_fn(path):
    # символы переноса
    wrap_symb = ('-', '_', '/')
    # ошибочное включение символа переноса в ячейках таблицы
    stm32f407_exclude = ('USART3_TX/', 'SPI3_MISO/')
    # случаи переноса без включения символа переноса
    stm32f407_wrap_wo_ws = (('ETH_MII_RX_CLK', 'ETH_RMII__REF_CLK'),
                            ('SPI3_NSS', 'I2S3_WS'),
                            ('ETH_MII_RX_DV', 'ETH_RMII_CRS_DV'),
                            ('JTDO/TRACES', 'WO'),
                            ('SPI3_SCK', 'I2S3_CK'),
                            ('I2C1_SMB', 'A'),
                            ('SPI3_MOSI', 'I2S3_SD'),
                            ('DCMI_VSYN', 'C'),
                            ('SPI2_NSS', 'I2S2_WS'),
                            ('SPI2_SCK', 'I2S2_CK'),
                            ('ETH_MII_TX_EN', 'ETH_RMII_TX_EN'),
                            ('SPI2_NSS', 'I2S2_WS'),
                            ('ETH _MII_TXD0', 'ETH _RMII_TXD0'),
                            ('SPI2_SCK', 'I2S2_CK'),
                            ('ETH_MII_TXD1', 'ETH _RMII_TXD1'),
                            ('SPI2_MOSI', 'I2S2_SD'),
                            ('SPI2_MOSI', 'I2S2_SD'),
                            ('ETH_MII_RXD0', 'ETH_MII_RXD0'),
                            ('ETH _MII_RXD1', 'ETH _RMII_RXD1'),
                            ('SPI3_MOSI', 'I2S3_SD'),
                            ('TRACECL', 'K'))
    num_skip_before = 46
    num_skip_after = 0
    with open(altfnc_tmp, "w") as fw:
        with fitz.open(path) as doc:
            text = []
            for num, page in enumerate(doc):
                # if ALTFNC_PAGE_START <= num <= ALTFNC_PAGE_STOP:
                if ALTFNC_PAGE_START <= num <= ALTFNC_PAGE_START+2:
                    string = page.get_text()
                    # string = string.replace('\n', ',')
                    # string = string.split(",")
                    string = string.replace(' ', '')
                    string = string.split("\n")
                    text.append(string)                    

    # remove unnecessary data
    strings = []
    for page in text:
        l = len(page)
        for i, cell in enumerate(page):
            if num_skip_before < i < (l - 1 - num_skip_after):
                strings.append(cell)
        num_skip_before = 5
        num_skip_after = 42

    # remove stm32f407_exclude
    del text
    text = []
    for cell in strings:
        symb_exist = False
        for symb in stm32f407_exclude:
            if cell == symb:
                symb_exist = True
            else:
                pass
        if symb_exist:
            text.append(cell.replace('/', ''))
        else:
            text.append(cell)

    # wrap repair
    del strings
    strings = []
    wrap_after = False
    for i, cell in enumerate(text):
        wrap_flag = 'normal'
        lc = len(cell)
        ic = lc -1
        ls = len(strings)
        if lc == 1:
            if cell != '-':
                strings[ls-1] += cell
            else:
                strings.append(cell)
        else:
            if wrap_after == True:
                strings[ls-1] += cell
                wrap_after = False
            else:
                if cell[0] == '-' or \
                cell[0] == '_' or \
                cell[0] == '/':
                    strings[ls-1] += cell
                elif cell[ic] == '-' or \
                    cell[ic] == '_' or \
                    cell[ic] == '/':
                        strings.append(cell)
                        wrap_after = True
                else:
                    strings.append(cell)

    # pin wraped by pattern
    del text
    text = []
    ll = len(strings)
    i = 0
    while i < ll:
        wrap_status = 'no wrap'
        if i < ll - 1:
            for pat in stm32f407_wrap_wo_ws:
                if strings[i] == pat[0] and strings[i+1] == pat[1]:
                    text.append("".join(pat))                
                    wrap_status = 'wrap'
                    i += 1
                else:
                    pass
        if wrap_status == 'no wrap':
            text.append(strings[i])
        i += 1

    # split by "EVENTOUT"
    i = 0
    result = [[] for x in range(128)]
    for cell in text:
        result[i].append(cell)
        if cell == 'EVENTOUT':
            i += 1
    return result[:i]
    

if __name__ == '__main__':
    main(file)