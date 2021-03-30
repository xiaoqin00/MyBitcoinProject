import bitcoin
import pandas as pd
import smtplib

from email.header import Header
from email.mime.text import MIMEText

balance_file_path = '/Users/e9c50/Documents/Projects/Bitcoin/address_balance.csv'
result_txt_file = 'hacked_result.txt'


# 生成一个随机的密钥
def demo_generate_private_key():
    # 生成一个用十六进制表示的长 256 位的私钥（str类型）
    private_key = bitcoin.random_key()
    # 解码为十进制的整形密钥
    decoded_private_key = bitcoin.decode_privkey(private_key, 'hex')
    if not 0 < decoded_private_key < bitcoin.N:
        return demo_generate_private_key()

    # 用 WIF 格式编码密钥
    wif_encoded_private_key = bitcoin.encode_privkey(decoded_private_key, 'wif')
    # 用 01 标识的压缩密钥
    compressed_private_key = private_key + '01'
    # 生成 WIF的压缩格式
    wif_compressed_private_key = bitcoin.encode_privkey(bitcoin.decode_privkey(compressed_private_key, 'hex'), 'wif')
    return private_key, decoded_private_key, wif_encoded_private_key, compressed_private_key, wif_compressed_private_key


# 私钥转公钥
def demo_private_to_public(decoded_private_key):
    # 计算公钥坐标 K = k * G
    public_key = bitcoin.fast_multiply(bitcoin.G, decoded_private_key)
    # 计算公钥
    hex_encoded_public_key = bitcoin.encode_pubkey(public_key, 'hex')
    # 计算压缩公钥
    # if public_key[1] % 2 == 0:  # 两种方式均可
    compressed_prefix = '02' if public_key[1] & 1 == 0 else '03'
    # 转十六也可用 bitcoin_core.encode(xxx, 16)
    hex_compressed_public_key = compressed_prefix + hex(public_key[0])[2:]
    return public_key, hex_encoded_public_key, compressed_prefix, hex_compressed_public_key


# 公钥转地址
def demo_public_to_address(public_key, hex_compressed_public_key):
    # 计算地址
    # 传入公钥坐标对象/十六进制公钥值，输出同样的地址
    # 传入压缩公钥值，输出与⬆️不同的地址
    address = bitcoin.pubkey_to_address(public_key)
    compressed_address = bitcoin.pubkey_to_address(hex_compressed_public_key)
    return address, compressed_address


# 获取余额账户信息
def get_all_balance():
    balance = pd.read_csv(balance_file_path)[['address', 'value_satoshi']]
    balance['balance'] = balance['value_satoshi'] * 0.00000001
    balance = balance.set_index('address')['balance'].to_dict()
    return balance


# 发送邮件通知
def send_smtp_email(message_content):
    try:
        message_content = message_content.replace('\n', '<br>')
        sender_user, sender_pass = '2250795018@qq.com', ''
        receivers = ['2250795018@qq.com']

        message = MIMEText(message_content, 'html', 'utf-8')
        message['Subject'] = Header('BTC FINDER NOTICE', 'utf-8')
        message['From'] = Header("E9C50", 'utf-8')
        message['To'] = Header("E9C50", 'utf-8')

        smtp_client = smtplib.SMTP('smtp.qq.com')
        smtp_client.login(sender_user, sender_pass)
        smtp_client.sendmail(sender_user, receivers, message.as_string())
        print('邮件发送成功')
    except smtplib.SMTPException as e:
        print('Error: 无法发送邮件')
        print(repr(e))


# 写入本地文件备份
def write_txt(message_content):
    with open(result_txt_file, 'a') as file:
        file.write(message_content)
        file.close()


def loop_hacker():
    while True:
        try:
            private_key, decoded_private_key, wif_encoded_private_key, compressed_private_key, wif_compressed_private_key = demo_generate_private_key()
            public_key, hex_encoded_public_key, compressed_prefix, hex_compressed_public_key = demo_private_to_public(
                decoded_private_key)
            address, compressed_address = demo_public_to_address(public_key, hex_compressed_public_key)
            address_balance = all_balance.get(address)
            compressed_address_balance = all_balance.get(compressed_address)
        except:
            continue

        if address_balance is None and compressed_address_balance is None:
            print(f'【empty address】{address}')
            continue

        if True or address_balance > 0 or compressed_address_balance > 0:
            address_info = '====================================================================================================\n'
            address_info += f'密钥（十六进制）：{private_key} （长 256 位）\n'
            address_info += f'密钥（十进制）：{decoded_private_key} （0 到 1.158*10**77 之间）\n'
            address_info += f'密钥（WIF）：{wif_encoded_private_key} （5 开头，长 51 字符）\n'
            address_info += f'压缩密钥（十六进制）：{compressed_private_key} （01 结尾，长 264 位）\n'
            address_info += f'压缩密钥（WIF）：{wif_compressed_private_key} （L/K 开头）\n'
            address_info += '\n'

            address_info += f'公钥（坐标）：{public_key}\n'
            address_info += f'公钥（坐标的十六进制）：{tuple(hex(i) for i in public_key)}\n'  # 转十六也可用 bitcoin_core.encode(xxx, 16)
            address_info += f'公钥（十六进制）：{hex_encoded_public_key} （04 x y）\n'
            address_info += f'压缩公钥（十六进制）{hex_compressed_public_key}（02 开头代表 y 是偶数，03 开头代表 y 是奇数）\n'
            address_info += '\n'

            address_info += f'地址（b58check）：{address} （1 开头）\n'
            address_info += f'压缩地址（b58check）：{compressed_address} （1 开头）\n'
            address_info += f'地址余额：{address_balance}\n'
            address_info += f'压缩地址余额：{compressed_address_balance}\n'
            address_info += '====================================================================================================\n'
            write_txt(address_info)
            send_smtp_email(address_info)


if __name__ == '__main__':
    all_balance = get_all_balance()
    loop_hacker()
